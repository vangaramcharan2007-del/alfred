import os
import subprocess
import logging
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from .timeline import Timeline

logging.basicConfig(level=logging.INFO, format='[Alfred Shotcut] %(message)s')

class ShotcutAdapter:
    def __init__(self, executable_path="melt"):
        appdata_path = os.path.expanduser(r"~\AppData\Local\Programs\Shotcut\melt.exe")
        if os.path.exists(r"C:\Program Files\Shotcut\melt.exe"):
            self.executable_path = r"C:\Program Files\Shotcut\melt.exe"
        elif os.path.exists(appdata_path):
            self.executable_path = appdata_path
        else:
            self.executable_path = executable_path

    def _validate_inputs(self, timeline: Timeline, output_path: str) -> bool:
        logging.info("Validating rendering inputs...")
        if len(timeline.clips) < 2:
            logging.error(f"Validation Failed: Timeline contains only {len(timeline.clips)} clip(s). Cannot render.")
            return False
            
        for clip in timeline.clips:
            if not os.path.exists(clip.filepath):
                logging.error(f"Validation Failed: Media file missing: {clip.filepath}")
                return False
                
        for audio in timeline.audio_tracks:
            if not os.path.exists(audio.filepath):
                logging.error(f"Validation Failed: Audio file missing: {audio.filepath}")
                return False
                
        # Check if output dir is writable
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                logging.error(f"Validation Failed: Output directory not writable: {e}")
                return False
                
        logging.info("Input validation passed.")
        return True

    def _print_diagnostics(self, timeline: Timeline):
        photos = sum(1 for c in timeline.clips if c.media_type == "photo")
        videos = sum(1 for c in timeline.clips if c.media_type == "video")
        total_duration = sum(c.duration for c in timeline.clips)
        audio_dur = sum(a.duration if hasattr(a, 'duration') and a.duration else total_duration for a in timeline.audio_tracks)
        transitions = len(timeline.transitions) if hasattr(timeline, 'transitions') else max(0, len(timeline.clips)-1)
        
        print("\n" + "="*50)
        print("TIMELINE DIAGNOSTICS")
        print("="*50)
        print(f"Timeline clips: {len(timeline.clips)}")
        print(f"Timeline duration: {total_duration:.2f}s")
        print(f"Photo count: {photos}")
        print(f"Video count: {videos}")
        print(f"Audio track duration: {audio_dur:.2f}s")
        print(f"Transition count: {transitions}")
        print(f"Expected render duration: {total_duration:.2f}s")
        print("="*50 + "\n")

    def _create_mlt_xml(self, timeline: Timeline) -> str:
        mlt = ET.Element('mlt')
        profile = ET.SubElement(mlt, 'profile', description="HD 1080p", width=str(timeline.resolution[0]), 
                             height=str(timeline.resolution[1]), progressive="1", 
                             frame_rate_num=str(int(timeline.fps)), frame_rate_den="1")
                             
        # Producers mapping
        producers = []
        
        # Audio Track Producer
        audio_prod_id = "audio_track_0"
        if timeline.audio_tracks:
            audio = timeline.audio_tracks[0]
            prod = ET.SubElement(mlt, 'producer', id=audio_prod_id)
            ET.SubElement(prod, 'property', name="resource").text = audio.filepath
            producers.append(audio_prod_id)

        # Video Clip Producers
        video_producers = []
        for i, clip in enumerate(timeline.clips):
            prod_id = f"video_clip_{i}"
            video_producers.append(prod_id)
            producers.append(prod_id)
            prod = ET.SubElement(mlt, 'producer', id=prod_id)
            ET.SubElement(prod, 'property', name="resource").text = clip.filepath
            
            frames = int(clip.duration * timeline.fps)
            if clip.media_type == "video":
                try:
                    import cv2
                    cap = cv2.VideoCapture(clip.filepath)
                    if cap.isOpened():
                        actual_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        if actual_frames > 0:
                            frames = min(frames, actual_frames)
                    cap.release()
                except Exception:
                    pass
            
            # Update clip duration to reflect actual frames so audio truncation stays perfectly synced
            clip.duration = frames / timeline.fps
            
            ET.SubElement(prod, 'property', name="length").text = str(frames)
            
            # Add ken burns if applicable
            if clip.ken_burns:
                filt = ET.SubElement(prod, 'filter', id=f"affine_{i}")
                ET.SubElement(filt, 'property', name="mlt_service").text = "affine"
                
                # We need to map 0.0-1.0 to rect coords (x, y, w, h)
                w = timeline.resolution[0]
                h = timeline.resolution[1]
                
                # Start
                sw, sh = w * clip.ken_burns.start_scale, h * clip.ken_burns.start_scale
                sx = (w - sw) * clip.ken_burns.start_x
                sy = (h - sh) * clip.ken_burns.start_y
                
                # End
                ew, eh = w * clip.ken_burns.end_scale, h * clip.ken_burns.end_scale
                ex = (w - ew) * clip.ken_burns.end_x
                ey = (h - eh) * clip.ken_burns.end_y
                
                # Format: "x y w h 1.0"
                geom = f"0={sx} {sy} {sw} {sh} 1.0;{frames - 1}={ex} {ey} {ew} {eh} 1.0"
                ET.SubElement(filt, 'property', name="geometry").text = geom
                
            # Add cinematic color grading if applicable
            if clip.color_grading:
                # lift_gamma_gain filter
                cg_filt = ET.SubElement(prod, 'filter', id=f"lift_gamma_gain_{i}")
                ET.SubElement(cg_filt, 'property', name="mlt_service").text = "lift_gamma_gain"
                
                # Extract values with safe defaults
                lift_r = clip.color_grading.get("lift_r", "0.0")
                lift_g = clip.color_grading.get("lift_g", "0.0")
                lift_b = clip.color_grading.get("lift_b", "0.0")
                ET.SubElement(cg_filt, 'property', name="lift_r").text = lift_r
                ET.SubElement(cg_filt, 'property', name="lift_g").text = lift_g
                ET.SubElement(cg_filt, 'property', name="lift_b").text = lift_b
                
                gamma_r = clip.color_grading.get("gamma_r", "1.0")
                gamma_g = clip.color_grading.get("gamma_g", "1.0")
                gamma_b = clip.color_grading.get("gamma_b", "1.0")
                ET.SubElement(cg_filt, 'property', name="gamma_r").text = gamma_r
                ET.SubElement(cg_filt, 'property', name="gamma_g").text = gamma_g
                ET.SubElement(cg_filt, 'property', name="gamma_b").text = gamma_b
                
                gain_r = clip.color_grading.get("gain_r", "1.0")
                gain_g = clip.color_grading.get("gain_g", "1.0")
                gain_b = clip.color_grading.get("gain_b", "1.0")
                ET.SubElement(cg_filt, 'property', name="gain_r").text = gain_r
                ET.SubElement(cg_filt, 'property', name="gain_g").text = gain_g
                ET.SubElement(cg_filt, 'property', name="gain_b").text = gain_b
                
        # Playlists
        # 1. Video Playlist (Background)
        video_playlist_id = "playlist_video"
        v_playlist = ET.SubElement(mlt, 'playlist', id=video_playlist_id)
        for vp in video_producers:
            entry = ET.SubElement(v_playlist, 'entry', producer=vp)
            
        # 2. Audio Playlist
        audio_playlist_id = "playlist_audio"
        a_playlist = ET.SubElement(mlt, 'playlist', id=audio_playlist_id)
        if timeline.audio_tracks:
            total_frames = sum(int(clip.duration * timeline.fps) for clip in timeline.clips)
            ET.SubElement(a_playlist, 'entry', producer=audio_prod_id, out=str(total_frames - 1))
            
        # Tractor to multiplex video and audio simultaneously
        tractor = ET.SubElement(mlt, 'tractor', id="master_tractor")
        multitrack = ET.SubElement(tractor, 'multitrack')
        ET.SubElement(multitrack, 'track', producer=video_playlist_id)
        ET.SubElement(multitrack, 'track', producer=audio_playlist_id)
        
        # Add a mix transition to blend audio if needed, though MLT implicitly mixes if not specified
        trans = ET.SubElement(tractor, 'transition')
        ET.SubElement(trans, 'property', name="mlt_service").text = "mix"
        
        xml_str = minidom.parseString(ET.tostring(mlt)).toprettyxml(indent="  ")
        return xml_str

    def _validate_xml(self, xml_path: str) -> bool:
        logging.info("Performing strict XML validation...")
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logging.error(f"XML Validation Failed: Invalid XML syntax - {e}")
            return False
            
        # Gather all producers
        producer_ids = set()
        for prod in root.findall('.//producer'):
            if 'id' in prod.attrib:
                producer_ids.add(prod.attrib['id'])
                
        # Check playlists for missing producers
        playlist_ids = set()
        for pl in root.findall('.//playlist'):
            pid = pl.attrib.get('id')
            if pid:
                playlist_ids.add(pid)
            for entry in pl.findall('.//entry'):
                prod_ref = entry.attrib.get('producer')
                if prod_ref not in producer_ids:
                    logging.error(f"XML Validation Failed: Missing producer reference '{prod_ref}' in playlist.")
                    return False
                    
        # Check tractor references
        tractor_tracks = set()
        for tractor in root.findall('.//tractor'):
            for track in tractor.findall('.//track'):
                prod_ref = track.attrib.get('producer')
                if prod_ref not in playlist_ids and prod_ref not in producer_ids:
                    logging.error(f"XML Validation Failed: Tractor track references unknown producer/playlist '{prod_ref}'.")
                    return False
                tractor_tracks.add(prod_ref)
                
        # Orphan playlists check
        for pid in playlist_ids:
            if pid not in tractor_tracks:
                logging.error(f"XML Validation Failed: Orphan playlist detected '{pid}' (not mapped to tractor).")
                return False
                
        logging.info("XML Validation passed.")
        return True

    def _validate_render(self, output_path: str, expected_duration: float) -> bool:
        logging.info("Performing post-render CV2 verification...")
        try:
            import cv2
            cap = cv2.VideoCapture(output_path)
            if not cap.isOpened():
                logging.error("Render Verification Failed: Cannot open output video stream.")
                return False
                
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            if fps <= 0:
                logging.error("Render Verification Failed: Invalid FPS detected.")
                return False
                
            duration = frame_count / fps
            
            # Allow 1 second margin of error for duration
            if abs(duration - expected_duration) > 1.0:
                logging.error(f"Render Verification Failed: Duration mismatch. Expected ~{expected_duration}s, got {duration:.2f}s.")
                return False
                
            if frame_count < 2:
                logging.error(f"Render Verification Failed: Suspiciously low frame count ({frame_count}).")
                return False
                
            logging.info(f"Render Verification PASSED: {duration:.2f}s, {frame_count} frames verified via OpenCV.")
            return True
        except Exception as e:
            logging.error(f"Render Verification Failed: {e}")
            return False

    def render(self, timeline: Timeline, output_path: str, project_dir: str):
        self._print_diagnostics(timeline)
        
        if not self._validate_inputs(timeline, output_path):
            return False
            
        logging.info("Generating proper MLT XML project file (Tractor/Multitrack architecture)...")
        xml_content = self._create_mlt_xml(timeline)
        
        project_path = os.path.join(project_dir, "project.mlt")
        with open(project_path, 'w') as f:
            f.write(xml_content)
            
        if not self._validate_xml(project_path):
            return False
            
        logging.info(f"Project saved to {project_path}. Initiating melt render engine...")
        
        # Run headless rendering
        try:
            cmd = [self.executable_path, project_path, "-consumer", f"avformat:{output_path}", "vcodec=libx264", "preset=ultrafast"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                if "percentage:" in line:
                    logging.info(line.strip())
            process.wait()
            
            if process.returncode != 0:
                logging.error(f"Render failed with code {process.returncode}")
                return False
                
            expected_duration = sum(c.duration for c in timeline.clips)
            if not self._validate_render(output_path, expected_duration):
                return False
                
            logging.info(f"Render complete and verified: {output_path}")
            return True
        except FileNotFoundError:
            logging.error(f"Render engine '{self.executable_path}' not found! Ensure Shotcut/melt is installed.")
            return False
