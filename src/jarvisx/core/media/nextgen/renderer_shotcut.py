import os
import subprocess
import logging
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from pathlib import Path
from .timeline import Timeline

logging.basicConfig(level=logging.INFO, format='[Alfred Shotcut] %(message)s')

class ShotcutAdapter:
    def __init__(self, executable_path="melt"):
        self.executable_path = executable_path
        
    def _create_mlt_xml(self, timeline: Timeline) -> str:
        mlt = Element('mlt')
        profile = SubElement(mlt, 'profile', description="HD 1080p", width=str(timeline.resolution[0]), 
                             height=str(timeline.resolution[1]), progressive="1", 
                             frame_rate_num=str(int(timeline.fps)), frame_rate_den="1")
                             
        playlist = SubElement(mlt, 'playlist', id="main_bin")
        
        # Audio track
        if timeline.audio_tracks:
            audio = timeline.audio_tracks[0]
            prod = SubElement(mlt, 'producer', id="audio_track")
            SubElement(prod, 'property', name="resource").text = audio.filepath
            SubElement(playlist, 'entry', producer="audio_track")
        
        # Video clips
        for i, clip in enumerate(timeline.clips):
            prod_id = f"clip_{i}"
            prod = SubElement(mlt, 'producer', id=prod_id)
            SubElement(prod, 'property', name="resource").text = clip.filepath
            
            # Duration in frames
            frames = int(clip.duration * timeline.fps)
            SubElement(prod, 'property', name="length").text = str(frames)
            
            if clip.ken_burns:
                filt = SubElement(prod, 'filter', id=f"affine_{i}")
                SubElement(filt, 'property', name="mlt_service").text = "affine"
                SubElement(filt, 'property', name="transition.scale_x").text = f"{clip.ken_burns.start_scale}={clip.ken_burns.end_scale}"
                SubElement(filt, 'property', name="transition.scale_y").text = f"{clip.ken_burns.start_scale}={clip.ken_burns.end_scale}"
            
            # Add to playlist
            entry = SubElement(playlist, 'entry', producer=prod_id)
            
        xml_str = minidom.parseString(tostring(mlt)).toprettyxml(indent="  ")
        return xml_str

    def render(self, timeline: Timeline, output_path: str, project_dir: str):
        logging.info("Generating MLT XML project file...")
        xml_content = self._create_mlt_xml(timeline)
        
        project_path = os.path.join(project_dir, "project.mlt")
        with open(project_path, 'w') as f:
            f.write(xml_content)
            
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
                
            logging.info(f"Render complete: {output_path}")
            return True
        except FileNotFoundError:
            logging.error(f"Render engine '{self.executable_path}' not found! Ensure Shotcut/melt is installed.")
            return False
