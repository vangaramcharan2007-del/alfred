"""
assets/presentation/gamma_illustrations.py
Generates clean, isometric 3D vector-style hardware illustrations with
cinematic ambient glow orbs, frosted glass reflection effects, and tech accents.
Tailored for:
- Core Hardware & 3-Part System Bus (Address, Data, Control)
- Interrupts & DMA Direct Memory Access
- Storage Hierarchy Pyramid (Registers, Cache, RAM, SSD/HDD)
- Locality of Reference (Temporal & Spatial)
- SMP vs AMP & Multicore Processor Architectures
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ILLUST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gamma_assets")
os.makedirs(ILLUST_DIR, exist_ok=True)

def get_font(size=20, bold=False):
    try:
        font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
        font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", font_name)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def iso_point(x, y, z, cx=400, cy=350, scale=1.0):
    """Transforms 3D (x,y,z) to 2D isometric projection (cx, cy)."""
    rad = math.radians(30)
    cos30 = math.cos(rad)
    sin30 = math.sin(rad)
    
    screen_x = cx + (x - y) * cos30 * scale
    screen_y = cy + (x + y) * sin30 * scale - z * scale
    return (int(screen_x), int(screen_y))

def draw_iso_box(draw, x, y, z, dx, dy, dz, top_col, left_col, right_col, outline_col=None, cx=400, cy=350, scale=1.0):
    """Draws a 3D isometric box."""
    p_top = [
        iso_point(x, y, z+dz, cx, cy, scale),
        iso_point(x+dx, y, z+dz, cx, cy, scale),
        iso_point(x+dx, y+dy, z+dz, cx, cy, scale),
        iso_point(x, y+dy, z+dz, cx, cy, scale)
    ]
    p_left = [
        iso_point(x, y, z, cx, cy, scale),
        iso_point(x, y+dy, z, cx, cy, scale),
        iso_point(x, y+dy, z+dz, cx, cy, scale),
        iso_point(x, y, z+dz, cx, cy, scale)
    ]
    p_right = [
        iso_point(x+dx, y, z, cx, cy, scale),
        iso_point(x+dx, y+dy, z, cx, cy, scale),
        iso_point(x+dx, y+dy, z+dz, cx, cy, scale),
        iso_point(x+dx, y, z+dz, cx, cy, scale)
    ]
    
    draw.polygon(p_left, fill=left_col, outline=outline_col)
    draw.polygon(p_right, fill=right_col, outline=outline_col)
    draw.polygon(p_top, fill=top_col, outline=outline_col)

def add_ambient_glow(img, cx, cy, radius, color=(56, 189, 248, 80)):
    """Draws a soft ambient glow aura behind the object."""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(glow)
    draw_g.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(radius // 2))
    return Image.alpha_composite(glow, img)

def create_motherboard_illustration():
    """Slide 1: Isometric Dark Motherboard with Cyan Ambient Glow."""
    w, h = 800, 800
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, scale = 400, 380, 1.4
    
    # 1. Main PCB Board
    draw_iso_box(draw, -180, -180, 0, 360, 360, 15,
                 top_col=(35, 38, 48), left_col=(20, 22, 30), right_col=(28, 30, 40),
                 outline_col=(70, 80, 100), cx=cx, cy=cy, scale=scale)
    
    # 2. CPU Socket in center
    draw_iso_box(draw, -60, -60, 15, 120, 120, 10,
                 top_col=(50, 55, 68), left_col=(30, 34, 44), right_col=(40, 45, 56),
                 outline_col=(90, 100, 125), cx=cx, cy=cy, scale=scale)
    # CPU Core Die
    draw_iso_box(draw, -35, -35, 25, 70, 70, 8,
                 top_col=(25, 30, 42), left_col=(18, 22, 32), right_col=(22, 26, 36),
                 outline_col=(56, 189, 248), cx=cx, cy=cy, scale=scale)

    # 3. RAM Slots (4 tall narrow boxes on the right)
    for i in range(4):
        offset = 80 + i * 22
        draw_iso_box(draw, offset, -140, 15, 12, 260, 24,
                     top_col=(45, 50, 62), left_col=(25, 28, 38), right_col=(35, 40, 50),
                     outline_col=(80, 95, 120), cx=cx, cy=cy, scale=scale)
        draw_iso_box(draw, offset, -135, 39, 12, 250, 4,
                     top_col=(245, 158, 11), left_col=(180, 115, 10), right_col=(210, 135, 10),
                     cx=cx, cy=cy, scale=scale)

    # 4. PCIe Expansion Slots
    for i in range(3):
        offset = 40 + i * 45
        draw_iso_box(draw, -150, offset, 15, 200, 16, 12,
                     top_col=(40, 45, 58), left_col=(22, 26, 35), right_col=(32, 36, 48),
                     outline_col=(70, 85, 110), cx=cx, cy=cy, scale=scale)

    # 5. VRM Heat Sinks
    draw_iso_box(draw, -165, -165, 15, 75, 80, 50,
                 top_col=(60, 66, 80), left_col=(35, 40, 52), right_col=(48, 54, 68),
                 outline_col=(100, 115, 140), cx=cx, cy=cy, scale=scale)
    draw_iso_box(draw, -70, -165, 15, 130, 45, 40,
                 top_col=(55, 60, 75), left_col=(30, 35, 46), right_col=(42, 48, 62),
                 outline_col=(90, 105, 130), cx=cx, cy=cy, scale=scale)

    # 6. Chipset Heat Sink
    draw_iso_box(draw, 70, 70, 15, 80, 80, 20,
                 top_col=(55, 62, 78), left_col=(32, 38, 50), right_col=(44, 50, 64),
                 outline_col=(90, 105, 130), cx=cx, cy=cy, scale=scale)

    # 7. Traces
    for r in range(4):
        p1 = iso_point(-140 + r*20, -50, 16, cx, cy, scale)
        p2 = iso_point(-60, -50 + r*20, 16, cx, cy, scale)
        draw.line([p1, p2], fill=(56, 189, 248, 160), width=2)

    final_img = add_ambient_glow(img, cx, cy, 260, (56, 189, 248, 70))
    out_path = os.path.join(ILLUST_DIR, "iso_motherboard.png")
    final_img.save(out_path, "PNG")
    return out_path

def create_system_bus_3parts_illustration():
    """Slide 3: Isometric 3-Part System Bus (Address, Data, Control) connecting CPU, RAM, I/O."""
    w, h = 850, 800
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, scale = 425, 380, 1.15

    # 3 Bus Highways in parallel:
    # 1. Address Bus (Cyan)
    draw_iso_box(draw, -240, -40, 0, 480, 20, 8,
                 top_col=(30, 50, 75), left_col=(18, 30, 45), right_col=(24, 40, 60),
                 outline_col=(56, 189, 248), cx=cx, cy=cy, scale=scale)
    p_ab = iso_point(-230, -35, 12, cx, cy, scale)
    draw.text(p_ab, "ADDRESS BUS (Destination / Routing)", fill=(56, 189, 248), font=get_font(13, True))

    # 2. Data Bus (Indigo)
    draw_iso_box(draw, -240, 0, 0, 480, 20, 8,
                 top_col=(45, 40, 75), left_col=(26, 22, 45), right_col=(34, 30, 60),
                 outline_col=(129, 140, 248), cx=cx, cy=cy, scale=scale)
    p_db = iso_point(-230, 5, 12, cx, cy, scale)
    draw.text(p_db, "DATA BUS (Instructions & Operands)", fill=(129, 140, 248), font=get_font(13, True))

    # 3. Control Bus (Emerald)
    draw_iso_box(draw, -240, 40, 0, 480, 20, 8,
                 top_col=(30, 55, 45), left_col=(18, 35, 28), right_col=(24, 45, 36),
                 outline_col=(52, 211, 153), cx=cx, cy=cy, scale=scale)
    p_cb = iso_point(-230, 45, 12, cx, cy, scale)
    draw.text(p_cb, "CONTROL BUS (Read/Write & Timing)", fill=(52, 211, 153), font=get_font(13, True))

    # CPU Node (Top Left)
    draw_iso_box(draw, -180, -180, 0, 100, 100, 30,
                 top_col=(30, 45, 65), left_col=(18, 26, 38), right_col=(24, 34, 48),
                 outline_col=(56, 189, 248), cx=cx, cy=cy, scale=scale)
    p_cpu = iso_point(-165, -135, 35, cx, cy, scale)
    draw.text(p_cpu, "CPU (Fetch/Decode/Exec)", fill=(56, 189, 248), font=get_font(14, True))

    # Main Memory / RAM Node (Top Right)
    draw_iso_box(draw, 80, -180, 0, 120, 80, 35,
                 top_col=(30, 55, 45), left_col=(18, 35, 28), right_col=(24, 45, 36),
                 outline_col=(52, 211, 153), cx=cx, cy=cy, scale=scale)
    p_ram = iso_point(95, -145, 40, cx, cy, scale)
    draw.text(p_ram, "MAIN MEMORY (RAM)", fill=(52, 211, 153), font=get_font(14, True))

    # I/O Devices Node (Bottom Center)
    draw_iso_box(draw, -70, 140, 0, 140, 80, 25,
                 top_col=(45, 40, 60), left_col=(26, 22, 38), right_col=(34, 30, 48),
                 outline_col=(245, 158, 11), cx=cx, cy=cy, scale=scale)
    p_io = iso_point(-55, 175, 28, cx, cy, scale)
    draw.text(p_io, "I/O CONTROLLERS & DEVICES", fill=(245, 158, 11), font=get_font(13, True))

    # Connecting Links from Nodes to the 3-Bus Highway
    draw_iso_box(draw, -140, -80, 0, 20, 40, 6,
                 top_col=(56, 189, 248), left_col=(0, 180, 200), right_col=(0, 200, 220), cx=cx, cy=cy, scale=scale)
    draw_iso_box(draw, 130, -100, 0, 20, 60, 6,
                 top_col=(52, 211, 153), left_col=(30, 150, 100), right_col=(40, 180, 120), cx=cx, cy=cy, scale=scale)
    draw_iso_box(draw, -10, 60, 0, 20, 80, 6,
                 top_col=(245, 158, 11), left_col=(180, 115, 10), right_col=(210, 135, 10), cx=cx, cy=cy, scale=scale)

    final_img = add_ambient_glow(img, cx, cy, 260, (56, 189, 248, 65))
    out_path = os.path.join(ILLUST_DIR, "iso_system_bus.png")
    final_img.save(out_path, "PNG")
    return out_path

def create_storage_pyramid_illustration():
    """Slide 6 & 10: 4-Tier Isometric Storage Hierarchy Pyramid."""
    w, h = 800, 800
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, scale = 400, 360, 1.25

    tiers = [
        {"name": "REGISTERS (Fastest / Smallest)", "z": 240, "size": 130, "h": 40, "col": (56, 189, 248), "top": (35, 60, 90)},
        {"name": "CACHE (L1 / L2 / L3 SRAM)", "z": 160, "size": 200, "h": 45, "col": (129, 140, 248), "top": (35, 45, 80)},
        {"name": "MAIN MEMORY (DRAM / Volatile)", "z": 80, "size": 270, "h": 50, "col": (52, 211, 153), "top": (25, 55, 45)},
        {"name": "SECONDARY (SSD / NVMe / HDD)", "z": 0, "size": 340, "h": 55, "col": (245, 158, 11), "top": (50, 42, 30)}
    ]

    for tier in tiers:
        sz = tier["size"]
        z = tier["z"]
        dz = tier["h"]
        half = sz / 2

        draw_iso_box(draw, -half, -half, z, sz, sz, dz,
                     top_col=tier["top"], left_col=(18, 22, 32), right_col=(25, 30, 42),
                     outline_col=tier["col"], cx=cx, cy=cy, scale=scale)

        p_label = iso_point(-half + 10, half - 10, z + dz/2, cx, cy, scale)
        font = get_font(13, bold=True)
        draw.text(p_label, tier["name"], fill=(248, 250, 252), font=font)

    final_img = add_ambient_glow(img, cx, cy, 250, (56, 189, 248, 65))
    out_path = os.path.join(ILLUST_DIR, "iso_storage_pyramid.png")
    final_img.save(out_path, "PNG")
    return out_path

def create_single_vs_multi_illustration():
    """Slide 11: Single-Processor vs Multiprocessor architecture comparison tree card."""
    w, h = 800, 600
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_head = get_font(20, True)
    font_sub = get_font(14, False)
    font_box = get_font(16, True)

    # Left Box: Single-Processor
    draw.rounded_rectangle([30, 20, 370, 70], radius=8, fill=(240, 244, 248), outline=(15, 23, 42), width=2)
    draw.text((80, 32), "Single-Processor", fill=(15, 23, 42), font=font_head)

    draw.rounded_rectangle([150, 110, 250, 170], radius=8, fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((175, 128), "CPU", fill=(15, 23, 42), font=font_box)

    draw.line([(200, 170), (200, 230)], fill=(15, 23, 42), width=3)
    draw.line([(80, 230), (320, 230)], fill=(15, 23, 42), width=3)

    draw.rounded_rectangle([60, 250, 340, 320], radius=8, fill=(245, 247, 250), outline=(15, 23, 42), width=2)
    draw.text((90, 270), "Special-purpose\ncontrollers", fill=(15, 23, 42), font=get_font(15, True))

    draw.line([(200, 320), (200, 370)], fill=(15, 23, 42), width=3)
    draw.rounded_rectangle([130, 370, 270, 430], radius=8, fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((160, 388), "Memory", fill=(15, 23, 42), font=font_box)

    draw.text((60, 480), "• 1 CPU: All instructions pass through it\n• Simpler design, limited throughput", fill=(71, 85, 105), font=font_sub)

    # Dividing Line
    draw.line([(400, 20), (400, 580)], fill=(203, 213, 225), width=2)

    # Right Box: Multiprocessor
    draw.rounded_rectangle([430, 20, 770, 70], radius=8, fill=(240, 244, 248), outline=(15, 23, 42), width=2)
    draw.text((500, 32), "Multiprocessor", fill=(15, 23, 42), font=font_head)

    draw.rounded_rectangle([450, 110, 530, 170], radius=8, fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((468, 128), "CPU 1", fill=(15, 23, 42), font=font_box)

    draw.text((570, 130), "• • •", fill=(15, 23, 42), font=get_font(20, True))

    draw.rounded_rectangle([670, 110, 750, 170], radius=8, fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((688, 128), "CPU N", fill=(15, 23, 42), font=font_box)

    draw.line([(490, 170), (490, 240)], fill=(15, 23, 42), width=3)
    draw.line([(710, 170), (710, 240)], fill=(15, 23, 42), width=3)
    draw.line([(450, 240), (750, 240)], fill=(15, 23, 42), width=5)
    draw.text((540, 215), "Shared bus", fill=(15, 23, 42), font=get_font(14, True))

    draw.line([(600, 240), (600, 330)], fill=(15, 23, 42), width=3)
    draw.rounded_rectangle([520, 330, 680, 400], radius=8, fill=(255, 255, 255), outline=(15, 23, 42), width=2)
    draw.text((560, 352), "Memory", fill=(15, 23, 42), font=font_box)

    draw.text((450, 460), "• Multiple CPUs: Run concurrent workloads\n• Shared memory & interconnect\n• Increased throughput & reliability", fill=(71, 85, 105), font=font_sub)

    out_path = os.path.join(ILLUST_DIR, "single_vs_multi_tree.png")
    img.save(out_path, "PNG")
    return out_path

def create_multicore_chip_3d():
    """Slide 13: Isometric 3D Multicore CPU package with silicon die grid."""
    w, h = 800, 800
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy, scale = 400, 380, 1.4

    # Substrate Package
    draw_iso_box(draw, -160, -160, 0, 320, 320, 20,
                 top_col=(40, 44, 56), left_col=(22, 25, 34), right_col=(30, 35, 46),
                 outline_col=(70, 85, 110), cx=cx, cy=cy, scale=scale)

    # Heat Spreader Rim
    draw_iso_box(draw, -130, -130, 20, 260, 260, 15,
                 top_col=(30, 34, 44), left_col=(18, 20, 28), right_col=(24, 28, 38),
                 outline_col=(90, 105, 130), cx=cx, cy=cy, scale=scale)

    # Silicon Die Cores Grid
    grid_size = 3
    block_sz = 60
    gap = 12
    start = - (grid_size * block_sz + (grid_size - 1) * gap) / 2

    for row in range(grid_size):
        for col in range(grid_size):
            bx = start + col * (block_sz + gap)
            by = start + row * (block_sz + gap)
            is_core = (row + col) % 2 == 0
            top_c = (56, 189, 248) if is_core else (129, 140, 248)
            draw_iso_box(draw, bx, by, 35, block_sz, block_sz, 10,
                         top_col=(25, 35, 50), left_col=(15, 22, 32), right_col=(20, 28, 40),
                         outline_col=top_c, cx=cx, cy=cy, scale=scale)

    # Gold Contact Pins
    for i in range(12):
        px = -150 + i * 26
        draw_iso_box(draw, px, 160, -12, 12, 6, 12,
                     top_col=(245, 158, 11), left_col=(180, 115, 10), right_col=(210, 135, 10),
                     cx=cx, cy=cy, scale=scale)

    final_img = add_ambient_glow(img, cx, cy, 260, (56, 189, 248, 70))
    out_path = os.path.join(ILLUST_DIR, "iso_multicore_chip.png")
    final_img.save(out_path, "PNG")
    return out_path

def generate_all_gamma_assets():
    a1 = create_motherboard_illustration()
    a2 = create_system_bus_3parts_illustration()
    a3 = create_storage_pyramid_illustration()
    a4 = create_single_vs_multi_illustration()
    a5 = create_multicore_chip_3d()
    print(f"Generated {len([a1, a2, a3, a4, a5])} Gamma/Envato isometric assets in {ILLUST_DIR}")
    return [a1, a2, a3, a4, a5]

if __name__ == "__main__":
    generate_all_gamma_assets()
