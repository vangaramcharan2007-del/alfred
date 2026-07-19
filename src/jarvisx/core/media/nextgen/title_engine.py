import os
from PIL import Image, ImageDraw, ImageFont
import logging

class TitleEngine:
    """
    Generates dynamic Title Cards (Intro/Outro) for cinematic videos.
    """
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Attempt to load a default Windows font, fallback to default Pillow font
        self.font_path = "arial.ttf" 

    def generate_intro(self, title: str, subtitle: str, date_str: str) -> str:
        """
        Generates a 1920x1080 Intro card.
        """
        return self._create_card("intro.jpg", title, subtitle, date_str)

    def generate_outro(self, signature: str = "Directed by Jarvis X") -> str:
        """
        Generates a 1920x1080 Outro card.
        """
        return self._create_card("outro.jpg", "The End", "Thank You For Watching", signature)

    def _create_card(self, filename: str, main_text: str, sub_text: str, footer_text: str) -> str:
        out_path = os.path.join(self.output_dir, filename)
        
        img = Image.new('RGB', (1920, 1080), color=(10, 10, 10))
        draw = ImageDraw.Draw(img)
        
        try:
            font_main = ImageFont.truetype(self.font_path, 100)
            font_sub = ImageFont.truetype(self.font_path, 50)
            font_footer = ImageFont.truetype(self.font_path, 40)
        except Exception:
            logging.warning("Failed to load truetype font, falling back to default.")
            font_main = ImageFont.load_default()
            font_sub = font_main
            font_footer = font_main

        # Center text coordinates (approximated based on text length since textsize is deprecated in Pillow 10)
        # For a truly robust system we'd use textbbox, but this is a simple fallback
        try:
            main_w = draw.textlength(main_text, font=font_main)
            sub_w = draw.textlength(sub_text, font=font_sub)
            foot_w = draw.textlength(footer_text, font=font_footer)
        except AttributeError:
            main_w = len(main_text) * 50
            sub_w = len(sub_text) * 25
            foot_w = len(footer_text) * 20

        draw.text(((1920 - main_w) / 2, 400), main_text, font=font_main, fill=(255, 255, 255))
        draw.text(((1920 - sub_w) / 2, 550), sub_text, font=font_sub, fill=(200, 200, 200))
        draw.text(((1920 - foot_w) / 2, 900), footer_text, font=font_footer, fill=(150, 150, 150))
        
        img.save(out_path, quality=95)
        logging.info(f"Generated title card: {out_path}")
        return out_path
