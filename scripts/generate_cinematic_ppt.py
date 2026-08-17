"""
scripts/generate_cinematic_ppt.py
Generates a luxury 15-slide PowerPoint deck for Computer System Architecture (OS Course).

Content Structure & Speaker Allocation:
- Act I (Slides 1-5): V. Ram Charan — Core Hardware & System Bus (CPU, RAM, I/O, 3-Part Bus, Interrupts & DMA)
- Act II (Slides 6-10): Vedhanth — Memory & Storage Hierarchy (Speed/Cost/Capacity, Tiers, Locality, Volatility, OS Memory Management)
- Act III (Slides 11-15): Lochan — Multiprocessing & Modern Systems (Single vs Multiprocessor, SMP vs AMP, Multicore & Clustered, OS Challenges)
- Slide 15: Grand Synthesis & Conclusion (V. Ram Charan · Vedhanth · Lochan)
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
os.makedirs(GAMMA_DIR, exist_ok=True)

# Color Palette: Envato / Gamma Luxury Tech Minimalist
BG_CARBON       = RGBColor(18, 20, 28)     # #12141C - Deep Obsidian/Carbon
CARD_BG         = RGBColor(26, 30, 42)     # #1A1E2A - Frosted Glass Card
CARD_HIGHLIGHT  = RGBColor(38, 45, 64)     # #262D40 - Hover / Active Container
CARD_BORDER     = RGBColor(46, 54, 74)     # #2E364A - Subtle Glass Border
CARD_BORDER_GLOW= RGBColor(56, 189, 248)   # #38BDF8 - Ice Cyan Accent Glow
PILL_BG         = RGBColor(30, 36, 52)     # #1E2434 - Pill / Tag Container

TEXT_WHITE      = RGBColor(255, 255, 255)  # #FFFFFF - Crisp Title White
TEXT_MUTED      = RGBColor(160, 175, 200)  # #A0AFC8 - Secondary Slate
TEXT_DIM        = RGBColor(110, 125, 150)  # #6E7D96 - Tertiary Annotation

ACCENT_CYAN     = RGBColor(56, 189, 248)   # #38BDF8 - Act I Cyan
ACCENT_INDIGO   = RGBColor(129, 140, 248)  # #818CF8 - Act II Indigo
ACCENT_EMERALD  = RGBColor(52, 211, 153)   # #34D399 - Act III Emerald
ACCENT_AMBER    = RGBColor(245, 158, 11)   # #F59E0B - Warning / Highlight Amber
ACCENT_ROSE     = RGBColor(244, 63, 94)    # #F43F5E - Trap / Fault Rose

FONT_HEADING    = "Segoe UI"
FONT_BODY       = "Segoe UI"

def set_slide_backdrop(slide):
    """Sets a solid deep carbon background."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_CARBON

def apply_slide_morph_transition(slide, duration_ms=800):
    """Adds valid ECMA-376 OpenXML Morph & Smooth Fade transition elements after cSld."""
    try:
        # Standard OpenXML Morph transition with fallback smooth duration
        transition_xml = f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:morph option="byObject"/></p:transition>'
        new_trans = parse_xml(transition_xml)
        for child in list(slide._element):
            if child.tag.endswith('transition'):
                slide._element.remove(child)
        slide._element.append(new_trans)
    except Exception as e:
        print(f"Warning: Transition XML could not be appended: {e}")

def add_header(slide, slide_num, total_slides, act_title, speaker_name, title, subtitle=None):
    """Standardized top header bar across all slides."""
    # Top Left Act Pill
    act_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.2), Inches(0.34))
    act_box.fill.solid()
    act_box.fill.fore_color.rgb = PILL_BG
    act_box.line.color.rgb = CARD_BORDER
    act_box.line.width = Pt(1)
    tf_act = act_box.text_frame
    tf_act.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_act = tf_act.paragraphs[0]
    p_act.text = act_title.upper()
    p_act.font.name = FONT_HEADING
    p_act.font.size = Pt(8.5)
    p_act.font.bold = True
    p_act.font.color.rgb = ACCENT_CYAN
    p_act.alignment = PP_ALIGN.CENTER

    # Presenter Pill
    spk_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.1), Inches(0.4), Inches(3.2), Inches(0.34))
    spk_box.fill.solid()
    spk_box.fill.fore_color.rgb = PILL_BG
    spk_box.line.color.rgb = CARD_BORDER
    spk_box.line.width = Pt(1)
    tf_spk = spk_box.text_frame
    tf_spk.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_spk = tf_spk.paragraphs[0]
    p_spk.text = f"PRESENTER: {speaker_name.upper()}"
    p_spk.font.name = FONT_HEADING
    p_spk.font.size = Pt(8.5)
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

    if corner_accent:
        tick = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left + width - 0.15), Inches(top + 0.08), Inches(0.08), Inches(0.08))
        tick.fill.solid()
        tick.fill.fore_color.rgb = accent_bar if accent_bar else CARD_BORDER_GLOW
        tick.line.fill.background()

    if accent_bar:
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top + 0.15), Inches(0.04), Inches(height - 0.3))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_bar
        bar.line.fill.background()

    if title:
        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.15), Inches(width - 0.5), Inches(0.4))
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

