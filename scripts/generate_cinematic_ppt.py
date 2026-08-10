"""
scripts/generate_cinematic_ppt.py
Generates the 15-slide Luxury Minimalist Tech PowerPoint presentation with:
- Native OpenXML Morph & Smooth Transitions on all slides
- Cinematic Ambient Lighting & Glow Overlays
- Frosted Glass Cards with High-Tech Corner Framing Accents
- 3D Isometric Hardware Artworks (Motherboard, Stacked Layers, Bus, Multicore Chip)
- Equal 3-Speaker structure: V. Ram Charan (1-5), Vedhanth (6-10), Lochan (11-15)
- Zero textbook or author citations
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "presentation")
GAMMA_DIR = os.path.join(ASSETS_DIR, "gamma_assets")
sys.path.insert(0, ROOT_DIR)

from assets.presentation.gamma_illustrations import generate_all_gamma_assets

# Luxury Dark Palette (Gamma / Envato Style)
BG_CARBON = RGBColor(18, 20, 28)        # #12141C Deep Charcoal
CARD_BG = RGBColor(26, 30, 42)          # #1A1E2A Translucent Dark Card
CARD_BORDER = RGBColor(46, 54, 74)      # #2E364A Subtle Outline
CARD_HIGHLIGHT = RGBColor(38, 45, 64)   # #262D40 Highlight Card
TEXT_WHITE = RGBColor(255, 255, 255)    # #FFFFFF Crisp Pure White
TEXT_MUTED = RGBColor(160, 175, 200)    # #A0AFC8 Soft Slate
TEXT_DIM = RGBColor(110, 125, 150)      # #6E7D96 Dim Metadata
ACCENT_CYAN = RGBColor(56, 189, 248)    # #38BDF8 Soft Ice Cyan
ACCENT_INDIGO = RGBColor(129, 140, 248) # #818CF8 Hyper Indigo
ACCENT_EMERALD = RGBColor(52, 211, 153) # #34D399 Emerald Green
ACCENT_AMBER = RGBColor(245, 158, 11)   # #F59E0B Amber
ACCENT_ROSE = RGBColor(244, 63, 94)     # #F43F5E Coral / Alert
PILL_BG = RGBColor(30, 36, 52)          # #1E2434

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

def set_slide_backdrop(slide, color=BG_CARBON):
    """Creates a clean solid matte carbon backdrop."""
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = color
    bg_shape.line.fill.background()

def apply_slide_morph_transition(slide):
    """Applies valid OpenXML Morph & Smooth Slide Transition."""
    tr_xml = parse_xml(
        '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="med" dur="1500">'
        '<p14:morph option="byObject"/>'
        '</p:transition>'
    )
    slide._element.append(tr_xml)

def add_header(slide, slide_num, total_slides, act_title, speaker_name, title, subtitle=None):
    """Creates a clean Gamma-style header with subtle pill tags."""
    # Top Left Act Tag
    act_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.5), Inches(0.34))
    act_box.fill.solid()
    act_box.fill.fore_color.rgb = PILL_BG
    act_box.line.color.rgb = CARD_BORDER
    act_box.line.width = Pt(1)
    tf_act = act_box.text_frame
    tf_act.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_act = tf_act.paragraphs[0]
    p_act.text = act_title.upper()
    p_act.font.name = FONT_HEADING
    p_act.font.size = Pt(9)
    p_act.font.bold = True
    p_act.font.color.rgb = ACCENT_CYAN
    p_act.alignment = PP_ALIGN.CENTER

    # Top Right Speaker Badge
    spk_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(0.4), Inches(2.5), Inches(0.34))
    spk_box.fill.solid()
    spk_box.fill.fore_color.rgb = PILL_BG
    spk_box.line.color.rgb = CARD_BORDER
    spk_box.line.width = Pt(1)
    tf_spk = spk_box.text_frame
    tf_spk.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_spk = tf_spk.paragraphs[0]
    p_spk.text = speaker_name.upper()
    p_spk.font.name = FONT_HEADING
    p_spk.font.size = Pt(9)
    p_spk.font.bold = True
    p_spk.font.color.rgb = ACCENT_INDIGO
    p_spk.alignment = PP_ALIGN.CENTER

    # Top Right Counter
    num_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.45), Inches(0.4), Inches(1.1), Inches(0.34))
    num_box.fill.solid()
    num_box.fill.fore_color.rgb = PILL_BG
    num_box.line.color.rgb = CARD_BORDER
    num_box.line.width = Pt(1)
    tf_num = num_box.text_frame
    tf_num.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_num = tf_num.paragraphs[0]
    p_num.text = f"{slide_num:02d} / {total_slides:02d}"
    p_num.font.name = FONT_HEADING
    p_num.font.size = Pt(9)
    p_num.font.bold = True
    p_num.font.color.rgb = TEXT_DIM
    p_num.alignment = PP_ALIGN.CENTER

    # Main Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.733), Inches(0.75))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    p_t = tf_title.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(24)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    if subtitle:
        p_sub = tf_title.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11.5)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(2)

def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=None, corner_accent=True):
    """Creates a minimalist glass card with high-tech corner framing and glowing accents."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)

    # Optional side accent bar
    if accent_bar:
        bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(0.08), Inches(height))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_bar
        bar.line.fill.background()

    # Optional high-tech corner tick mark (Top-Right)
    if corner_accent:
        c_tick = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left + width - 0.25), Inches(top + 0.08), Inches(0.15), Inches(0.02))
        c_tick.fill.solid()
        c_tick.fill.fore_color.rgb = accent_bar if accent_bar else CARD_BORDER
        c_tick.line.fill.background()

    if title:
        tb = slide.shapes.add_textbox(Inches(left + (0.24 if accent_bar else 0.2)), Inches(top + 0.15), Inches(width - 0.4), Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    return card

def add_bottom_banner(slide, text, tag="Speed-up Rule:", tag_color=ACCENT_CYAN):
    """Adds a sleek full-width bottom callout banner matching the Gamma template."""
    banner = add_card(slide, 0.8, 6.35, 11.733, 0.65, border_color=CARD_BORDER, bg_color=PILL_BG)
    tb = slide.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.3), Inches(0.45))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    
    r_tag = p.add_run()
    r_tag.text = f"□ {tag} "
    r_tag.font.name = FONT_HEADING
    r_tag.font.size = Pt(10.5)
    r_tag.font.bold = True
    r_tag.font.color.rgb = tag_color
    
    r_body = p.add_run()
    r_body.text = text
    r_body.font.name = FONT_BODY
    r_body.font.size = Pt(10.5)
    r_body.font.color.rgb = TEXT_WHITE

