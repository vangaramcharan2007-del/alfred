"""
assets/presentation/cinematic_bg.py
Generates 15 high-resolution (1920x1080) cinematic dark tech background images
with glowing circuits, dark vignettes, ambient lighting, and hardware textures.
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

BG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cinematic_bgs")
os.makedirs(BG_DIR, exist_ok=True)

def create_base_canvas(width=1920, height=1080, top_color=(8, 12, 22), bot_color=(3, 5, 10)):
    """Creates a smooth dark vertical gradient background."""
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

def add_glow_orb(img, cx, cy, radius, color, max_alpha=120):
    """Adds a smooth radial neon glow orb."""
    width, height = img.size
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    
    steps = 40
    for i in range(steps, 0, -1):
        r = int(radius * (i / steps))
        alpha = int(max_alpha * (1 - (i / steps))**2)
        c = (color[0], color[1], color[2], alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
        
    glow = glow.filter(ImageFilter.GaussianBlur(radius=radius // 8))
    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, glow)
    return img_rgba.convert("RGB")

def add_cyber_grid(img, spacing=80, line_color=(20, 35, 60), alpha=30):
    """Adds an isometric / perspective or subtle cyber grid."""
    width, height = img.size
    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid)
    
    col = (line_color[0], line_color[1], line_color[2], alpha)
    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=col, width=1)
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=col, width=1)
        
    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, grid)
    return img_rgba.convert("RGB")

def add_circuit_traces(img, seed=42, accent_color=(0, 240, 255), trace_count=18):
    """Draws cinematic glowing circuit PCB traces with connection nodes."""
    random.seed(seed)
    width, height = img.size
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for _ in range(trace_count):
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)
        points = [(x, y)]
        
        # 3-4 segments with 45 or 90 deg bends
        cur_x, cur_y = x, y
        for _ in range(random.randint(2, 5)):
            direction = random.choice(["H", "V", "D"])
            length = random.randint(60, 220)
            if direction == "H":
                cur_x += random.choice([-length, length])
            elif direction == "V":
                cur_y += random.choice([-length, length])
            else:
                cur_x += random.choice([-length, length])
                cur_y += random.choice([-length, length])
            cur_x = max(50, min(width - 50, cur_x))
            cur_y = max(50, min(height - 50, cur_y))
            points.append((cur_x, cur_y))
            
        trace_col = (accent_color[0], accent_color[1], accent_color[2], random.randint(25, 60))
        for p1, p2 in zip(points[:-1], points[1:]):
            draw.line([p1, p2], fill=trace_col, width=2)
            
        # Draw glowing node circle at ends
        node_col = (accent_color[0], accent_color[1], accent_color[2], random.randint(60, 140))
        for pt in [points[0], points[-1]]:
            draw.ellipse([pt[0]-4, pt[1]-4, pt[0]+4, pt[1]+4], fill=node_col)
            
    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")

def add_dark_vignette(img, intensity=0.75):
    """Applies a heavy cinematic dark vignette around borders."""
    width, height = img.size
    vignette = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    
    # Corner gradients
    max_dist = math.sqrt((width/2)**2 + (height/2)**2)
    for i in range(50):
        factor = i / 50
        r_w = width * (1 - factor * 0.5)
        r_h = height * (1 - factor * 0.5)
        alpha = int(255 * intensity * (factor**1.8))
        draw.ellipse([width/2 - r_w/2, height/2 - r_h/2, width/2 + r_w/2, height/2 + r_h/2], outline=(0, 0, 0, alpha), width=int(width//45))
        
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=60))
    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, vignette)
    return img_rgba.convert("RGB")

def generate_cinematic_backgrounds():
    """Generates 15 customized 1920x1080 background images."""
    paths = []
    
    # Slide configs with unique lighting moods
    configs = [
        {"id": 1, "top": (10, 16, 32), "bot": (3, 5, 10), "glow": (0, 240, 255), "pos": (960, 540), "rad": 600, "traces": 25}, # Hero Core
        {"id": 2, "top": (8, 14, 28), "bot": (2, 4, 8), "glow": (56, 189, 248), "pos": (400, 300), "rad": 500, "traces": 16}, # System Stack
        {"id": 3, "top": (12, 16, 30), "bot": (3, 5, 10), "glow": (99, 102, 241), "pos": (1500, 400), "rad": 550, "traces": 18}, # Architecture Evolution
        {"id": 4, "top": (10, 18, 30), "bot": (3, 6, 12), "glow": (0, 240, 255), "pos": (500, 540), "rad": 550, "traces": 22}, # Multicore SMP
        {"id": 5, "top": (14, 14, 28), "bot": (4, 4, 10), "glow": (245, 158, 11), "pos": (1400, 600), "rad": 500, "traces": 20}, # NUMA Interconnect
        {"id": 6, "top": (8, 18, 28), "bot": (2, 5, 9), "glow": (56, 189, 248), "pos": (960, 200), "rad": 500, "traces": 24}, # Hardware Interrupts
        {"id": 7, "top": (12, 14, 30), "bot": (3, 4, 10), "glow": (129, 140, 248), "pos": (300, 600), "rad": 500, "traces": 18}, # Interrupts & Syscalls
        {"id": 8, "top": (16, 10, 24), "bot": (4, 3, 8), "glow": (244, 63, 94), "pos": (1500, 500), "rad": 550, "traces": 22}, # Dual-Mode Security
        {"id": 9, "top": (16, 12, 20), "bot": (5, 3, 6), "glow": (244, 63, 94), "pos": (960, 700), "rad": 550, "traces": 18}, # Privileged Protection
        {"id": 10, "top": (10, 20, 26), "bot": (3, 6, 9), "glow": (52, 211, 153), "pos": (1400, 300), "rad": 500, "traces": 16}, # Hardware Timer
        {"id": 11, "top": (14, 14, 32), "bot": (4, 4, 10), "glow": (0, 240, 255), "pos": (400, 540), "rad": 550, "traces": 20}, # Storage Hierarchy
        {"id": 12, "top": (8, 20, 24), "bot": (2, 6, 8), "glow": (52, 211, 153), "pos": (1500, 600), "rad": 500, "traces": 22}, # DMA I/O
        {"id": 13, "top": (12, 16, 30), "bot": (3, 5, 10), "glow": (245, 158, 11), "pos": (960, 400), "rad": 500, "traces": 18}, # SMP vs NUMA Matrix
        {"id": 14, "top": (8, 14, 32), "bot": (2, 4, 12), "glow": (129, 140, 248), "pos": (400, 300), "rad": 550, "traces": 22}, # Clustered Cloud
        {"id": 15, "top": (12, 18, 36), "bot": (3, 5, 12), "glow": (0, 240, 255), "pos": (960, 540), "rad": 650, "traces": 28}, # Grand Synthesis & Q&A
    ]
    
    for cfg in configs:
        img = create_base_canvas(1920, 1080, cfg["top"], cfg["bot"])
        img = add_glow_orb(img, cfg["pos"][0], cfg["pos"][1], cfg["rad"], cfg["glow"], max_alpha=100)
        img = add_cyber_grid(img, spacing=90, line_color=(30, 50, 80), alpha=20)
        img = add_circuit_traces(img, seed=cfg["id"] * 17, accent_color=cfg["glow"], trace_count=cfg["traces"])
        img = add_dark_vignette(img, intensity=0.70)
        
        path = os.path.join(BG_DIR, f"slide_bg_{cfg['id']:02d}.jpg")
        img.save(path, "JPEG", quality=95)
        paths.append(path)
        
    print(f"Successfully generated {len(paths)} cinematic background images in {BG_DIR}")
    return paths

if __name__ == "__main__":
    generate_cinematic_backgrounds()