def add_bottom_banner(slide, text, tag="Key Principle:", tag_color=ACCENT_CYAN):
    """Adds a full-width bottom summary banner."""
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.55), Inches(11.733), Inches(0.55))
    box.fill.solid()
    box.fill.fore_color.rgb = PILL_BG
    box.line.color.rgb = CARD_BORDER
    box.line.width = Pt(1)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.2)
    tf.margin_top = Inches(0.08)
    p = tf.paragraphs[0]
    p.text = f"{tag} "
    p.font.name = FONT_HEADING
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = tag_color
    run = p.add_run()
    run.text = text
    run.font.name = FONT_BODY
    run.font.size = Pt(10)
    run.font.bold = False
    run.font.color.rgb = TEXT_WHITE

def add_bullet_list(slide, left, top, width, height, items, font_size=10.5):
    """Adds formatted bullet items into a card."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_before = Pt(4) if idx > 0 else Pt(0)
        p.font.name = FONT_BODY
        p.font.size = Pt(font_size)
        p.font.color.rgb = TEXT_MUTED

        if ":" in item:
            parts = item.split(":", 1)
            p.text = "• " + parts[0] + ":"
            p.font.bold = True
            p.font.color.rgb = TEXT_WHITE
            run = p.add_run()
            run.text = parts[1]
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED
        else:
            p.text = "• " + item

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
    p2.text = "Core Hardware, Storage Hierarchies & Modern Multiprocessing"
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

    presenters = [
        ("V. Ram Charan", "Act I Lead — Core Hardware & System Bus", ACCENT_CYAN),
        ("Vedhanth", "Act II Lead — Memory & Storage Hierarchy", ACCENT_INDIGO),
        ("Lochan", "Act III Lead — Multiprocessing & Modern Architectures", ACCENT_EMERALD)
    ]
    for i, (name, role, col) in enumerate(presenters):
        py = 3.3 + i * 0.95
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

    mb_img = os.path.join(GAMMA_DIR, "iso_motherboard.png")
    if os.path.exists(mb_img):
        s1.shapes.add_picture(mb_img, Inches(7.2), Inches(1.3), width=Inches(5.4))

    set_speaker_notes(
        s1,
        "Good morning everyone. I’ll be explaining the core hardware of a computer system. Together with Vedhanth and Lochan, we will walk you through how hardware components communicate, how memory hierarchies optimize speed and capacity, and how modern multiprocessing systems scale concurrent execution.",
        "Computer system architecture establishes the hardware foundation for operating system process management, memory allocation, and I/O handling.",
        "Let us begin with Slide 2 by examining the three fundamental hardware pillars: the CPU, main memory, and I/O devices.",
        "Stand center, introduce team members, gesture to the presenter cards."
    )

    # =========================================================================
    # SLIDE 2: THE THREE FUNDAMENTAL HARDWARE PILLARS (V. Ram Charan)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s2)
    apply_slide_morph_transition(s2)
    add_header(s2, 2, 15, "Act I: Core Hardware", "V. Ram Charan", "The Three Fundamental Hardware Pillars", "The CPU, Main Memory & I/O Devices Powering Computation")

    pillars = [
        ("The CPU (Processor)", "Fetch, Decode, Execute", [
            "Responsible for fetching, decoding, and executing instructions.",
            "Contains Arithmetic Logic Unit (ALU), Control Unit (CU), and high-speed registers.",
            "Coordinates calculations and directs binary program flow."
        ], ACCENT_CYAN),
        ("Main Memory (RAM)", "Active Program Workspace", [
            "Stores the data and programs that are currently being used.",
            "The only large storage medium directly accessible and executable by the CPU.",
            "Volatile working area holding active instructions."
        ], ACCENT_INDIGO),
        ("I/O Devices", "Peripherals & External Bridge", [
            "Helps the computer communicate with the outside world.",
            "Includes storage drives, displays, input devices, and network cards.",
            "Managed by dedicated hardware device controllers."
        ], ACCENT_EMERALD)
    ]
    card_w = 3.65
    for i, (p_title, p_sub, p_items, col) in enumerate(pillars):
        px = 0.8 + i * 4.05
        add_card(s2, px, 1.8, card_w, 4.45, p_title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb_sub = s2.shapes.add_textbox(Inches(px + 0.25), Inches(2.25), Inches(card_w - 0.5), Inches(0.35))
        p_s = tb_sub.text_frame.paragraphs[0]
        p_s.text = p_sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(9.5)
        p_s.font.bold = True
        p_s.font.color.rgb = col
        add_bullet_list(s2, px + 0.25, 2.7, card_w - 0.5, 3.3, p_items, font_size=10.5)

    add_bottom_banner(s2, "The CPU executes instructions, Main Memory provides active storage, and I/O Devices bridge external communication.", "Hardware Core:", ACCENT_CYAN)

    set_speaker_notes(
        s2,
        "Good morning everyone. I’ll be explaining the core hardware of a computer system. A computer system mainly consists of three parts: the CPU, main memory, and I/O devices. The CPU is responsible for fetching, decoding, and executing instructions. Main memory stores the data and programs that are currently being used, while I/O devices help the computer communicate with the outside world.",
        "The CPU, RAM, and I/O form the triad of computer architecture; the CPU cannot run code that is not first loaded into main memory.",
        "Now let's examine how these three components communicate with each other over the system bus.",
        "Point to the 3 distinct cards highlighting CPU, Main Memory, and I/O Devices."
    )

    # =========================================================================
    # SLIDE 3: THE SYSTEM BUS ARCHITECTURE (V. Ram Charan)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s3)
    apply_slide_morph_transition(s3)
    add_header(s3, 3, 15, "Act I: Core Hardware", "V. Ram Charan", "The System Bus Architecture", "Three Specialized High-Speed Communication Channels")

    buses = [
        ("1. Address Bus", "Tells WHERE the data should go by carrying memory addresses and I/O port targets (Unidirectional from CPU/DMA).", ACCENT_CYAN),
        ("2. Data Bus", "Carries the ACTUAL DATA and binary instructions between CPU, memory, and controllers (Bidirectional).", ACCENT_INDIGO),
        ("3. Control Bus", "Carries CONTROL SIGNALS and timing clocks — Read/Write commands, Interrupt requests, and ACKs (Bidirectional).", ACCENT_EMERALD)
    ]
    for i, (btitle, bdesc, bcol) in enumerate(buses):
        by = 1.8 + i * 1.45
        add_card(s3, 0.8, by, 5.8, 1.3, btitle, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=bcol)
        tb = s3.shapes.add_textbox(Inches(1.05), Inches(by + 0.45), Inches(5.3), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = bdesc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    bus_img = os.path.join(GAMMA_DIR, "iso_system_bus.png")
    if os.path.exists(bus_img):
        s3.shapes.add_picture(bus_img, Inches(7.0), Inches(1.5), width=Inches(5.5))

    add_bottom_banner(s3, "These three buses work synchronously to coordinate all instruction fetching, operand reads, and device data transfers.", "System Bus Synchronization:", ACCENT_CYAN)

    set_speaker_notes(
        s3,
        "These components communicate through a system bus, which has three parts: the address bus, which tells where the data should go; the data bus, which carries the actual data; and the control bus, which carries control signals.",
        "The system bus connects CPU, memory, and I/O controllers; bus width determines addressable memory limits and throughput bandwidth.",
        "Next, let's look at two critical concepts in hardware communication: Interrupts and DMA.",
        "Trace the Address, Data, and Control lines on the diagram."
    )

    # =========================================================================
    # SLIDE 4: INTERRUPTS & DMA (V. Ram Charan)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s4)
    apply_slide_morph_transition(s4)
    add_header(s4, 4, 15, "Act I: Core Hardware", "V. Ram Charan", "Hardware Communication: Interrupts & DMA", "Asynchronous Event Signaling & High-Speed Memory Transfers")

    add_card(s4, 0.8, 1.8, 5.7, 4.45, "Interrupt Mechanism (Event Signaling)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    int_points = [
        "CPU Attention: Allow devices to get the CPU’s attention when they need it.",
        "Eliminates Polling: Eliminates constant CPU polling loops, freeing execution time.",
        "Vector Lookup: CPU pushes state and branches immediately to the Interrupt Service Routine (ISR).",
        "Context Restoration: Automatically restores user execution context upon completion."
    ]
    add_bullet_list(s4, 1.05, 2.4, 5.2, 3.6, int_points, font_size=11)

    add_card(s4, 6.8, 1.8, 5.7, 4.45, "Direct Memory Access (DMA)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_EMERALD)
    dma_points = [
        "Direct RAM Transfer: Allows devices to transfer data directly to memory without making the CPU handle every piece of data.",
        "High-Speed Channel: Essential for disk controllers, NVMe SSDs, and Gigabit network interfaces.",
        "Block Efficiency: Emits only 1 interrupt per entire block rather than 1 per byte.",
        "CPU Offload: CPU computes freely in parallel while memory transfers complete."
    ]
    add_bullet_list(s4, 7.05, 2.4, 5.2, 3.6, dma_points, font_size=11)

    add_bottom_banner(s4, "Interrupts signal events asynchronously; DMA offloads bulk data transfers to prevent CPU bottlenecks.", "Communication Synergy:", ACCENT_CYAN)

    set_speaker_notes(
        s4,
        "Two important concepts are interrupts and DMA. Interrupts allow devices to get the CPU’s attention when they need it. DMA allows devices to transfer data directly to memory without making the CPU handle every piece of data.",
        "Interrupts eliminate busy-wait polling overhead; DMA offloads byte-by-byte data transfer from the CPU.",
        "Let us summarize how core hardware components integrate before moving to memory hierarchy.",
        "Contrast the event-driven signal flow of interrupts with the high-throughput block stream of DMA."
    )

    # =========================================================================
    # SLIDE 5: ACT I SUMMARY (V. Ram Charan)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s5)
    apply_slide_morph_transition(s5)
    add_header(s5, 5, 15, "Act I: Core Hardware", "V. Ram Charan", "Act I Summary: Core Hardware Integration", "Cohesive Operation Across Processor, Memory, Bus & Controllers")

    cards_s5 = [
        ("1. Triad Hardware Organization", "The CPU fetches, decodes, and executes. Main memory holds active programs. I/O devices bridge communication with the outside world.", ACCENT_CYAN),
        ("2. Tri-Bus Highway", "The Address Bus tells where data goes, the Data Bus carries actual data, and the Control Bus delivers read/write synchronization.", ACCENT_INDIGO),
        ("3. Efficient Signaling", "Interrupts allow devices to alert the CPU on demand, while DMA streams bulk data directly to memory without CPU overhead.", ACCENT_EMERALD)
    ]
    for i, (title, desc, col) in enumerate(cards_s5):
        px = 0.8 + i * 4.05
        add_card(s5, px, 1.8, 3.65, 3.4, title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb = s5.shapes.add_textbox(Inches(px + 0.25), Inches(2.4), Inches(3.15), Inches(2.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

    add_card(s5, 0.8, 5.4, 11.733, 0.9, "Act Handover: To Vedhanth for Act II", border_color=CARD_BORDER, bg_color=PILL_BG, accent_bar=ACCENT_INDIGO)
    tb_h = s5.shapes.add_textbox(Inches(1.05), Inches(5.8), Inches(11.2), Inches(0.4))
    p_h = tb_h.text_frame.paragraphs[0]
    p_h.text = "Next: Vedhanth will cover the Memory and Storage Hierarchy, Locality of Reference, Volatility, and OS Caching Techniques."
    p_h.font.name = FONT_BODY
    p_h.font.size = Pt(10.5)
    p_h.font.color.rgb = TEXT_WHITE

    add_bottom_banner(s5, "CPUs, Memory, and I/O work synchronously via buses, utilizing interrupts and DMA for efficient data transfer.", "Core Hardware Integration:", ACCENT_CYAN)

    set_speaker_notes(
        s5,
        "That’s the basic idea of how the hardware components communicate. Now I’ll hand it over to explain memory and storage hierarchy.",
        "Hardware components form a tightly synchronized system coordinated by the system bus, interrupts, and DMA.",
        "Pass presentation to Vedhanth for Act II.",
        "Hand over clicker to Vedhanth."
    )

    # =========================================================================
    # SLIDE 6: BALANCING SPEED, COST, AND CAPACITY (Vedhanth)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s6)
    apply_slide_morph_transition(s6)
    add_header(s6, 6, 15, "Act II: Memory & Storage", "Vedhanth", "Balancing Speed, Cost, and Capacity", "Memory and Storage Hierarchy Overview")

    add_card(s6, 0.8, 1.8, 5.8, 1.3, "The Fundamental Trade-off", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    tb_t = s6.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.3), Inches(0.75))
    p = tb_t.text_frame.paragraphs[0]
    p.text = "Faster memory is usually smaller and more expensive, while slower memory can provide much larger capacity."
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    add_card(s6, 0.8, 3.25, 5.8, 1.3, "High-Speed Tier (Top of Pyramid)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_t1 = s6.shapes.add_textbox(Inches(1.05), Inches(3.7), Inches(5.3), Inches(0.75))
    p = tb_t1.text_frame.paragraphs[0]
    p.text = "Registers and CPU caches provide sub-nanosecond access speeds to keep the execution pipeline fed."
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    add_card(s6, 0.8, 4.65, 5.8, 1.4, "High-Capacity Tier (Bottom of Pyramid)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_AMBER)
    tb_t2 = s6.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(5.3), Inches(0.85))
    p = tb_t2.text_frame.paragraphs[0]
    p.text = "Main memory and secondary storage (SSDs/HDDs) provide gigabytes to terabytes of storage at low cost per bit."
    p.font.name = FONT_BODY
    p.font.size = Pt(10)
    p.font.color.rgb = TEXT_MUTED

    pyr_img = os.path.join(GAMMA_DIR, "iso_storage_pyramid.png")
    if os.path.exists(pyr_img):
        s6.shapes.add_picture(pyr_img, Inches(7.0), Inches(1.5), width=Inches(5.5))

    add_bottom_banner(s6, "Faster memory is smaller and expensive; slower storage is large and economical. The hierarchy balances both.", "The Trade-off:", ACCENT_CYAN)

    set_speaker_notes(
        s6,
        "Now I’ll explain memory and storage hierarchy. Computers use different types of memory because faster memory is usually smaller and more expensive, while slower memory can provide much larger capacity.",
        "Trade-off between access latency, cost per bit, and storage capacity across the memory hierarchy.",
        "Let us examine each tier of the hierarchy from internal registers down to secondary storage.",
        "Trace the pyramid from top (Registers/Cache) to bottom (RAM/SSD)."
    )

    # =========================================================================
    # SLIDE 7: THE HIERARCHY TIERS (Vedhanth)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s7)
    apply_slide_morph_transition(s7)
    add_header(s7, 7, 15, "Act II: Memory & Storage", "Vedhanth", "The Hierarchy Tiers", "From Internal CPU Registers Down to Secondary Mass Storage")

    tiers = [
        ("1. Registers", "Fastest & Smallest", "< 1 ns", "Bytes", "The fastest and smallest storage inside the CPU holding immediate operands.", ACCENT_CYAN),
        ("2. Cache (SRAM)", "High-Speed Buffer", "1 – 10 ns", "Megabytes", "High-speed SRAM buffering active data and frequent instructions.", ACCENT_INDIGO),
        ("3. RAM (DRAM)", "Primary Workspace", "50 – 100 ns", "Gigabytes", "Main workspace for running programs and active operating system buffers.", ACCENT_EMERALD),
        ("4. Secondary Storage", "Mass Storage", "10 μs – 10 ms", "Terabytes", "SSDs and hard disks for massive capacity, retaining data permanently.", ACCENT_AMBER)
    ]
    tw = 2.7
    for i, (t_title, t_sub, t_spd, t_cap, t_desc, col) in enumerate(tiers):
        tx = 0.8 + i * 3.0
        add_card(s7, tx, 1.8, tw, 4.45, t_title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb_meta = s7.shapes.add_textbox(Inches(tx + 0.2), Inches(2.3), Inches(tw - 0.4), Inches(0.9))
        tf_m = tb_meta.text_frame
        p1 = tf_m.paragraphs[0]
        p1.text = t_sub
        p1.font.name = FONT_BODY
        p1.font.size = Pt(9.5)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = tf_m.add_paragraph()
        p2.text = f"Speed: {t_spd} | Cap: {t_cap}"
        p2.font.name = FONT_BODY
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = TEXT_DIM
        
        tb_d = s7.shapes.add_textbox(Inches(tx + 0.2), Inches(3.3), Inches(tw - 0.4), Inches(2.8))
        tf_d = tb_d.text_frame
        tf_d.word_wrap = True
        p = tf_d.paragraphs[0]
        p.text = t_desc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    add_bottom_banner(s7, "Registers (<1ns) → Cache (1-10ns) → RAM (~100ns) → Secondary SSD/HDD (~10ms).", "Latency Spectrum:", ACCENT_CYAN)

    set_speaker_notes(
        s7,
        "The hierarchy starts with registers, which are the fastest and smallest, followed by cache, RAM, and finally secondary storage such as SSDs and hard disks.",
        "Step-by-step characteristics of Registers, Cache (SRAM), Main Memory (DRAM), and Secondary Storage (NVM/Disks).",
        "Next, why does caching work so effectively? Let's look at the Locality of Reference.",
        "Point to the 4 columns from fastest (Registers) to largest (Secondary Storage)."
    )

    # =========================================================================
    # SLIDE 8: LOCALITY OF REFERENCE (Vedhanth)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s8)
    apply_slide_morph_transition(s8)
    add_header(s8, 8, 15, "Act II: Memory & Storage", "Vedhanth", "Locality of Reference", "Temporal and Spatial Behavioral Principles")

    add_card(s8, 0.8, 1.8, 5.7, 4.45, "Temporal Locality (Locality in Time)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    temp_pts = [
        "Core Rule: Data used recently is likely to be used again soon.",
        "Program Examples: Loop counters, repeated subroutine calls, stack frame pointers.",
        "Caching Impact: Keeping recently referenced memory blocks in fast cache produces high hit rates (>90%)."
    ]
    add_bullet_list(s8, 1.05, 2.4, 5.2, 3.6, temp_pts, font_size=11)

    add_card(s8, 6.8, 1.8, 5.7, 4.45, "Spatial Locality (Locality in Space)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    spat_pts = [
        "Core Rule: Data near recently used data is likely to be needed next.",
        "Program Examples: Sequential instruction streams, contiguous array element traversals.",
        "Caching Impact: Fetching complete cache lines (64 bytes) rather than single words drastically cuts memory stalls."
    ]
    add_bullet_list(s8, 7.05, 2.4, 5.2, 3.6, spat_pts, font_size=11)

    add_bottom_banner(s8, "Cache succeeds because programs exhibit strong temporal (time) and spatial (space) locality.", "Locality Axiom:", ACCENT_CYAN)

    set_speaker_notes(
        s8,
        "Cache is important because programs usually show locality of reference. Temporal locality means that data used recently is likely to be used again soon. Spatial locality means that data near recently used data is likely to be needed next.",
        "Temporal locality (reuse in time) and Spatial locality (adjacency in space) are the core reasons caching succeeds.",
        "Now let's examine the difference between volatile and non-volatile storage.",
        "Highlight the contrast between loop re-execution (Temporal) and sequential array scans (Spatial)."
    )

    # =========================================================================
    # SLIDE 9: MEMORY VOLATILITY (Vedhanth)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s9)
    apply_slide_morph_transition(s9)
    add_header(s9, 9, 15, "Act II: Memory & Storage", "Vedhanth", "Memory Volatility", "Volatile Working Storage vs. Non-Volatile Permanent Retention")

    add_card(s9, 0.8, 1.8, 5.7, 4.45, "Volatile Memory (RAM & Caches)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_ROSE)
    vol_pts = [
        "Power Dependent: RAM is volatile, meaning it loses its contents when power is turned off.",
        "Physical Implementation: Uses capacitor charges (DRAM) or transistor latches (SRAM).",
        "System Role: High-speed temporary workspace for running processes and active kernel buffers."
    ]
    add_bullet_list(s9, 1.05, 2.4, 5.2, 3.6, vol_pts, font_size=11)

    add_card(s9, 6.8, 1.8, 5.7, 4.45, "Non-Volatile Storage (SSDs & Hard Disks)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_EMERALD)
    nvol_pts = [
        "Power Independent: SSDs and hard disks are non-volatile, so they retain data even without power.",
        "Physical Implementation: Uses NAND flash floating gates or magnetic platters.",
        "System Role: Long-term permanent storage preserving operating system files, applications, and user data."
    ]
    add_bullet_list(s9, 7.05, 2.4, 5.2, 3.6, nvol_pts, font_size=11)

    add_bottom_banner(s9, "Volatile RAM provides rapid runtime execution; Non-Volatile SSDs/HDDs guarantee permanent data persistence.", "Volatility Distinction:", ACCENT_CYAN)

    set_speaker_notes(
        s9,
        "RAM is volatile, meaning it loses its contents when power is turned off. SSDs and hard disks are non-volatile, so they retain data even without power.",
        "Volatile working RAM vs Non-volatile secondary storage (SSDs/HDDs) and the role of permanent file storage.",
        "Next, how does the Operating System manage this entire storage hierarchy efficiently?",
        "Emphasize that volatile RAM provides execution speed while non-volatile SSDs provide data permanence."
    )

    # =========================================================================
    # SLIDE 10: OS MEMORY MANAGEMENT (Vedhanth)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s10)
    apply_slide_morph_transition(s10)
    add_header(s10, 10, 15, "Act II: Memory & Storage", "Vedhanth", "OS Memory Management", "Software Strategies for Maximizing Storage Hierarchy Performance")

    os_tech = [
        ("1. Paging", "Divides memory into fixed-size pages and maps virtual addresses to physical RAM frames, swapping inactive pages to disk.", ACCENT_CYAN),
        ("2. Buffering", "Temporarily holds data in memory during device transfers to bridge speed mismatches between CPU and slower I/O peripherals.", ACCENT_INDIGO),
        ("3. Disk Caching", "Maintains copies of frequently accessed file system blocks in RAM to avoid slow physical disk read operations.", ACCENT_EMERALD),
        ("4. Prefetching", "Anticipates future memory and file requests based on spatial locality, loading data into cache/RAM before requested.", ACCENT_AMBER)
    ]
    for i, (title, desc, col) in enumerate(os_tech):
        col_idx = i % 2
        row_idx = i // 2
        px = 0.8 + col_idx * 6.0
        py = 1.8 + row_idx * 2.25
        add_card(s10, px, py, 5.7, 2.1, title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb = s10.shapes.add_textbox(Inches(px + 0.25), Inches(py + 0.5), Inches(5.2), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    add_bottom_banner(s10, "Techniques Used: Paging, buffering, disk caching, and prefetching.", "OS Hierarchy Management:", ACCENT_CYAN)

    set_speaker_notes(
        s10,
        "The OS uses techniques such as paging, buffering, disk caching, and prefetching to use this hierarchy efficiently. Now Lochan will take over to discuss multiprocessing.",
        "Operating system storage management techniques: Paging, Buffering, Disk Caching, and Prefetching.",
        "I will now pass the presentation to Lochan, who will explain multiprocessing, modern multicore systems, and OS challenges.",
        "Hand over clicker to Lochan."
    )

    # =========================================================================
    # SLIDE 11: SINGLE-PROCESSOR VS MULTIPROCESSOR (Lochan)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s11)
    apply_slide_morph_transition(s11)
    add_header(s11, 11, 15, "Act III: Multiprocessing", "Lochan", "Single-Processor vs. Multiprocessor Systems", "Architectural Scaling from Single Execution Streams to Parallel Computing")

    add_card(s11, 0.8, 1.8, 5.8, 2.15, "Single-Processor Systems", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    sp_pts = [
        "One CPU handles all instructions.",
        "Simpler hardware design, but limited computational throughput.",
        "Concurrency is simulated purely via OS time-slicing."
    ]
    add_bullet_list(s11, 1.05, 2.3, 5.3, 1.5, sp_pts, font_size=10)

    add_card(s11, 0.8, 4.1, 5.8, 2.15, "Multiprocessor Systems", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    mp_pts = [
        "Multiple CPUs share the bus, clock, and memory.",
        "Runs concurrent workloads to increase speed and reliability.",
        "Provides higher throughput and graceful degradation (fault tolerance)."
    ]
    add_bullet_list(s11, 1.05, 4.6, 5.3, 1.5, mp_pts, font_size=10)

    tree_img = os.path.join(GAMMA_DIR, "single_vs_multi_tree.png")
    if os.path.exists(tree_img):
        s11.shapes.add_picture(tree_img, Inches(7.0), Inches(1.8), width=Inches(5.5))

    add_bottom_banner(s11, "Multiprocessor systems use multiple CPUs sharing bus and memory to run tasks simultaneously.", "Architectural Shift:", ACCENT_CYAN)

    set_speaker_notes(
        s11,
        "Thank you. Moving into modern architectures, we look at multiprocessing. Unlike older systems with a single CPU, multiprocessor systems use multiple CPUs sharing the same bus and memory to run tasks simultaneously.",
        "Single-processor serial execution vs multiprocessor concurrent hardware execution.",
        "Let us examine the two primary multiprocessing architectural approaches: SMP and AMP.",
        "Point to the single CPU path versus the multiple parallel CPU paths on the diagram."
    )

    # =========================================================================
    # SLIDE 12: MULTIPROCESSING: SMP VS AMP (Lochan)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s12)
    apply_slide_morph_transition(s12)
    add_header(s12, 12, 15, "Act III: Multiprocessing", "Lochan", "Multiprocessing Approaches: SMP vs. AMP", "Peer Multiprocessing vs. Master-Slave Hierarchical Scheduling")

    add_card(s12, 0.8, 1.8, 5.7, 4.45, "Symmetric Multiprocessing (SMP)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    smp_pts = [
        "Peer Processors: All processors are peers and can execute OS and user tasks independently.",
        "Shared Architecture: Share physical memory and the system bus equally.",
        "Dominant Model: Used in virtually all modern personal computers and enterprise servers.",
        "Dynamic Scheduling: Any processor can pick up any ready process from the ready queue."
    ]
    add_bullet_list(s12, 1.05, 2.4, 5.2, 3.6, smp_pts, font_size=11)

    add_card(s12, 6.8, 1.8, 5.7, 4.45, "Asymmetric Multiprocessing (AMP)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_AMBER)
    amp_pts = [
        "Master-Slave Model: A master processor controls the system and assigns specific tasks to slave processors.",
        "Dedicated Roles: Slaves run specific application code or I/O while the master executes OS kernel code.",
        "Simplified Coordination: Avoids complex kernel locking contention by centralizing decisions.",
        "Specialized Systems: Often found in specialized embedded controllers and legacy mainframes."
    ]
    add_bullet_list(s12, 7.05, 2.4, 5.2, 3.6, amp_pts, font_size=11)

    add_bottom_banner(s12, "SMP treats all processors as equal peers; AMP uses a master processor delegating work to slave processors.", "Multiprocessing Models:", ACCENT_CYAN)

    set_speaker_notes(
        s12,
        "There are two main approaches here: Symmetric, where all processors are equal peers, and Asymmetric, where a master processor delegates work to slave processors.",
        "Symmetric (peer-to-peer) vs Asymmetric (master-slave) multiprocessing models and their trade-offs.",
        "Now let's examine modern systems: Multicore chips and Clustered systems.",
        "Contrast the decentralized peer model of SMP with the centralized master-slave model of AMP."
    )

    # =========================================================================
    # SLIDE 13: MULTICORE & CLUSTERED SYSTEMS (Lochan)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s13)
    apply_slide_morph_transition(s13)
    add_header(s13, 13, 15, "Act III: Multiprocessing", "Lochan", "Modern Systems: Multicore & Clustered", "On-Chip Scale-Up vs. Networked Scale-Out Architecture")

    add_card(s13, 0.8, 1.8, 5.8, 2.15, "Multicore Processors (Scale-Up)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)
    tb_mc = s13.shapes.add_textbox(Inches(1.05), Inches(2.3), Inches(5.3), Inches(1.5))
    tf_mc = tb_mc.text_frame
    tf_mc.word_wrap = True
    pts_mc = [
        "Multiple processing cores placed on a single physical chip for ultra-fast communication.",
        "On-chip communication is significantly faster and uses far less energy than inter-chip buses.",
        "Each core features private L1/L2 caches and shares an on-die L3 cache."
    ]
    for pt in pts_mc:
        p = tf_mc.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(2)

    add_card(s13, 0.8, 4.1, 5.8, 2.15, "Clustered Systems (Scale-Out)", border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_INDIGO)
    tb_cl = s13.shapes.add_textbox(Inches(1.05), Inches(4.6), Inches(5.3), Inches(1.5))
    tf_cl = tb_cl.text_frame
    tf_cl.word_wrap = True
    pts_cl = [
        "Multiple independent computers connected over a network to share immense workloads.",
        "Nodes share a common Storage Area Network (SAN) for unified data access.",
        "Provides high availability and fault tolerance — if one machine fails, others take over."
    ]
    for pt in pts_cl:
        p = tf_cl.add_paragraph()
        p.text = "• " + pt
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(2)

    chip_img = os.path.join(GAMMA_DIR, "iso_multicore_chip.png")
    if os.path.exists(chip_img):
        s13.shapes.add_picture(chip_img, Inches(7.0), Inches(1.5), width=Inches(5.5))

    add_bottom_banner(s13, "Multicore puts multiple cores on one chip; Clustered systems network independent computers together.", "Modern Architectural Spectrum:", ACCENT_CYAN)

    set_speaker_notes(
        s13,
        "Today, this scales up into Multicore processors, where multiple cores live on one chip, and Clustered systems, where whole independent computers network together to act as one.",
        "Multicore processors (on-chip parallelism) and Clustered systems (distributed high-availability nodes).",
        "However, multiprocessing creates significant challenges for the operating system. Let's look at those challenges.",
        "Contrast on-chip multicore scaling with distributed networked cluster scaling."
    )

    # =========================================================================
    # SLIDE 14: OS CHALLENGES IN MULTIPROCESSING (Lochan)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s14)
    apply_slide_morph_transition(s14)
    add_header(s14, 14, 15, "Act III: Multiprocessing", "Lochan", "OS Challenges in Multiprocessing", "Critical Complexities in Coordinating Concurrent Hardware Execution")

    challenges = [
        ("1. CPU Scheduling", "Deciding which core runs which process to maximize throughput, minimize latency, and maintain processor cache affinity.", ACCENT_CYAN),
        ("2. Cache Coherence", "Ensuring that when one CPU modifies data in its private cache, all other cores with copies of that memory address are kept updated.", ACCENT_INDIGO),
        ("3. Load Balancing", "Ensuring no single CPU sits idle while another is overwhelmed by evenly distributing ready threads across all cores.", ACCENT_EMERALD),
        ("4. Synchronization", "Using mutexes, spinlocks, and semaphores to protect shared kernel data structures and prevent race conditions.", ACCENT_ROSE)
    ]
    for i, (title, desc, col) in enumerate(challenges):
        col_idx = i % 2
        row_idx = i // 2
        px = 0.8 + col_idx * 6.0
        py = 1.8 + row_idx * 2.25
        add_card(s14, px, py, 5.7, 2.1, title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb = s14.shapes.add_textbox(Inches(px + 0.25), Inches(py + 0.5), Inches(5.2), Inches(1.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.name = FONT_BODY
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_MUTED

    add_bottom_banner(s14, "The OS must handle complex challenges like CPU scheduling, cache coherence, and load balancing.", "Operating System Burden:", ACCENT_CYAN)

    set_speaker_notes(
        s14,
        "While this hardware is powerful, it forces the operating system to work harder. The OS must handle complex challenges like CPU scheduling, cache coherence, and load balancing to keep everything running smoothly.",
        "Four major OS multiprocessing challenges: Scheduling, Cache Coherence, Load Balancing, and Synchronization.",
        "Now let's bring our entire presentation together into our final synthesis and key takeaways.",
        "Review each of the four challenges and explain why hardware parallelism demands sophisticated OS coordination."
    )

    # =========================================================================
    # SLIDE 15: COMPLETE ARCHITECTURE & KEY TAKEAWAYS (All Presenters)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_backdrop(s15)
    apply_slide_morph_transition(s15)
    add_header(s15, 15, 15, "Synthesis & Conclusion", "V. Ram Charan · Vedhanth · Lochan", "Complete Architecture & Key Takeaways", "Hardware Foundations, Storage Hierarchies & Modern Multiprocessing")

    takeaways = [
        ("1. Hardware Foundations", "CPU, RAM, and I/O linked via Address, Data, and Control buses with Interrupts and DMA for efficient operation.", ACCENT_CYAN),
        ("2. Storage Hierarchy", "Balancing speed and capacity from fast volatile Registers/Cache/RAM down to non-volatile SSDs and hard disks.", ACCENT_INDIGO),
        ("3. Locality & Memory", "Leveraging Temporal and Spatial locality through OS paging, buffering, disk caching, and prefetching.", ACCENT_EMERALD),
        ("4. Multiprocessing", "Scaling computation through SMP, AMP, Multicore on-chip processors, and Clustered networked systems.", ACCENT_AMBER)
    ]
    card_w = 2.75
    for i, (title, desc, col) in enumerate(takeaways):
        px = 0.8 + i * 3.0
        add_card(s15, px, 1.8, card_w, 2.85, title, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=col)
        tb = s15.shapes.add_textbox(Inches(px + 0.2), Inches(2.4), Inches(card_w - 0.4), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = desc
        p.font.name = FONT_BODY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    add_card(s15, 0.8, 4.8, 11.733, 0.85, None, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=ACCENT_ROSE)
    num_badge5 = s15.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.05), Inches(4.95), Inches(0.55), Inches(0.55))
    num_badge5.fill.solid()
    num_badge5.fill.fore_color.rgb = ACCENT_ROSE
    num_badge5.line.color.rgb = CARD_BORDER
    num_badge5.line.width = Pt(1.5)
    p_nb5 = num_badge5.text_frame.paragraphs[0]
    p_nb5.alignment = PP_ALIGN.CENTER
    p_nb5.text = "★"
    p_nb5.font.name = FONT_HEADING
    p_nb5.font.size = Pt(12)
    p_nb5.font.bold = True
    p_nb5.font.color.rgb = TEXT_WHITE

    tb_5 = s15.shapes.add_textbox(Inches(1.75), Inches(4.95), Inches(10.5), Inches(0.6))
    tf_5 = tb_5.text_frame
    tf_5.word_wrap = True
    p5 = tf_5.paragraphs[0]
    p5.text = "OS Coordination: The critical software that manages all this complex hardware—coordinating scheduling, cache coherence, load balancing, and synchronization."
    p5.font.name = FONT_BODY
    p5.font.size = Pt(10.5)
    p5.font.bold = True
    p5.font.color.rgb = TEXT_WHITE

    pres_cards = [
        ("V. Ram Charan", "Act I: Core Hardware (Slides 1–5)", ACCENT_CYAN),
        ("Vedhanth", "Act II: Memory & Storage Hierarchy (Slides 6–10)", ACCENT_INDIGO),
        ("Lochan", "Act III: Multiprocessing & Modern Systems (Slides 11–15)", ACCENT_EMERALD)
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
        p.font.size = Pt(10)
        p.font.color.rgb = col

    set_speaker_notes(
        s15,
        "To summarize our complete presentation: Ram Charan walked us through the core hardware and 3-part system bus; Vedhanth explained the storage hierarchy, locality of reference, and OS caching optimizations; and Lochan covered multiprocessing architectures, SMP vs AMP, multicore, clustering, and OS coordination challenges. On behalf of Ram Charan, Vedhanth, and Lochan, thank you for your attention. We are now open for questions.",
        "Comprehensive architectural synthesis covering core hardware, system bus, storage hierarchy, locality, multiprocessing, and OS coordination.",
        "End of presentation — open floor for Q&A.",
        "All three presenters step forward together, smile, and invite questions from the professor and audience."
    )

    out_pptx = os.path.join(ROOT_DIR, "computer_system_architecture.pptx")
    prs.save(out_pptx)
    out_pptx_clean = os.path.join(ROOT_DIR, "Computer_System_Architecture_OS.pptx")
    prs.save(out_pptx_clean)
    out_pptx_cinematic = os.path.join(ROOT_DIR, "Computer_System_Architecture_Cinematic.pptx")
    prs.save(out_pptx_cinematic)
    print(f"Successfully generated 15-slide Luxury presentation updated with Lochan and exact speech!")
    return out_pptx

if __name__ == "__main__":
    build_presentation()