def add_circular_step(slide, cx, cy, radius, label, sublabel=None, number=None, border_color=ACCENT_CYAN):
    """Draws sleek circular process step nodes matching Gamma template Slide 6 & 9."""
    r_inch = Inches(radius)
    # Circle shape with glowing border
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - radius), Inches(cy - radius), Inches(radius * 2), Inches(radius * 2))
    circle.fill.solid()
    circle.fill.fore_color.rgb = PILL_BG
    circle.line.color.rgb = border_color
    circle.line.width = Pt(2)

    # Text inside circle
    tb = slide.shapes.add_textbox(Inches(cx - radius - 0.2), Inches(cy - 0.2), Inches(radius * 2 + 0.4), Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    if number:
        p.text = str(number)
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
    else:
        p.text = "< / >"
        p.font.name = FONT_HEADING
        p.font.size = Pt(12)
        p.font.color.rgb = ACCENT_CYAN

    # Sublabel under circle
    if label:
        tb_lbl = slide.shapes.add_textbox(Inches(cx - 0.8), Inches(cy + radius + 0.1), Inches(1.6), Inches(0.6))
        tf_l = tb_lbl.text_frame
        tf_l.word_wrap = True
        p_l = tf_l.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = label
        p_l.font.name = FONT_HEADING
        p_l.font.size = Pt(10.5)
        p_l.font.bold = True
        p_l.font.color.rgb = TEXT_WHITE

def set_speaker_notes(slide, what_to_say, concept, transition, cue):
    """Sets structured presenter script notes on the slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = f"=== PRESENTER SCRIPT ===\n\n" \
                      f"1. WHAT TO SAY (Spoken Script):\n{what_to_say}\n\n" \
                      f"2. KEY ARCHITECTURAL CONCEPT:\n{concept}\n\n" \
                      f"3. TRANSITION TO NEXT SLIDE:\n{transition}\n\n" \
                      f"4. PRESENTATION CUE:\n{cue}"

def build_presentation():
    # 1. Generate all isometric assets with ambient lighting
    generate_all_gamma_assets()
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE & PRESENTERS (V. Ram Charan)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s1)
    apply_slide_morph_transition(s1)

    # Left Column Text & Presenters
    tb_t = s1.shapes.add_textbox(Inches(0.8), Inches(1.0), Inches(7.0), Inches(2.2))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True
    p1 = tf_t.paragraphs[0]
    p1.text = "Computer System Architecture"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf_t.add_paragraph()
    p2.text = "Understanding the Hardware Foundation of Operating Systems"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(6)

    p3 = tf_t.add_paragraph()
    p3.text = "Operating Systems — System Architecture & Execution Foundations"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(11)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(4)

    # 3 Presenter Rows with Circular Avatar Badges
    presenters = [
        ("V. Ram Charan", "Speaker 1 (Act I Lead)", ACCENT_CYAN),
        ("Vedhanth", "Speaker 2 (Act II Lead)", ACCENT_INDIGO),
        ("Lochan", "Speaker 3 (Act III Lead)", ACCENT_EMERALD)
    ]
    for i, (name, role, col) in enumerate(presenters):
        py = 3.3 + i * 0.95
        # Avatar Circle
        avatar = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(py), Inches(0.7), Inches(0.7))
        avatar.fill.solid()
        avatar.fill.fore_color.rgb = PILL_BG
        avatar.line.color.rgb = CARD_BORDER
        avatar.line.width = Pt(1)
        tf_av = avatar.text_frame
        p_av = tf_av.paragraphs[0]
        p_av.alignment = PP_ALIGN.CENTER
        p_av.text = "👤"
        p_av.font.size = Pt(14)
        
        # Name Text
        tb_p = s1.shapes.add_textbox(Inches(1.65), Inches(py + 0.05), Inches(5.5), Inches(0.6))
        tf_p = tb_p.text_frame
        p_pn = tf_p.paragraphs[0]
        p_pn.text = name
        p_pn.font.name = FONT_HEADING
        p_pn.font.size = Pt(14)
        p_pn.font.bold = True
        p_pn.font.color.rgb = TEXT_WHITE
        p_pr = tf_p.add_paragraph()
        p_pr.text = role
        p_pr.font.name = FONT_BODY
        p_pr.font.size = Pt(10)
        p_pr.font.color.rgb = col

    # Bottom Quote Line with vertical cyan accent
    q_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.3), Inches(0.06), Inches(0.65))
    q_bar.fill.solid()
    q_bar.fill.fore_color.rgb = ACCENT_CYAN
    q_bar.line.fill.background()
    tb_q = s1.shapes.add_textbox(Inches(0.95), Inches(6.3), Inches(6.8), Inches(0.65))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    pq = tf_q.paragraphs[0]
    pq.text = '"The operating system is the software most intimately involved with computer hardware."'
    pq.font.name = FONT_BODY
    pq.font.size = Pt(11)
    pq.font.italic = True
    pq.font.color.rgb = TEXT_MUTED

    # Right Side Isometric Motherboard Art with Ambient Glow
    mb_img = os.path.join(GAMMA_DIR, "iso_motherboard.png")
    if os.path.exists(mb_img):
        s1.shapes.add_picture(mb_img, Inches(7.5), Inches(0.8), width=Inches(5.2))

    set_speaker_notes(
        s1,
        "Good morning everyone. Welcome to our presentation on Computer System Architecture. I am Ram Charan, and together with Vedhanth and Lochan, we will walk you through the fundamental relationship between computer hardware and the operating system. The OS is the critical piece of software that transforms raw silicon, memory, and devices into a cohesive, secure platform.",
        "The Operating System acts as the vital bridge between user software and physical hardware, balancing resource allocation and execution control.",
        "Let us begin with Slide 2 by looking at the four fundamental components that make up any computer system.",
        "Stand center, introduce team members, gesture to the presenter cards."
    )

    # =========================================================================
    # SLIDE 2: WHAT IS A COMPUTER SYSTEM? (V. Ram Charan)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s2)
    apply_slide_morph_transition(s2)
    add_header(s2, 2, 15, "Act I: Foundations", "V. Ram Charan", "What is a Computer System?")

    # Left: 3D Stacked Layers Tower
    tower_img = os.path.join(GAMMA_DIR, "iso_stacked_layers.png")
    if os.path.exists(tower_img):
        s2.shapes.add_picture(tower_img, Inches(0.8), Inches(1.6), width=Inches(4.5))

    # Right: Four Major Components List
    tb_fc = s2.shapes.add_textbox(Inches(5.6), Inches(1.6), Inches(6.9), Inches(3.0))
    tf_fc = tb_fc.text_frame
    tf_fc.word_wrap = True

    p_fch = tf_fc.paragraphs[0]
    p_fch.text = "Four Major Components"
    p_fch.font.name = FONT_HEADING
    p_fch.font.size = Pt(16)
    p_fch.font.bold = True
    p_fch.font.color.rgb = TEXT_WHITE

    comp_items = [
        ("→  User", "Interacts with application programs"),
        ("→  Application Programs", "Solve user computing problems (compilers, databases, browsers)"),
        ("→  Operating System", "Controls and coordinates hardware use among competing applications"),
        ("→  Computer Hardware", "CPU, Main Memory, and I/O Devices providing raw computing resources")
    ]
    for k, v in comp_items:
        pk = tf_fc.add_paragraph()
        pk.text = k
        pk.font.name = FONT_HEADING
        pk.font.size = Pt(13)
        pk.font.bold = True
        pk.font.color.rgb = ACCENT_CYAN
        pk.space_before = Pt(6)

        pv = tf_fc.add_paragraph()
        pv.text = "    " + v
        pv.font.name = FONT_BODY
        pv.font.size = Pt(10.5)
        pv.font.color.rgb = TEXT_MUTED

    # Bottom Row: 3 Role Cards
    r_w = 3.7
    cards_s2 = [
        ("Resource Allocator", "Manages CPU time, memory space, storage, and I/O devices fairly and efficiently.", ACCENT_CYAN),
        ("Control Program", "Prevents errors and improper use of the computer by monitoring execution.", ACCENT_EMERALD),
        ("Hardware Manager", "Coordinates hardware among all running applications to maximize throughput.", ACCENT_INDIGO)
    ]
    for i, (rtitle, rdesc, rcol) in enumerate(cards_s2):
        rx = 0.8 + i * 4.0
        add_card(s2, rx, 4.8, r_w, 1.8, rtitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=rcol)
        tb_r = s2.shapes.add_textbox(Inches(rx + 0.2), Inches(5.3), Inches(r_w - 0.4), Inches(1.1))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        pr = tf_r.paragraphs[0]
        pr.text = rdesc
        pr.font.name = FONT_BODY
        pr.font.size = Pt(10.5)
        pr.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s2,
        "A computer system is divided into four components: Users, Application Programs, the Operating System, and Computer Hardware. Hardware supplies raw computing resources—the CPU, main memory, and I/O devices. Sitting right between applications and hardware is the Operating System, which fulfills two vital roles: as a Resource Allocator managing CPU cycles and memory without conflict, and as a Control Program preventing bugs and illegal operations from crashing the machine.",
        "Four-component computer system model & OS duality as Resource Allocator and Control Program.",
        "Now let's examine how computer system architectures have evolved from single-processor systems to modern multi-core chips.",
        "Point to the vertical diagram showing the OS buffering applications from raw hardware."
    )

    # =========================================================================
    # SLIDE 3: COMPUTER-SYSTEM ORGANIZATION (V. Ram Charan)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s3)
    apply_slide_morph_transition(s3)
    add_header(s3, 3, 15, "Act I: Foundations", "V. Ram Charan", "Computer-System Organization")

    # Left: Isometric System Bus Topology
    bus_img = os.path.join(GAMMA_DIR, "iso_system_bus.png")
    if os.path.exists(bus_img):
        s3.shapes.add_picture(bus_img, Inches(0.8), Inches(1.6), width=Inches(4.6))

    # Right Column: Modern System Components & 3 Key Aspects
    tb_mc = s3.shapes.add_textbox(Inches(5.7), Inches(1.6), Inches(6.8), Inches(2.2))
    tf_mc = tb_mc.text_frame
    tf_mc.word_wrap = True

    p_mch = tf_mc.paragraphs[0]
    p_mch.text = "Modern System Components"
    p_mch.font.name = FONT_HEADING
    p_mch.font.size = Pt(15)
    p_mch.font.bold = True
    p_mch.font.color.rgb = TEXT_WHITE

    pts_s3 = [
        "One or more CPUs and device controllers connected via a common bus",
        "Device Controllers manage specific device types — disk, audio, graphics",
        "Memory Controller synchronizes access to shared system memory",
        "Parallel Execution: CPU and device controllers compete concurrently for memory cycles"
    ]
    for pt in pts_s3:
        p = tf_mc.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    # Right Bottom: 3 Key Aspects Stacked Cards
    aspects = [
        ("Interrupts", "Hardware signals CPU when immediate attention is required", ACCENT_CYAN),
        ("Storage Structure", "Hierarchy from ultra-fast registers down to secondary storage", ACCENT_INDIGO),
        ("I/O Structure", "Data movement between CPU, main memory, and peripheral controllers", ACCENT_EMERALD)
    ]
    for i, (atitle, adesc, acol) in enumerate(aspects):
        ay = 4.2 + i * 1.0
        add_card(s3, 5.7, ay, 6.8, 0.85, atitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=acol)
        tb_a = s3.shapes.add_textbox(Inches(5.95), Inches(ay + 0.4), Inches(6.4), Inches(0.4))
        tf_a = tb_a.text_frame
        pa = tf_a.paragraphs[0]
        pa.text = adesc
        pa.font.name = FONT_BODY
        pa.font.size = Pt(10)
        pa.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s3,
        "In modern computer system organization, CPUs and device controllers are connected through a shared system bus. Each device controller manages a specific device type—like disks, network interfaces, or displays—and maintains its own local buffer storage. The CPU and controllers execute concurrently, competing for memory cycles managed by the memory controller.",
        "Computer-system organization, shared bus interconnects, device controllers, and concurrent execution.",
        "Let's look at how single-processor systems compare with multiprocessor architectures.",
        "Trace the connection of CPUs, memory, and devices to the common central bus."
    )

    # =========================================================================
    # SLIDE 4: SINGLE-PROCESSOR VS MULTIPROCESSOR (V. Ram Charan)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s4)
    apply_slide_morph_transition(s4)
    add_header(s4, 4, 15, "Act I: Foundations", "V. Ram Charan", "Single-Processor vs. Multiprocessor Systems")

    # Left: Text Descriptions
    tb_s4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(5.8), Inches(4.5))
    tf_s4 = tb_s4.text_frame
    tf_s4.word_wrap = True

    p_sp = tf_s4.paragraphs[0]
    p_sp.text = "Single-Processor Systems"
    p_sp.font.name = FONT_HEADING
    p_sp.font.size = Pt(16)
    p_sp.font.bold = True
    p_sp.font.color.rgb = TEXT_WHITE

    pts_sp = [
        "One CPU with a single general-purpose processing core",
        "May include special-purpose processors — disk, keyboard, graphics controllers",
        "Special-purpose processors do not run user processes"
    ]
    for pt in pts_sp:
        p = tf_s4.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    p_mp = tf_s4.add_paragraph()
    p_mp.text = "Multiprocessor Systems"
    p_mp.font.name = FONT_HEADING
    p_mp.font.size = Pt(16)
    p_mp.font.bold = True
    p_mp.font.color.rgb = TEXT_WHITE
    p_mp.space_before = Pt(16)

    pts_mp = [
        "Two or more processors, each with a single-core CPU",
        "Share bus, clock, memory, and peripheral devices",
        "Dominate modern computing — from mobile devices to high-performance servers"
    ]
    for pt in pts_mp:
        p = tf_s4.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    # Right: High-Contrast Tree Card
    tree_img = os.path.join(GAMMA_DIR, "single_vs_multi_tree.png")
    if os.path.exists(tree_img):
        s4.shapes.add_picture(tree_img, Inches(7.0), Inches(1.5), width=Inches(5.5))

    # Bottom Banner
    add_bottom_banner(s4, "With N processors, speed-up is always less than N due to memory contention and coordination overhead.", "Speed-up Rule:", ACCENT_AMBER)

    set_speaker_notes(
        s4,
        "Single-processor systems have one main general-purpose CPU. While they may contain special-purpose microcontrollers for disks or keyboards, only the main CPU executes user applications. Multiprocessor systems introduce two or more processors sharing memory and buses, delivering increased throughput and reliability. However, as our Speed-up Rule notes, adding N processors yields less than an N-fold speed-up due to bus contention and synchronization overhead.",
        "Single vs multiprocessor architectures and the law of diminishing returns in processor scaling.",
        "Let's examine how multicore designs bring multiprocessing directly onto a single silicon chip.",
        "Point to the shared bus bottleneck on the multiprocessor diagram."
    )

    # =========================================================================
    # SLIDE 5: MULTICORE & SYMMETRIC MULTIPROCESSING (V. Ram Charan)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s5)
    apply_slide_morph_transition(s5)
    add_header(s5, 5, 15, "Act I: Foundations", "V. Ram Charan", "Multicore & Symmetric Multiprocessing (SMP)")

    # Left: 4 Concept Cards
    c_w = 6.2
    mc_cards = [
        ("⚙", "Multicore Architecture", "Multiple computing cores reside on a single processor chip, enabling faster on-chip communication than separate chips.", ACCENT_CYAN),
        ("⚡", "Power Efficiency", "Multicore systems consume significantly less power and generate less heat than an equivalent number of single-core chips.", ACCENT_EMERALD),
        ("🧠", "Cache Architecture", "Each core has dedicated registers and L1 cache; L2 and L3 caches may be shared across cores on the chip.", ACCENT_INDIGO),
        ("⚯", "SMP Definition", "Processors and cores cooperate, sharing system resources; the OS sees and manages multiple processing units.", ACCENT_AMBER)
    ]
    for i, (icon, ctitle, cdesc, ccol) in enumerate(mc_cards):
        cy = 1.6 + i * 1.3
        add_card(s5, 0.8, cy, c_w, 1.15, f"{icon}  {ctitle}", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ccol)
        tb = s5.shapes.add_textbox(Inches(1.05), Inches(cy + 0.45), Inches(c_w - 0.4), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    # Right: 3D Multicore Chip Illustration with Glow
    chip_img = os.path.join(GAMMA_DIR, "iso_multicore_chip.png")
    if os.path.exists(chip_img):
        s5.shapes.add_picture(chip_img, Inches(7.5), Inches(1.6), width=Inches(5.0))

    set_speaker_notes(
        s5,
        "Why has the computing industry shifted entirely to multicore? On-chip communication between cores on the same silicon die is vastly faster and consumes far less power than broadcasting signals across motherboard buses. In a multicore SMP system, each core has its own private registers and L1 cache, while sharing lower-level caches and main memory. The operating system views each core as an independent logical CPU, scheduling threads across all cores simultaneously. That concludes Act I. I now pass to Vedhanth.",
        "Multicore chip architecture, private vs shared caches, and Symmetric Multiprocessing (SMP) peer scheduling.",
        "I will now pass the presentation to Vedhanth, who will explain how the operating system maintains hardware control through interrupts and dual-mode execution.",
        "Hand over presentation clicker/focus to Vedhanth."
    )

    # =========================================================================
    # SLIDE 6: INTERRUPTS: HARDWARE-OS COMMUNICATION (Vedhanth)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s6)
    apply_slide_morph_transition(s6)
    add_header(s6, 6, 15, "Act II: OS Control & Memory", "Vedhanth", "Interrupts: Hardware–OS Communication")

    # Left: Circular Step Pipeline
    tb_intro = s6.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(6.0), Inches(0.8))
    tf_in = tb_intro.text_frame
    tf_in.word_wrap = True
    p_in = tf_in.paragraphs[0]
    p_in.text = "The interrupt mechanism is the primary signal pathway between hardware devices and the operating system kernel."
    p_in.font.name = FONT_BODY
    p_in.font.size = Pt(11.5)
    p_in.font.color.rgb = TEXT_MUTED

    # 4 Circular Nodes in a Row
    steps_s6 = ["Hardware Event", "CPU Halt", "Invoke ISR", "Resume CPU"]
    for i, step in enumerate(steps_s6):
        cx = 1.3 + i * 1.45
        add_circular_step(s6, cx, 3.2, 0.55, step, number=i+1, border_color=ACCENT_CYAN if i==0 else CARD_BORDER)

    # Connecting Chevron Arrows
    for i in range(3):
        ax = 1.95 + i * 1.45
        tb_a = s6.shapes.add_textbox(Inches(ax), Inches(3.0), Inches(0.3), Inches(0.4))
        p = tb_a.text_frame.paragraphs[0]
        p.text = "→"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = ACCENT_AMBER

    # Left Bottom Box: Event-driven summary
    add_card(s6, 0.8, 4.4, 5.8, 2.3, "Event-Driven OS Execution", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    tb_ed = s6.shapes.add_textbox(Inches(1.05), Inches(4.85), Inches(5.3), Inches(1.7))
    tf_ed = tb_ed.text_frame
    tf_ed.word_wrap = True
    pts_ed = [
        "The OS sits idle awaiting events if there are no active tasks or I/O requests.",
        "Device controllers assert an electrical interrupt signal along the bus line.",
        "CPU hardware pushes PC and registers onto kernel stack before branching."
    ]
    for pt in pts_ed:
        p = tf_ed.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    # Right Column: 3 Numbered Cards
    c_w = 5.7
    r_cards_s6 = [
        (1, "Interrupt Vector", "Table of pointers to interrupt service routines, indexed by unique interrupt number for deterministic lookup.", ACCENT_CYAN),
        (2, "Priority Levels", "Enable the CPU to defer low-priority interrupts and respond immediately to critical urgent events.", ACCENT_INDIGO),
        (3, "Deferral Capability", "CPU can temporarily disable or mask interrupt handling during critical kernel processing sections.", ACCENT_EMERALD)
    ]
    for num, ctitle, cdesc, ccol in r_cards_s6:
        cy = 1.6 + (num - 1) * 1.65
        add_card(s6, 6.8, cy, c_w, 1.5, ctitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ccol)
        
        num_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), Inches(cy + 0.4), Inches(0.55), Inches(0.55))
        num_card.fill.solid()
        num_card.fill.fore_color.rgb = PILL_BG
        num_card.line.color.rgb = ccol
        num_card.line.width = Pt(1)
        tf_n = num_card.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        p_n.text = str(num)
        p_n.font.name = FONT_HEADING
        p_n.font.size = Pt(14)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_WHITE
        
        tb = s6.shapes.add_textbox(Inches(7.75), Inches(cy + 0.4), Inches(c_w - 1.1), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s6,
        "Thank you Ram Charan. Hello everyone, I am Vedhanth, and in Act II we explore how the Operating System controls and protects hardware. Modern operating systems are completely interrupt-driven. When an I/O device finishes an operation, its controller asserts an interrupt signal. The CPU detects this, saves the current Program Counter and registers, looks up the corresponding service routine in the Interrupt Vector Table, executes the handler, and resumes the user program.",
        "Interrupt mechanism as the core foundation of event-driven OS control and the role of the Interrupt Vector Table.",
        "Now let's distinguish between hardware interrupts, software exceptions, and system calls.",
        "Walk the audience step-by-step through the 4-stage circular pipeline on the left."
    )

    # =========================================================================
    # SLIDE 7: INTERRUPTS & SYSTEM CALLS (Vedhanth)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s7)
    apply_slide_morph_transition(s7)
    add_header(s7, 7, 15, "Act II: OS Control & Memory", "Vedhanth", "Interrupts & System Calls")

    # Left: Isometric Stack Flow with Glow
    tower_img = os.path.join(GAMMA_DIR, "iso_stacked_layers.png")
    if os.path.exists(tower_img):
        s7.shapes.add_picture(tower_img, Inches(0.8), Inches(1.6), width=Inches(4.5))

    # Right Top: 3 Cards (Hardware Interrupt, Trap, System Call)
    right_x = 5.6
    r_w = 6.9
    
    add_card(s7, right_x, 1.6, 3.35, 1.8, "Hardware Interrupt", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_hw = s7.shapes.add_textbox(Inches(right_x + 0.2), Inches(2.05), Inches(3.0), Inches(1.2))
    tf_hw = tb_hw.text_frame
    tf_hw.word_wrap = True
    p = tf_hw.paragraphs[0]
    p.text = "Generated by hardware/device — e.g., keyboard input, timer tick, or I/O completion signal."
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    add_card(s7, right_x + 3.55, 1.6, 3.35, 1.8, "Trap / Exception", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_AMBER)
    tb_tr = s7.shapes.add_textbox(Inches(right_x + 3.75), Inches(2.05), Inches(3.0), Inches(1.2))
    tf_tr = tb_tr.text_frame
    tf_tr.word_wrap = True
    p = tf_tr.paragraphs[0]
    p.text = "Generated by software error or exceptional condition (division by zero, page fault, software trap)."
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    add_card(s7, right_x, 3.55, r_w, 1.1, "System Call Interface", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_EMERALD)
    tb_sc = s7.shapes.add_textbox(Inches(right_x + 0.2), Inches(3.95), Inches(r_w - 0.4), Inches(0.6))
    tf_sc = tb_sc.text_frame
    tf_sc.word_wrap = True
    p = tf_sc.paragraphs[0]
    p.text = "User program requests a privileged operating system service safely via a dedicated trap mechanism."
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = TEXT_MUTED

    # Right Bottom: 5-Node Circular System Call Pipeline
    tb_pipe_lbl = s7.shapes.add_textbox(Inches(right_x), Inches(4.8), Inches(r_w), Inches(0.4))
    p_pl = tb_pipe_lbl.text_frame.paragraphs[0]
    p_pl.text = "System Call Execution Flow"
    p_pl.font.name = FONT_HEADING
    p_pl.font.size = Pt(14)
    p_pl.font.bold = True
    p_pl.font.color.rgb = TEXT_WHITE

    sc_steps = ["User Call", "Trap", "Vector", "Kernel Routine", "OS Operation"]
    for i, step in enumerate(sc_steps):
        cx = right_x + 0.5 + i * 1.35
        add_circular_step(s7, cx, 5.7, 0.45, step, number=i+1, border_color=ACCENT_CYAN if i==1 else CARD_BORDER)

    set_speaker_notes(
        s7,
        "It is critical to distinguish between Hardware Interrupts, Traps, and System Calls. Hardware interrupts are asynchronous signals from physical devices. A Trap or exception is synchronous, triggered directly by an instruction—like a divide-by-zero error or a software trap. A System Call is the programmatic interface user applications use to request services reserved for the OS kernel, executing a trap that safely crosses the user-kernel boundary.",
        "Distinction between asynchronous hardware interrupts and synchronous software traps/syscalls, plus the system call execution sequence.",
        "To ensure user programs cannot bypass this boundary, the hardware enforces Dual-Mode Operation.",
        "Trace the 5-step circular flow across the bottom."
    )

    # =========================================================================
    # SLIDE 8: DUAL-MODE OPERATION (Vedhanth)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s8)
    apply_slide_morph_transition(s8)
    add_header(s8, 8, 15, "Act II: OS Control & Memory", "Vedhanth", "Dual-Mode Operation")

    # Top Left: Two Operating Modes
    add_card(s8, 0.8, 1.6, 5.7, 3.0, "Two Operating Modes & Privileged Instructions", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_dm_l = s8.shapes.add_textbox(Inches(1.05), Inches(2.1), Inches(5.2), Inches(2.3))
    tf_dml = tb_dm_l.text_frame
    tf_dml.word_wrap = True
    pts_dml = [
        "Executable only in kernel mode (Mode Bit = 0)",
        "Include: I/O control, timer management, interrupt disabling, memory protection setup",
        "Hardware enforces mode distinction at the CPU status register level",
        "Boot sequence starts in kernel mode, loads OS, and switches to user mode before running apps"
    ]
    for pt in pts_dml:
        p = tf_dml.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    # Top Right: Why Dual-Mode Matters
    add_card(s8, 6.8, 1.6, 5.7, 3.0, "Why Dual-Mode Matters", border_color=CARD_BORDER, bg_color=CARD_HIGHLIGHT, accent_bar=ACCENT_INDIGO)
    tb_dm_r = s8.shapes.add_textbox(Inches(7.05), Inches(2.1), Inches(5.2), Inches(2.3))
    tf_dmr = tb_dm_r.text_frame
    tf_dmr.word_wrap = True
    pts_dmr = [
        "Prevents incorrect or malicious user programs from interfering with the OS or other programs.",
        "The mode bit is a hardware flag set by the CPU — not software — ensuring enforcement cannot be bypassed.",
        "Every transition from user to kernel mode is a controlled, auditable hardware event via traps/syscalls."
    ]
    for pt in pts_dmr:
        p = tf_dmr.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)

    # Bottom Split Cards: User Mode vs Kernel Mode
    c_w = 5.7
    add_card(s8, 0.8, 4.8, c_w, 1.9, "User Mode", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_um = s8.shapes.add_textbox(Inches(1.05), Inches(5.3), Inches(c_w - 0.4), Inches(1.2))
    tf_um = tb_um.text_frame
    tf_um.word_wrap = True
    p_um = tf_um.paragraphs[0]
    p_um.text = "Active while executing user application code. Mode bit = 1.\nCannot execute privileged instructions or access kernel memory directly."
    p_um.font.name = FONT_BODY
    p_um.font.size = Pt(11)
    p_um.font.color.rgb = TEXT_MUTED

    add_card(s8, 6.8, 4.8, c_w, 1.9, "Kernel Mode", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_ROSE)
    tb_km = s8.shapes.add_textbox(Inches(7.05), Inches(5.3), Inches(c_w - 0.4), Inches(1.2))
    tf_km = tb_km.text_frame
    tf_km.word_wrap = True
    p_km = tf_km.paragraphs[0]
    p_km.text = "Active while executing operating system code. Mode bit = 0.\nFull access to all hardware instructions, memory spaces, and device controllers."
    p_km.font.name = FONT_BODY
    p_km.font.size = Pt(11)
    p_km.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s8,
        "Dual-mode operation is one of the most fundamental concepts in computer science. The CPU hardware contains a Mode Bit: when Mode Bit equals 1, the CPU is in User Mode; when Mode Bit equals 0, it is in Kernel Mode. Why is this necessary? If user applications could directly alter hardware registers or halt the processor, one buggy program could crash the entire computer. By enforcing dual modes in hardware, privileged instructions can only execute when the mode bit is zero.",
        "Dual-mode operation, the hardware Mode Bit (0=Kernel, 1=User), privileged instructions, and fault isolation.",
        "Let's look at exactly what constitutes a privileged instruction and what happens when an illegal operation occurs.",
        "Point to the contrast between User Mode (Mode Bit=1) and Kernel Mode (Mode Bit=0)."
    )

    # =========================================================================
    # SLIDE 9: PROTECTION & TIMER CONTROL (Vedhanth)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s9)
    apply_slide_morph_transition(s9)
    add_header(s9, 9, 15, "Act II: OS Control & Memory", "Vedhanth", "Protection & Timer Control")

    # Left: Protection & Illegal Operation Flow
    add_card(s9, 0.8, 1.6, 5.7, 2.4, "Protection via Privileged Instructions", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_ROSE)
    tb_pt = s9.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(5.2), Inches(1.8))
    tf_pt = tb_pt.text_frame
    tf_pt.word_wrap = True
    pts_pt = [
        "Harmful instructions can cause serious damage if ordinary programs execute them",
        "Privileged instructions — I/O control, timer, interrupts — allowed only in kernel mode",
        "CPU hardware enforces the mode distinction; user programs cannot bypass it"
    ]
    for pt in pts_pt:
        p = tf_pt.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(3)

    # Left Bottom: 3 Circular Nodes for Illegal Operation Flow
    tb_il = s9.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(5.7), Inches(0.4))
    p_il = tb_il.text_frame.paragraphs[0]
    p_il.text = "Illegal Operation Flow"
    p_il.font.name = FONT_HEADING
    p_il.font.size = Pt(14)
    p_il.font.bold = True
    p_il.font.color.rgb = TEXT_WHITE

    chain_s9 = ["User tries\nprivileged", "CPU generates\ntrap", "OS handles\nviolation"]
    for i, step in enumerate(chain_s9):
        cx = 1.6 + i * 1.8
        add_circular_step(s9, cx, 5.3, 0.55, step, number=i+1, border_color=ACCENT_ROSE if i==1 else CARD_BORDER)

    # Right Column: Timer & OS Control (3 Numbered Cards)
    r_cards_s9 = [
        (1, "The Problem", "A user program could enter an infinite loop and never voluntarily return control to the operating system.", ACCENT_ROSE),
        (2, "The Solution", "A hardware timer interrupts the computer after a specified period — typically every 1–100 milliseconds.", ACCENT_EMERALD),
        (3, "The Outcome", "OS regains CPU control, invokes the scheduler, enforces time-sharing, then resumes the user program.", ACCENT_CYAN)
    ]
    for num, ctitle, cdesc, ccol in r_cards_s9:
        cy = 1.6 + (num - 1) * 1.65
        add_card(s9, 6.8, cy, 5.7, 1.5, ctitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ccol)
        
        num_card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.05), Inches(cy + 0.4), Inches(0.55), Inches(0.55))
        num_card.fill.solid()
        num_card.fill.fore_color.rgb = PILL_BG
        num_card.line.color.rgb = ccol
        num_card.line.width = Pt(1)
        tf_n = num_card.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        p_n.text = str(num)
        p_n.font.name = FONT_HEADING
        p_n.font.size = Pt(14)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_WHITE
        
        tb = s9.shapes.add_textbox(Inches(7.75), Inches(cy + 0.4), Inches(4.6), Inches(0.9))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s9,
        "What prevents a user program from getting stuck in an infinite loop and refusing to yield control? The hardware timer. Before handing the CPU to a user process, the OS configures a timer. As the CPU runs, the timer decrements. When it reaches zero, a hardware interrupt fires, forcing control back to the OS scheduler. This guarantees preemption and makes multitasking possible. That concludes Act II. I now pass to Lochan.",
        "Privileged instruction protection, hardware trap generation, and guaranteed preemption via the hardware interval timer.",
        "I will now pass the presentation to Lochan, who will cover the Memory Hierarchy, I/O systems, Clustered systems, and our final synthesis.",
        "Hand over presentation clicker/focus to Lochan."
    )

    # =========================================================================
    # SLIDE 10: STORAGE HIERARCHY (Lochan)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s10)
    apply_slide_morph_transition(s10)
    add_header(s10, 10, 15, "Act III: Multiprocessors & I/O", "Lochan", "Storage Hierarchy")

    # 3 Column Cards with Icons
    col_w = 3.7
    storage_cards = [
        ("Registers & Cache", "Fastest, most expensive storage. CPU registers are directly inside the processor; L1/L2/L3 cache sits between registers and main memory.\n\nVolatile — data lost on power off.", ACCENT_CYAN, "CPU"),
        ("Main Memory (RAM)", "Programs must be loaded here for execution. Directly accessible by the processor via the memory bus.\n\nVolatile — larger capacity but slower than cache.", ACCENT_EMERALD, "RAM"),
        ("Secondary & Tertiary", "HDDs and NVM devices (SSDs) provide large, nonvolatile capacity.\n\nMagnetic tapes and optical disks serve as tertiary backup storage for special archiving.", ACCENT_INDIGO, "SSD")
    ]
    for i, (stitle, sdesc, scol, sicon) in enumerate(storage_cards):
        sx = 0.8 + i * 4.0
        add_card(s10, sx, 1.6, col_w, 4.4, stitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=scol)
        
        # Top Icon Tag
        icon_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(sx + 0.24), Inches(2.1), Inches(0.9), Inches(0.35))
        icon_box.fill.solid()
        icon_box.fill.fore_color.rgb = PILL_BG
        icon_box.line.color.rgb = scol
        icon_box.line.width = Pt(1)
        p_ic = icon_box.text_frame.paragraphs[0]
        p_ic.alignment = PP_ALIGN.CENTER
        p_ic.text = sicon
        p_ic.font.name = FONT_HEADING
        p_ic.font.size = Pt(10)
        p_ic.font.bold = True
        p_ic.font.color.rgb = scol

        tb = s10.shapes.add_textbox(Inches(sx + 0.24), Inches(2.6), Inches(col_w - 0.45), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = sdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

    # Bottom Full-Width Key Trade-off Banner
    add_bottom_banner(s10, "Faster memory is more expensive per bit. The storage hierarchy balances speed, cost, and capacity across every level.", "Key Trade-off:", ACCENT_CYAN)

    set_speaker_notes(
        s10,
        "Thank you Vedhanth. Hello everyone, I am Lochan, and in Act III we will explore storage hierarchies, I/O systems, and clustered environments. Memory is organized in a strict hierarchy governed by speed, cost, and volatility. At the top, CPU registers and caches offer near-instant access but are small, expensive, and volatile. Main memory is the only large storage the CPU can directly address. Below that, nonvolatile SSDs and hard disks preserve data permanently. The OS must stage data across these tiers efficiently.",
        "Storage hierarchy trade-offs (speed, cost per bit, volatility) and the caching principle.",
        "Now let's examine how the operating system communicates with I/O devices.",
        "Trace the storage pyramid from top to bottom on the diagram."
    )

    # =========================================================================
    # SLIDE 11: I/O STRUCTURE & DMA (Lochan)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s11)
    apply_slide_morph_transition(s11)
    add_header(s11, 11, 15, "Act III: Multiprocessors & I/O", "Lochan", "I/O Structure & Direct Memory Access (DMA)")

    col_w = 3.7
    io_cards = [
        ("Device Controllers", ACCENT_CYAN, [
            ("Dedicated Hardware:", "Hardware unit managing specific device types (disk, keyboard, network)."),
            ("Local Buffers:", "Maintains local buffer storage and control registers for data staging."),
            ("Autonomous:", "Moves data between device and local buffer independently.")
        ]),
        ("Device Drivers", ACCENT_INDIGO, [
            ("Software Interface:", "OS module understanding controller register protocols."),
            ("Uniform Interface:", "Presents a clean, uniform I/O interface to the rest of the OS."),
            ("Register Dispatch:", "Writes command registers to initiate physical I/O.")
        ]),
        ("Direct Memory Access (DMA)", ACCENT_EMERALD, [
            ("High-Speed Devices:", "Essential for high-throughput disk and network interfaces."),
            ("CPU Bypass:", "Transfers whole data blocks directly between buffer and RAM."),
            ("Single Interrupt per Block:", "Generates only one interrupt per block instead of one per byte.")
        ])
    ]
    for i, (ctitle, ccol, citems) in enumerate(io_cards):
        cx = 0.8 + i * 4.0
        add_card(s11, cx, 1.6, col_w, 3.2, ctitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ccol)
        tb = s11.shapes.add_textbox(Inches(cx + 0.24), Inches(2.1), Inches(col_w - 0.45), Inches(2.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (h, b) in enumerate(citems):
            p = tf.add_paragraph() if j > 0 else tf.paragraphs[0]
            p.text = h + " "
            p.font.name = FONT_HEADING
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = ccol
            if j > 0: p.space_before = Pt(4)
            run = p.add_run()
            run.text = b
            run.font.name = FONT_BODY
            run.font.size = Pt(10)
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Full-Width Pipeline Banner
    add_bottom_banner(s11, "Application request → Driver loads registers → Controller stages buffer → DMA block transfer → Interrupt completion.", "I/O Execution Cycle:", ACCENT_EMERALD)

    set_speaker_notes(
        s11,
        "How does the operating system coordinate with I/O devices? Each physical device is managed by a hardware Device Controller with its own local buffer storage. In the OS kernel, a corresponding Device Driver speaks the controller's language. For high-speed block devices like SSDs and network cards, transferring data byte-by-byte through the CPU would cause massive overhead. Direct Memory Access (DMA) transfers entire blocks directly between the controller buffer and RAM, generating only one interrupt per block.",
        "Device Controller, Device Driver, local buffer storage, interrupt-driven I/O, and Direct Memory Access (DMA).",
        "Let's revisit multiprocessor systems and compare Symmetric Multiprocessing with NUMA in depth.",
        "Explain how DMA frees the CPU from byte-by-byte transfer duties."
    )

    # =========================================================================
    # SLIDE 12: MULTIPROCESSOR SYSTEMS: SMP VS NUMA (Lochan)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s12)
    apply_slide_morph_transition(s12)
    add_header(s12, 12, 15, "Act III: Multiprocessors & I/O", "Lochan", "Multiprocessor Systems: SMP vs NUMA")

    # Top Table Card
    add_card(s12, 0.8, 1.6, 11.733, 2.7, "Direct Architectural Comparison: SMP vs NUMA", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    
    rows, cols = 4, 3
    left_t, top_t, width_t, height_t = Inches(1.1), Inches(2.0), Inches(11.1), Inches(2.1)
    tbl_shape = s12.shapes.add_table(rows, cols, left_t, top_t, width_t, height_t)
    table = tbl_shape.table
    table.columns[0].width = Inches(2.8)
    table.columns[1].width = Inches(4.1)
    table.columns[2].width = Inches(4.2)

    table_data = [
        ("Architectural Feature", "Symmetric Multiprocessing (SMP / UMA)", "Non-Uniform Memory Access (NUMA)"),
        ("Memory Access Time", "Uniform access time across all CPUs / cores.", "Non-uniform: Local memory is fast; remote memory is slower."),
        ("System Interconnect", "Single shared system bus connecting all CPUs to RAM.", "Point-to-point interconnect linking distributed nodes."),
        ("Scalability & OS Role", "Scalability limited by shared bus contention.", "Highly scalable; OS must optimize thread memory locality.")
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(35, 42, 60) if r_idx == 0 else RGBColor(22, 26, 38)
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(10.5 if r_idx == 0 else 10)
            p.font.bold = True if r_idx == 0 or c_idx == 0 else False
            p.font.color.rgb = ACCENT_CYAN if r_idx == 0 else (TEXT_WHITE if c_idx == 0 else TEXT_MUTED)

    # Bottom Two Cards: NUMA Trade-off & OS Scheduling
    c_w = 5.7
    add_card(s12, 0.8, 4.5, c_w, 2.2, "The NUMA Latency Trade-Off", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_AMBER)
    tb_u1 = s12.shapes.add_textbox(Inches(1.05), Inches(4.9), Inches(5.2), Inches(1.6))
    tf_u1 = tb_u1.text_frame
    tf_u1.word_wrap = True
    pts_u1 = [
        ("Local Memory Access:", "CPU directly accesses its own attached memory channel at minimum latency."),
        ("Remote Memory Access:", "Accessing memory on another node incurs interconnect delays and increases penalty.")
    ]
    for i, (h, b) in enumerate(pts_u1):
        p = tf_u1.add_paragraph() if i > 0 else tf_u1.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_card(s12, 6.8, 4.5, c_w, 2.2, "OS NUMA Memory & Thread Scheduling", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_EMERALD)
    tb_u2 = s12.shapes.add_textbox(Inches(7.05), Inches(4.9), Inches(5.2), Inches(1.6))
    tf_u2 = tb_u2.text_frame
    tf_u2.word_wrap = True
    pts_u2 = [
        ("Thread Affinity:", "The OS scheduler binds threads to CPU cores physically close to the thread's allocated memory."),
        ("Locality-Aware Allocation:", "Memory managers prioritize allocating physical frames from the local NUMA node.")
    ]
    for i, (h, b) in enumerate(pts_u2):
        p = tf_u2.add_paragraph() if i > 0 else tf_u2.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s12,
        "Comparing SMP and NUMA side-by-side reveals a fundamental engineering trade-off. In pure Symmetric Multiprocessing, all CPUs share a single memory bus. While simple, bus contention caps scalability as processor counts increase. In NUMA, memory is partitioned across processor nodes. While this solves the bus bottleneck, it introduces variable latency: local access is fast, while remote access across the interconnect is slower. The operating system must be NUMA-aware to schedule threads on the same node where their memory lives.",
        "SMP vs NUMA comparison, uniform vs non-uniform memory access, and OS locality-aware scheduling.",
        "Beyond single machines, what happens when we connect independent computer systems together? This brings us to Clustered Systems.",
        "Guide the audience through the comparison table columns."
    )

    # =========================================================================
    # SLIDE 13: CLUSTERED SYSTEMS (Lochan)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s13)
    apply_slide_morph_transition(s13)
    add_header(s13, 13, 15, "Act III: Multiprocessors & I/O", "Lochan", "Clustered Systems Architecture")

    c_w = 5.7
    add_card(s13, 0.8, 1.6, c_w, 4.8, "Clustered Systems Architecture", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_cl1 = s13.shapes.add_textbox(Inches(1.05), Inches(2.1), Inches(5.2), Inches(4.1))
    tf_cl1 = tb_cl1.text_frame
    tf_cl1.word_wrap = True

    pts_cl1 = [
        ("Loosely Coupled Nodes:", "Two or more individual computer systems/nodes connected via a high-speed network or SAN interconnect."),
        ("Shared Storage (SAN):", "Nodes share a Storage Area Network, providing uniform data access across all machines."),
        ("High Availability & Fault Tolerance:", "Failure of any individual node does not interrupt service; remaining nodes take over the workload."),
        ("Asymmetric Clustering:", "One machine runs applications while another remains in hot-standby mode monitoring the active server."),
        ("Symmetric Clustering:", "Multiple nodes run applications concurrently while monitoring each other for failure.")
    ]
    for i, (h, b) in enumerate(pts_cl1):
        p = tf_cl1.add_paragraph() if i > 0 else tf_cl1.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(4)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_card(s13, 6.8, 1.6, c_w, 4.8, "High Availability Mechanics", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    tb_cl2 = s13.shapes.add_textbox(Inches(7.05), Inches(2.1), Inches(5.2), Inches(4.1))
    tf_cl2 = tb_cl2.text_frame
    tf_cl2.word_wrap = True

    pts_cl2 = [
        ("Heartbeat Monitoring:", "Continuous health checks between cluster nodes detect hardware or OS failures in milliseconds."),
        ("Automatic Failover:", "Cluster manager software migrates active database or application state to healthy standby nodes without downtime."),
        ("Parallel Clusters:", "Multiple nodes access shared disks concurrently with distributed lock manager (DLM) synchronization."),
        ("Grid & Cloud Scaling:", "Clustering forms the bedrock of modern cloud computing infrastructures and hyperscale datacenters.")
    ]
    for i, (h, b) in enumerate(pts_cl2):
        p = tf_cl2.add_paragraph() if i > 0 else tf_cl2.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(4)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s13,
        "While multiprocessor systems share a single chassis, Clustered Systems connect two or more independent computers together across a network, typically sharing a Storage Area Network (SAN). We distinguish asymmetric clustering—where one node acts as a hot-standby—and symmetric clustering—where all nodes run applications concurrently while monitoring each other for high availability.",
        "Clustered systems (loosely coupled nodes, shared SAN, asymmetric vs symmetric) and high availability.",
        "Now let's examine diverse computing environments from mobile to cloud.",
        "Contrast clustered scale-out architecture with single-system multi-core scale-up architecture."
    )

    # =========================================================================
    # SLIDE 14: COMPUTING ENVIRONMENTS (Lochan)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s14)
    apply_slide_morph_transition(s14)
    add_header(s14, 14, 15, "Act III: Multiprocessors & I/O", "Lochan", "Diverse Computing Environments")

    # 4 Card Grid (2x2)
    grid_cards = [
        ("Traditional / Desktop Computing", "Standard PCs, workstations, and dedicated file servers running general-purpose multitasking operating systems with rich UI frameworks.", ACCENT_CYAN),
        ("Mobile Computing", "Smartphones and tablets with power-constrained architectures, touch/sensor interfaces, and wireless communications (iOS/Android).", ACCENT_INDIGO),
        ("Distributed Systems", "Networked collection of physically separate computational nodes presenting a single unified computing system to users.", ACCENT_EMERALD),
        ("Cloud & Real-Time Computing", "Virtualized compute/storage delivered on-demand via massive server clusters, alongside embedded deterministic real-time systems.", ACCENT_AMBER)
    ]
    for i, (gtitle, gdesc, gcol) in enumerate(grid_cards):
        gx = 0.8 if i % 2 == 0 else 6.8
        gy = 1.6 if i < 2 else 4.2
        add_card(s14, gx, gy, 5.7, 2.3, gtitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=gcol)
        tb = s14.shapes.add_textbox(Inches(gx + 0.25), Inches(gy + 0.55), Inches(5.2), Inches(1.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = gdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

    set_speaker_notes(
        s14,
        "Computer architecture principles apply across a wide spectrum of environments: traditional desktop PCs, power-sensitive mobile smartphones, networked distributed systems, cloud computing platforms, and embedded real-time systems. In every case, the operating system controls hardware execution and resource allocation.",
        "Overview of computing environment categories (Traditional, Mobile, Distributed, Cloud, Real-Time).",
        "Now let's bring our entire presentation together into our final synthesis and key takeaways.",
        "Summarize the spectrum from embedded IoT to hyperscale cloud."
    )

    # =========================================================================
    # SLIDE 15: MASTER SYNTHESIS & PRESENTERS (All 3 Presenters)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s15)
    apply_slide_morph_transition(s15)
    add_header(s15, 15, 15, "Synthesis & Conclusion", "V. Ram Charan · Vedhanth · Lochan", "Key Takeaways")

    # 5 Numbered Capsule Cards in a Grid matching Gamma Screenshot 11!
    capsules_top = [
        (1, "System Organization", "CPUs, device controllers, and shared memory cooperate via a common bus — concurrency drives the need for OS coordination.", ACCENT_CYAN),
        (2, "Interrupts", "The fundamental mechanism for hardware–OS communication; interrupt vectors and priority levels enable efficient, ordered response.", ACCENT_INDIGO),
        (3, "Dual-Mode Operation", "User mode and kernel mode — enforced by a hardware mode bit — protect the OS and users from erroneous or malicious programs.", ACCENT_ROSE),
        (4, "Multicore & SMP", "Multiple cores on one chip deliver throughput gains with lower power; speed-up with N processors is always less than N.", ACCENT_AMBER)
    ]
    c_w4 = 2.75
    for num, ctitle, cdesc, ccol in capsules_top:
        cx = 0.8 + (num - 1) * 3.0
        add_card(s15, cx, 1.6, c_w4, 2.7, ctitle, border_color=CARD_BORDER, bg_color=CARD_BG)
        
        num_badge = s15.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx + c_w4/2 - 0.25), Inches(1.4), Inches(0.5), Inches(0.5))
        num_badge.fill.solid()
        num_badge.fill.fore_color.rgb = PILL_BG
        num_badge.line.color.rgb = ccol
        num_badge.line.width = Pt(1.5)
        p_nb = num_badge.text_frame.paragraphs[0]
        p_nb.alignment = PP_ALIGN.CENTER
        p_nb.text = str(num)
        p_nb.font.name = FONT_HEADING
        p_nb.font.size = Pt(12)
        p_nb.font.bold = True
        p_nb.font.color.rgb = TEXT_WHITE

        tb = s15.shapes.add_textbox(Inches(cx + 0.15), Inches(2.0), Inches(c_w4 - 0.3), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = cdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Middle Row: 5th Wide Capsule Card (Storage Hierarchy)
    add_card(s15, 0.8, 4.6, 11.733, 1.0, "Storage Hierarchy", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_EMERALD)
    num_badge5 = s15.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8 + 11.733/2 - 0.25), Inches(4.4), Inches(0.5), Inches(0.5))
    num_badge5.fill.solid()
    num_badge5.fill.fore_color.rgb = PILL_BG
    num_badge5.line.color.rgb = ACCENT_EMERALD
    num_badge5.line.width = Pt(1.5)
    p_nb5 = num_badge5.text_frame.paragraphs[0]
    p_nb5.alignment = PP_ALIGN.CENTER
    p_nb5.text = "5"
    p_nb5.font.name = FONT_HEADING
    p_nb5.font.size = Pt(12)
    p_nb5.font.bold = True
    p_nb5.font.color.rgb = TEXT_WHITE

    tb_5 = s15.shapes.add_textbox(Inches(1.1), Inches(4.9), Inches(11.2), Inches(0.6))
    tf_5 = tb_5.text_frame
    tf_5.word_wrap = True
    p5 = tf_5.paragraphs[0]
    p5.text = "Speed, cost, and capacity trade-offs define a hierarchy from registers to tertiary storage — the OS manages movement across all levels."
    p5.font.name = FONT_BODY
    p5.font.size = Pt(10.5)
    p5.font.color.rgb = TEXT_MUTED

    # Bottom Row: 3 Presenter Cards
    pres_cards = [
        ("V. Ram Charan", "Slides 1–5 · Act I", ACCENT_CYAN),
        ("Vedhanth", "Slides 6–10 · Act II", ACCENT_INDIGO),
        ("Lochan", "Slides 11–15 · Act III", ACCENT_EMERALD)
    ]
    p_w = 3.7
    for i, (name, act_info, col) in enumerate(pres_cards):
        px = 0.8 + i * 4.0
        add_card(s15, px, 5.8, p_w, 1.2, name, border_color=CARD_BORDER, bg_color=PILL_BG, accent_bar=col)
        tb = s15.shapes.add_textbox(Inches(px + 0.2), Inches(6.25), Inches(p_w - 0.4), Inches(0.6))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = act_info
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = col

    set_speaker_notes(
        s15,
        "To conclude our presentation: Users execute applications; applications request operating system services; the OS manages memory, processes, and I/O; and underlying hardware executes instructions under dual-mode protection. The five core takeaways are: system organization requires concurrency coordination, interrupts enable efficient communication, dual-mode operation protects the kernel, multicore delivers scalable parallelism, and storage hierarchies balance speed and capacity. On behalf of Ram Charan, Vedhanth, and myself, thank you for your attention. We are now open for questions.",
        "Complete architectural synthesis: hardware resources, OS dual role, interrupt-driven operation, and hardware protection.",
        "End of presentation — open floor for Q&A.",
        "All three presenters step forward together, smile, and invite questions from the professor and classmates."
    )

    out_pptx = os.path.join(ROOT_DIR, "computer_system_architecture.pptx")
    prs.save(out_pptx)
    out_pptx_clean = os.path.join(ROOT_DIR, "Computer_System_Architecture_OS.pptx")
    prs.save(out_pptx_clean)
    out_pptx_cinematic = os.path.join(ROOT_DIR, "Computer_System_Architecture_Cinematic.pptx")
    prs.save(out_pptx_cinematic)
    print(f"Successfully generated 15-slide Luxury Gamma/Envato-style presentation with Morph transitions & lighting effects!")
    return out_pptx

if __name__ == "__main__":
    build_presentation()
