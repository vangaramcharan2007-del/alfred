import os
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

class PhotoEngine:
    def __init__(self, exports_dir, tts_engine=None):
        self.exports_dir = exports_dir
        self.tts = tts_engine
        
    def speak(self, text):
        print(f"[Alfred] {text}")
        if self.tts:
            self.tts.speak(text)

    def enhance_photos(self, photos):
        self.speak("Phase 4: Initiating Cinematic Photo Enhancement.")
        enhanced_paths = []
        
        for i, p_path in enumerate(photos):
            try:
                img = Image.open(p_path).convert("RGB")
                
                # Apply LUT-style cinematic grading (Vibrance + Contrast + slight Sharpness)
                img = ImageEnhance.Color(img).enhance(1.25)
                img = ImageEnhance.Contrast(img).enhance(1.15)
                img = ImageEnhance.Sharpness(img).enhance(1.3)
                
                out_path = os.path.join(self.exports_dir, f"Cinematic_Tirupati_{i+1}.jpg")
                img.save(out_path, quality=95)
                enhanced_paths.append(out_path)
            except Exception as e:
                print(f"Error enhancing {p_path}: {e}")
                
        if enhanced_paths:
            self.generate_thumbnail(enhanced_paths[0])
            self.generate_collage(enhanced_paths[:4])
            
        self.speak(f"Successfully processed {len(enhanced_paths)} photos. Generated Cover Image and Collages.")
        return enhanced_paths

    def generate_thumbnail(self, base_image_path):
        try:
            thumb = Image.open(base_image_path)
            thumb = thumb.resize((1920, 1080))
            d = ImageDraw.Draw(thumb)
            try:
                font = ImageFont.truetype("arialbd.ttf", 120)
                sub_font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
                sub_font = ImageFont.load_default()
                
            d.text((150, 700), "TIRUPATI", fill=(255, 255, 255), font=font)
            d.text((150, 850), "Cinematic Travel Film", fill=(220, 220, 220), font=sub_font)
            
            thumb.save(os.path.join(self.exports_dir, "YouTube_Thumbnail.jpg"))
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")

    def generate_collage(self, photos):
        if len(photos) < 4: return
        try:
            # 2x2 grid
            imgs = [Image.open(p).resize((960, 540)) for p in photos]
            collage = Image.new('RGB', (1920, 1080))
            collage.paste(imgs[0], (0, 0))
            collage.paste(imgs[1], (960, 0))
            collage.paste(imgs[2], (0, 540))
            collage.paste(imgs[3], (960, 540))
            collage.save(os.path.join(self.exports_dir, "Instagram_Collage.jpg"))
        except Exception as e:
            print(f"Collage generation failed: {e}")
