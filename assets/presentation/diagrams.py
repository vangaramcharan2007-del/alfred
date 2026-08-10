"""
assets/presentation/diagrams.py
Generates clean, high-resolution architectural diagram assets for the
Operating System Concepts (10th Edition) Chapter 1 presentation.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(ASSETS_DIR, exist_ok=True)

def get_font(size=20, bold=False):
    try:
        font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
        font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", font_name)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        arial = "arialbd.ttf" if bold else "arial.ttf"
        font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", arial)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def create_system_components_diagram():
    """Generates Slide 2 Abstract View of Computer System (Textbook Fig 1.1)"""
    width, height = 1200, 700
    img = Image.new("RGBA", (width, height), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    
    tiers = [
        {"title": "USERS (Users 1, 2, ... N)", "desc": "People, machines, other computers requiring computation", "color": (56, 189, 248), "bg": (15, 23, 42)},
        {"title": "APPLICATION & SYSTEM PROGRAMS", "desc": "Compilers, Assemblers, Text Editors, Database Systems, Web Browsers", "color": (129, 140, 248), "bg": (17, 24, 39)},
        {"title": "OPERATING SYSTEM", "desc": "Controls & coordinates use of hardware among competing applications", "color": (52, 211, 153), "bg": (6, 78, 59)},
        {"title": "COMPUTER HARDWARE (Physical Computing Engine)", "desc": "CPU  |  Main Memory  |  I/O Devices & Controllers", "color": (245, 158, 11), "bg": (30, 41, 59)}
    ]
    
    y = 30
    box_height = 110
    spacing = 45
    
    for i, tier in enumerate(tiers):
        box_y = y + i * (box_height + spacing)
        draw.rounded_rectangle([80, box_y, width - 80, box_y + box_height], radius=16, fill=(22, 30, 46, 255), outline=tier["color"], width=2)
        draw.rounded_rectangle([80, box_y, 96, box_y + box_height], radius=8, fill=tier["color"])
        
        font_title = get_font(24, bold=True)
        draw.text((120, box_y + 22), tier["title"], fill=(248, 250, 252), font=font_title)
        
        font_desc = get_font(18, bold=False)
        draw.text((120, box_y + 60), tier["desc"], fill=(148, 163, 184), font=font_desc)
        
        if i < len(tiers) - 1:
            arrow_y = box_y + box_height + 6
            arrow_center = width // 2
            draw.line([(arrow_center, arrow_y), (arrow_center, arrow_y + 32)], fill=(56, 189, 248), width=3)
            draw.polygon([
                (arrow_center - 8, arrow_y + 24),
                (arrow_center + 8, arrow_y + 24),
                (arrow_center, arrow_y + 34)
            ], fill=(56, 189, 248))
            
    out_path = os.path.join(ASSETS_DIR, "system_components.png")
    img.save(out_path, "PNG")
    return out_path

def create_multicore_diagram():
    """Generates Slide 4 Multicore SMP Processor architecture diagram (Textbook Fig 1.8)"""
    width, height = 1200, 650
    img = Image.new("RGBA", (width, height), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([40, 30, width - 40, 460], radius=20, fill=(17, 24, 39, 255), outline=(56, 189, 248), width=3)
    
    font_chip = get_font(22, bold=True)
    draw.text((60, 48), "PROCESSOR CHIP (Multicore CPU Package)", fill=(56, 189, 248), font=font_chip)
    
    core_w = 240
    core_h = 240
    start_x = 80
    gap = (width - 160 - (4 * core_w)) // 3
    
    font_core = get_font(19, bold=True)
    font_sub = get_font(15, bold=False)
    
    for i in range(4):
        cx = start_x + i * (core_w + gap)
        cy = 95
        draw.rounded_rectangle([cx, cy, cx + core_w, cy + core_h], radius=12, fill=(30, 41, 59, 255), outline=(99, 102, 241), width=2)
        draw.text((cx + 20, cy + 18), f"CORE {i}", fill=(248, 250, 252), font=font_core)
        
        draw.rounded_rectangle([cx + 15, cy + 60, cx + core_w - 15, cy + 125], radius=8, fill=(15, 23, 42, 255), outline=(56, 189, 248), width=1)
        draw.text((cx + 25, cy + 72), "Registers & ALU", fill=(56, 189, 248), font=font_sub)
        draw.text((cx + 25, cy + 96), "Instruction Execution", fill=(148, 163, 184), font=get_font(13))
        
        draw.rounded_rectangle([cx + 15, cy + 145, cx + core_w - 15, cy + 215], radius=8, fill=(15, 23, 42, 255), outline=(52, 211, 153), width=1)
        draw.text((cx + 25, cy + 157), "L1 Cache (Private)", fill=(52, 211, 153), font=font_sub)
        draw.text((cx + 25, cy + 182), "Ultra Fast Per-Core", fill=(148, 163, 184), font=get_font(13))
        
        draw.line([(cx + core_w//2, cy + core_h), (cx + core_w//2, 365)], fill=(129, 140, 248), width=2)
        draw.polygon([(cx + core_w//2 - 5, 360), (cx + core_w//2 + 5, 360), (cx + core_w//2, 368)], fill=(129, 140, 248))
    
    draw.rounded_rectangle([80, 370, width - 80, 435], radius=12, fill=(30, 27, 75, 255), outline=(168, 85, 247), width=2)
    draw.text((width//2 - 180, 390), "SHARED CACHE / ON-CHIP INTERCONNECT", fill=(216, 180, 254), font=font_core)
    
    draw.line([(width//2, 460), (width//2, 530)], fill=(56, 189, 248), width=4)
    draw.polygon([(width//2 - 8, 520), (width//2 + 8, 520), (width//2, 532)], fill=(56, 189, 248))
    
    draw.rounded_rectangle([180, 535, width - 180, 620], radius=16, fill=(15, 23, 42, 255), outline=(52, 211, 153), width=3)
    draw.text((width//2 - 190, 555), "MAIN MEMORY (System DRAM)", fill=(52, 211, 153), font=font_core)
    draw.text((width//2 - 250, 585), "Uniform Shared Physical Address Space across all 4 Cores", fill=(148, 163, 184), font=font_sub)
    
    out_path = os.path.join(ASSETS_DIR, "multicore_chip.png")
    img.save(out_path, "PNG")
    return out_path

def create_numa_diagram():
    """Generates Slide 5 NUMA Architecture diagram (Textbook Fig 1.9)"""
    width, height = 1200, 650
    img = Image.new("RGBA", (width, height), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    
    font_node = get_font(20, bold=True)
    font_sub = get_font(16, bold=False)
    font_bus = get_font(22, bold=True)
    
    nodes = [
        {"title": "NUMA NODE 0", "x": 80, "y": 40},
        {"title": "NUMA NODE 1", "x": 680, "y": 40},
        {"title": "NUMA NODE 2", "x": 80, "y": 400},
        {"title": "NUMA NODE 3", "x": 680, "y": 400},
    ]
    
    node_w = 440
    node_h = 160
    
    for i, node in enumerate(nodes):
        nx, ny = node["x"], node["y"]
        draw.rounded_rectangle([nx, ny, nx + node_w, ny + node_h], radius=14, fill=(17, 24, 39, 255), outline=(56, 189, 248), width=2)
        draw.text((nx + 20, ny + 15), node["title"], fill=(56, 189, 248), font=font_node)
        
        draw.rounded_rectangle([nx + 20, ny + 55, nx + 200, ny + 135], radius=8, fill=(30, 41, 59, 255), outline=(129, 140, 248), width=1)
        draw.text((nx + 40, ny + 72), f"CPU / Core {i}", fill=(248, 250, 252), font=get_font(17, True))
        draw.text((nx + 40, ny + 100), "Processor Group", fill=(148, 163, 184), font=get_font(13))
        
        draw.line([(nx + 200, ny + 95), (nx + 240, ny + 95)], fill=(52, 211, 153), width=3)
        draw.polygon([(nx + 235, ny + 90), (nx + 235, ny + 100), (nx + 243, ny + 95)], fill=(52, 211, 153))
        
        draw.rounded_rectangle([nx + 240, ny + 55, nx + 420, ny + 135], radius=8, fill=(6, 78, 59, 255), outline=(52, 211, 153), width=2)
        draw.text((nx + 255, ny + 72), f"LOCAL MEMORY {i}", fill=(52, 211, 153), font=get_font(15, True))
        draw.text((nx + 255, ny + 100), "Fast Low-Latency", fill=(167, 243, 208), font=get_font(13))
        
        if ny < 250:
            draw.line([(nx + node_w//2, ny + node_h), (nx + node_w//2, 240)], fill=(245, 158, 11), width=3)
        else:
            draw.line([(nx + node_w//2, ny), (nx + node_w//2, 340)], fill=(245, 158, 11), width=3)

    draw.rounded_rectangle([120, 240, width - 120, 340], radius=16, fill=(30, 41, 59, 255), outline=(245, 158, 11), width=3)
    draw.text((width//2 - 240, 260), "SYSTEM INTERCONNECT BUS", fill=(251, 191, 36), font=font_bus)
    draw.text((width//2 - 320, 298), "Accessing Remote Memory incurs Interconnect Overhead (Non-Uniform Latency)", fill=(203, 213, 225), font=font_sub)
    
    out_path = os.path.join(ASSETS_DIR, "numa_architecture.png")
    img.save(out_path, "PNG")
    return out_path

def create_dual_mode_diagram():
    """Generates Slide 8 Dual-Mode Transition diagram (Textbook Fig 1.14)"""
    width, height = 1200, 650
    img = Image.new("RGBA", (width, height), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    
    font_mode = get_font(24, bold=True)
    font_step = get_font(18, bold=True)
    font_desc = get_font(15, bold=False)
    
    draw.rounded_rectangle([60, 60, 520, 580], radius=20, fill=(15, 23, 42, 255), outline=(56, 189, 248), width=3)
    draw.text((120, 90), "USER MODE (Mode Bit = 1)", fill=(56, 189, 248), font=font_mode)
    draw.text((100, 130), "Executing User Process / Application", fill=(148, 163, 184), font=font_desc)
    
    draw.rounded_rectangle([90, 180, 490, 300], radius=12, fill=(30, 41, 59, 255), outline=(56, 189, 248), width=1)
    draw.text((110, 200), "1. User Process Executing", fill=(248, 250, 252), font=font_step)
    draw.text((110, 235), "• Non-privileged instructions only\n• Direct hardware access forbidden\n• Memory restricted to user space", fill=(148, 163, 184), font=font_desc)
    
    draw.rounded_rectangle([90, 340, 490, 460], radius=12, fill=(30, 41, 59, 255), outline=(245, 158, 11), width=1)
    draw.text((110, 360), "2. Calls System Call / Trap", fill=(251, 191, 36), font=font_step)
    draw.text((110, 395), "• User program requests OS service\n• E.g. open(), read(), write(), fork()\n• Triggers hardware mode switch", fill=(148, 163, 184), font=font_desc)
    
    draw.rounded_rectangle([680, 60, 1140, 580], radius=20, fill=(15, 23, 42, 255), outline=(244, 63, 94), width=3)
    draw.text((720, 90), "KERNEL MODE (Mode Bit = 0)", fill=(244, 63, 94), font=font_mode)
    draw.text((720, 130), "Executing Operating System Kernel", fill=(148, 163, 184), font=font_desc)
    
    draw.rounded_rectangle([710, 180, 1110, 300], radius=12, fill=(69, 10, 10, 255), outline=(244, 63, 94), width=1)
    draw.text((730, 200), "3. Execute Privileged Service", fill=(254, 205, 211), font=font_step)
    draw.text((730, 235), "• Mode bit set to 0 by hardware\n• Full access to memory & hardware\n• Kernel validates request parameters", fill=(253, 164, 175), font=font_desc)
    
    draw.rounded_rectangle([710, 340, 1110, 460], radius=12, fill=(30, 41, 59, 255), outline=(52, 211, 153), width=1)
    draw.text((730, 360), "4. Return to User Mode", fill=(52, 211, 153), font=font_step)
    draw.text((730, 395), "• Hardware resets Mode Bit to 1\n• Restores user process context\n• Program execution continues", fill=(148, 163, 184), font=font_desc)
    
    draw.line([(490, 400), (710, 240)], fill=(245, 158, 11), width=4)
    draw.polygon([(705, 230), (718, 238), (702, 248)], fill=(245, 158, 11))
    draw.text((530, 280), "TRAP / SYSCALL\n(Set mode bit = 0)", fill=(251, 191, 36), font=get_font(14, True))
    
    draw.line([(710, 400), (490, 520)], fill=(52, 211, 153), width=4)
    draw.polygon([(495, 510), (482, 522), (498, 528)], fill=(52, 211, 153))
    draw.text((530, 470), "RETURN FROM SYSCALL\n(Reset mode bit = 1)", fill=(52, 211, 153), font=get_font(14, True))
    
    out_path = os.path.join(ASSETS_DIR, "dual_mode.png")
    img.save(out_path, "PNG")
    return out_path

def create_storage_hierarchy_diagram():
    """Generates Slide 11 Storage-Device Hierarchy (Textbook Fig 1.10)"""
    width, height = 1200, 680
    img = Image.new("RGBA", (width, height), (15, 23, 42, 0))
    draw = ImageDraw.Draw(img)
    
    tiers = [
        {"name": "REGISTERS", "type": "Volatile Storage", "managed": "Compiler / CPU Hardware", "w": 400, "color": (244, 63, 94)},
        {"name": "CACHE (L1 / L2 / L3)", "type": "Volatile Storage", "managed": "Hardware / MMU", "w": 560, "color": (245, 158, 11)},
        {"name": "MAIN MEMORY (DRAM)", "type": "Volatile Storage", "managed": "Operating System", "w": 720, "color": (52, 211, 153)},
        {"name": "SOLID-STATE DISK (NVM)", "type": "Nonvolatile Storage", "managed": "Operating System / File System", "w": 880, "color": (56, 189, 248)},
        {"name": "HARD DISK / OPTICAL / MAGNETIC", "type": "Nonvolatile Storage", "managed": "Operating System / File System", "w": 1040, "color": (129, 140, 248)}
    ]
    
    y = 50
    h = 95
    spacing = 20
    
    font_name = get_font(19, bold=True)
    font_meta = get_font(14, bold=False)
    
    for i, tier in enumerate(tiers):
        tw = tier["w"]
        tx = (width - tw) // 2
        ty = y + i * (h + spacing)
        
        draw.rounded_rectangle([tx, ty, tx + tw, ty + h], radius=12, fill=(22, 30, 46, 255), outline=tier["color"], width=2)
        draw.rounded_rectangle([tx, ty, tx + 14, ty + h], radius=6, fill=tier["color"])
        
        draw.text((tx + 30, ty + 20), tier["name"], fill=(248, 250, 252), font=font_name)
        draw.text((tx + 30, ty + 54), f"Type: {tier['type']}  |  Managed By: {tier['managed']}", fill=(148, 163, 184), font=font_meta)
    
    draw.line([(50, height - 80), (50, 80)], fill=(244, 63, 94), width=4)
    draw.polygon([(42, 90), (58, 90), (50, 72)], fill=(244, 63, 94))
    draw.text((20, height//2 - 60), "FASTER\nMORE EXPENSIVE\nSMALLER CAPACITY", fill=(244, 63, 94), font=get_font(13, True))
    
    draw.line([(width - 50, 80), (width - 50, height - 80)], fill=(56, 189, 248), width=4)
    draw.polygon([(width - 58, height - 90), (width - 42, height - 90), (width - 50, height - 72)], fill=(56, 189, 248))
    draw.text((width - 150, height//2 - 60), "GREATER CAPACITY\nLOWER COST / BIT\nSLOWER ACCESS", fill=(56, 189, 248), font=get_font(13, True))
    
    out_path = os.path.join(ASSETS_DIR, "storage_hierarchy.png")
    img.save(out_path, "PNG")
    return out_path

def generate_all_diagrams():
    p1 = create_system_components_diagram()
    p2 = create_multicore_diagram()
    p3 = create_numa_diagram()
    p4 = create_dual_mode_diagram()
    p5 = create_storage_hierarchy_diagram()
    return [p1, p2, p3, p4, p5]

if __name__ == "__main__":
    generated = generate_all_diagrams()
    print(f"Generated {len(generated)} diagram assets in {ASSETS_DIR}")
