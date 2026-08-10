"""
scripts/generate_cinematic_ppt.py
Generates the authoritative 15-slide PowerPoint presentation:
'computer_system_architecture.pptx' for an Operating Systems university course.

Source of Truth:
Operating System Concepts, 10th Edition (2018)
Abraham Silberschatz, Peter B. Galvin, Greg Gagne
Chapter 1: Introduction

Team:
- Speaker 1: V. Ram Charan (Act I - Slides 1-5)
- Speaker 2: Vedhanth (Act II - Slides 6-10)
- Speaker 3: Lochan (Act III - Slides 11-15)
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# Ensure assets are generated
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "presentation")
sys.path.insert(0, ROOT_DIR)
from assets.presentation.diagrams import generate_all_diagrams

# Color Palette (Cinematic Dark OS Theme)
BG_DARK = RGBColor(11, 15, 25)         # #0B0F19 Deep Obsidian Slate
CARD_BG = RGBColor(21, 28, 44)         # #151C2C Graphite Card Surface
CARD_BORDER = RGBColor(42, 54, 79)     # #2A364F Subtle Card Outline
TEXT_WHITE = RGBColor(248, 250, 252)   # #F8FAFC Heading / Crisp White
TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 Secondary Text / Slate
TEXT_DIM = RGBColor(100, 116, 139)     # #64748B Dim metadata
ACCENT_CYAN = RGBColor(56, 189, 248)   # #38BDF8 Electric Cyan (Primary)
ACCENT_INDIGO = RGBColor(129, 140, 248)# #818CF8 Hyper Indigo
ACCENT_EMERALD = RGBColor(52, 211, 153)# #34D399 Emerald Green
ACCENT_AMBER = RGBColor(245, 158, 11)  # #F59E0B Amber Warning / Step
ACCENT_ROSE = RGBColor(244, 63, 94)    # #F43F5E Coral / Kernel Red
PILL_BG = RGBColor(30, 41, 59)         # #1E293B Badge Background

FONT_HEADING = "Segoe UI"
FONT_BODY = "Segoe UI"

def set_slide_background(slide, color=BG_DARK):
    """Sets a solid dark background for the slide."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_transition(slide):
    """Adds a smooth Push / Fade transition to the slide via XML."""
    try:
        slide_element = slide._element
        transition_xml = parse_xml(f'<p:transition {nsdecls("p")} spd="med"><p:push dir="l"/></p:transition>')
        slide_element.append(transition_xml)
    except Exception:
        pass

def add_header(slide, slide_num, total_slides, act_title, speaker_name, title, subtitle):
    """Creates a consistent cinematic header with Act Pill, Speaker Badge, Slide Counter, Title & Subtitle."""
    # 1. Act Pill (Top Left)
    act_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.8), Inches(0.38))
    act_box.fill.solid()
    act_box.fill.fore_color.rgb = PILL_BG
    act_box.line.color.rgb = ACCENT_CYAN
    act_box.line.width = Pt(1)
    tf_act = act_box.text_frame
    tf_act.word_wrap = True
    tf_act.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_act = tf_act.paragraphs[0]
    p_act.text = act_title.upper()
    p_act.font.name = FONT_HEADING
    p_act.font.size = Pt(10)
    p_act.font.bold = True
    p_act.font.color.rgb = ACCENT_CYAN
    p_act.alignment = PP_ALIGN.CENTER

    # 2. Speaker Badge (Top Right - Speaker name)
    spk_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(0.4), Inches(2.7), Inches(0.38))
    spk_box.fill.solid()
    spk_box.fill.fore_color.rgb = PILL_BG
    spk_box.line.color.rgb = ACCENT_INDIGO
    spk_box.line.width = Pt(1)
    tf_spk = spk_box.text_frame
    tf_spk.word_wrap = True
    tf_spk.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_spk = tf_spk.paragraphs[0]
    p_spk.text = f"SPEAKER: {speaker_name.upper()}"
    p_spk.font.name = FONT_HEADING
    p_spk.font.size = Pt(10)
    p_spk.font.bold = True
    p_spk.font.color.rgb = ACCENT_INDIGO
    p_spk.alignment = PP_ALIGN.CENTER

    # 3. Slide Number Pill (Top Right Corner)
    num_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.45), Inches(0.4), Inches(1.1), Inches(0.38))
    num_box.fill.solid()
    num_box.fill.fore_color.rgb = PILL_BG
    num_box.line.color.rgb = CARD_BORDER
    num_box.line.width = Pt(1)
    tf_num = num_box.text_frame
    tf_num.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_num = tf_num.paragraphs[0]
    p_num.text = f"{slide_num:02d} / {total_slides:02d}"
    p_num.font.name = FONT_HEADING
    p_num.font.size = Pt(10)
    p_num.font.bold = True
    p_num.font.color.rgb = TEXT_MUTED
    p_num.alignment = PP_ALIGN.CENTER

    # 4. Slide Title & Subtitle Box
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.733), Inches(0.8))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
    
    p_t = tf_title.paragraphs[0]
    p_t.text = title
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    p_sub = tf_title.add_paragraph()
    p_sub.text = subtitle
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = ACCENT_CYAN
    p_sub.space_before = Pt(2)

def add_footer(slide):
    """Adds standard reference footer."""
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.733), Inches(0.3))
    tf = footer_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = "Primary Reference: Silberschatz, Galvin & Gagne — Operating System Concepts, 10th Edition (2018), Chapter 1"
    p.font.name = FONT_BODY
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_DIM

def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER, bg_color=CARD_BG, accent_bar=None):
    """Creates a stylized dark card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if accent_bar:
        bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(0.12), Inches(height))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent_bar
        bar.line.fill.background()

    if title:
        tb = slide.shapes.add_textbox(Inches(left + (0.25 if accent_bar else 0.2)), Inches(top + 0.15), Inches(width - 0.4), Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN if not accent_bar else accent_bar

    return card

def set_speaker_notes(slide, what_to_say, concept, transition, cue):
    """Formats and sets comprehensive speaker notes on the slide."""
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = f"=== PRESENTER NOTES ===\n\n" \
                      f"1. WHAT TO SAY (45-75s Delivery Script):\n{what_to_say}\n\n" \
                      f"2. KEY TEXTBOOK CONCEPT:\n{concept}\n\n" \
                      f"3. TRANSITION TO NEXT SLIDE:\n{transition}\n\n" \
                      f"4. PRESENTATION CUE:\n{cue}"

def build_presentation():
    # 1. Generate image assets first
    generate_all_diagrams()
    
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # =========================================================================
    # SLIDE 1: TITLE (V. Ram Charan)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_transition(s1)

    # Hero Banner Container
    hero_card = add_card(s1, 1.0, 1.0, 11.333, 5.5, border_color=ACCENT_CYAN, bg_color=CARD_BG, accent_bar=ACCENT_CYAN)

    # Pill: Course
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.4), Inches(4.5), Inches(0.4))
    pill.fill.solid()
    pill.fill.fore_color.rgb = PILL_BG
    pill.line.color.rgb = ACCENT_CYAN
    pill.line.width = Pt(1)
    p_p = pill.text_frame.paragraphs[0]
    p_p.text = "OPERATING SYSTEMS  •  CHAPTER 1 INTRODUCTION"
    p_p.font.name = FONT_HEADING
    p_p.font.size = Pt(10)
    p_p.font.bold = True
    p_p.font.color.rgb = ACCENT_CYAN
    p_p.alignment = PP_ALIGN.CENTER

    # Main Title
    tb_title = s1.shapes.add_textbox(Inches(1.5), Inches(2.0), Inches(10.3), Inches(1.6))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p1 = tf_t.paragraphs[0]
    p1.text = "Computer System Architecture"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf_t.add_paragraph()
    p2.text = "Understanding the Hardware Foundation of Operating Systems"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(8)

    # Quote Box
    quote_card = add_card(s1, 1.5, 3.8, 10.3, 0.9, border_color=ACCENT_INDIGO, bg_color=PILL_BG, accent_bar=ACCENT_INDIGO)
    tb_q = s1.shapes.add_textbox(Inches(1.8), Inches(3.9), Inches(9.8), Inches(0.7))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    pq = tf_q.paragraphs[0]
    pq.text = '"The operating system is the software most intimately involved with computer hardware."'
    pq.font.name = FONT_BODY
    pq.font.size = Pt(13)
    pq.font.italic = True
    pq.font.color.rgb = TEXT_WHITE
    pq2 = tf_q.add_paragraph()
    pq2.text = "— Silberschatz, Galvin & Gagne (Operating System Concepts, 10th Edition)"
    pq2.font.name = FONT_BODY
    pq2.font.size = Pt(10)
    pq2.font.color.rgb = ACCENT_CYAN
    pq2.space_before = Pt(4)

    # Presenters Bar (3 distinct cards)
    presenters = [
        ("V. RAM CHARAN", "Speaker 1 (Act I Lead)", ACCENT_CYAN),
        ("VEDHANTH", "Speaker 2 (Act II Lead)", ACCENT_INDIGO),
        ("LOCHAN", "Speaker 3 (Act III Lead)", ACCENT_EMERALD)
    ]
    for i, (name, role, col) in enumerate(presenters):
        px = 1.5 + i * 3.55
        p_card = add_card(s1, px, 5.0, 3.2, 1.1, border_color=col, bg_color=PILL_BG, accent_bar=col)
        tb_p = s1.shapes.add_textbox(Inches(px + 0.25), Inches(5.1), Inches(2.8), Inches(0.8))
        tf_pres = tb_p.text_frame
        tf_pres.word_wrap = True
        pp1 = tf_pres.paragraphs[0]
        pp1.text = name
        pp1.font.name = FONT_HEADING
        pp1.font.size = Pt(13)
        pp1.font.bold = True
        pp1.font.color.rgb = TEXT_WHITE
        pp2 = tf_pres.add_paragraph()
        pp2.text = role
        pp2.font.name = FONT_BODY
        pp2.font.size = Pt(10)
        pp2.font.color.rgb = col
        pp2.space_before = Pt(2)

    add_footer(s1)
    set_speaker_notes(
        s1,
        "Good morning everyone. Welcome to our presentation on Computer System Architecture. I am Ram Charan, and along with my co-presenters Vedhanth and Lochan, we will walk you through how computer hardware and the operating system interact, based on Chapter 1 of Silberschatz's Operating System Concepts 10th Edition. The OS is the critical layer that transforms raw silicon, memory, and devices into a cohesive, secure platform.",
        "The Operating System is the software most intimately involved with computer hardware, balancing resource allocation and control.",
        "Let us begin with Slide 2 by looking at the four fundamental components that make up any computer system.",
        "Stand center, acknowledge professors and classmates, gesture to team member names."
    )

    # =========================================================================
    # SLIDE 2: WHAT IS A COMPUTER SYSTEM? (V. Ram Charan)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_transition(s2)
    add_header(s2, 2, 15, "Act I: Foundations", "V. Ram Charan", "What is a Computer System?", "Four Major Components & The Role of the Operating System")

    # Left: Image Diagram (Fig 1.1)
    diag_path_2 = os.path.join(ASSETS_DIR, "system_components.png")
    if os.path.exists(diag_path_2):
        s2.shapes.add_picture(diag_path_2, Inches(0.8), Inches(1.8), width=Inches(5.6))

    # Right: Structured Cards
    right_x = 6.6
    r1 = add_card(s2, right_x, 1.8, 5.9, 2.3, "The Operating System Duality", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_r1 = s2.shapes.add_textbox(Inches(right_x + 0.3), Inches(2.2), Inches(5.4), Inches(1.8))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    
    p = tf_r1.paragraphs[0]
    p.text = "1. Resource Allocator:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p_desc = tf_r1.add_paragraph()
    p_desc.text = "• Manages CPU time, memory space, and file-storage space.\n• Resolves conflicting resource requests fairly and efficiently."
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(11)
    p_desc.font.color.rgb = TEXT_MUTED
    
    p_c = tf_r1.add_paragraph()
    p_c.text = "2. Control Program:"
    p_c.font.name = FONT_HEADING
    p_c.font.size = Pt(12)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_EMERALD
    p_c.space_before = Pt(4)
    p_cdesc = tf_r1.add_paragraph()
    p_cdesc.text = "• Controls execution of user programs to prevent errors.\n• Prevents improper and unauthorized use of the computer."
    p_cdesc.font.name = FONT_BODY
    p_cdesc.font.size = Pt(11)
    p_cdesc.font.color.rgb = TEXT_MUTED

    r2 = add_card(s2, right_x, 4.3, 5.9, 2.5, "Hardware & Application Interaction", border_color=ACCENT_INDIGO, accent_bar=ACCENT_INDIGO)
    tb_r2 = s2.shapes.add_textbox(Inches(right_x + 0.3), Inches(4.7), Inches(5.4), Inches(2.0))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True

    items = [
        ("Computer Hardware:", "Provides basic computing resources (CPU, Memory, I/O Devices)."),
        ("Application Programs:", "Compilers, databases, browsers—define ways resources are used to solve user problems."),
        ("The Core Abstraction:", "The OS shields users from the ugly complexities of physical hardware.")
    ]
    for i, (k, v) in enumerate(items):
        pk = tf_r2.add_paragraph() if i > 0 else tf_r2.paragraphs[0]
        pk.text = k + " "
        pk.font.name = FONT_HEADING
        pk.font.size = Pt(11.5)
        pk.font.bold = True
        pk.font.color.rgb = TEXT_WHITE
        if i > 0: pk.space_before = Pt(4)
        
        # Add description
        pk_run = pk.add_run()
        pk_run.text = v
        pk_run.font.name = FONT_BODY
        pk_run.font.size = Pt(11)
        pk_run.font.bold = False
        pk_run.font.color.rgb = TEXT_MUTED

    add_footer(s2)
    set_speaker_notes(
        s2,
        "Silberschatz breaks a computer system into four components: Users, Application Programs, the Operating System, and Computer Hardware. Hardware supplies raw computational power—the CPU, main memory, and I/O devices. Applications want to use those resources. Sitting right between them is the Operating System. The textbook emphasizes that the OS acts as both a Resource Allocator—deciding how CPU time and memory are shared among competing requests—and as a Control Program—preventing bugs and illegal operations from crashing the machine.",
        "Four-component architecture (Users, Apps, OS, Hardware) and the OS's dual identity as Resource Allocator and Control Program.",
        "Now let's examine how computer system architectures have evolved from simple single-processor systems to modern multi-core chips.",
        "Point to the vertical diagram showing the OS buffering applications from raw hardware."
    )

    # =========================================================================
    # SLIDE 3: COMPUTER-SYSTEM ARCHITECTURE (V. Ram Charan)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_transition(s3)
    add_header(s3, 3, 15, "Act I: Foundations", "V. Ram Charan", "Computer-System Architecture", "Evolution: Single-Processor, Multiprocessor, and Multicore Systems")

    # 3 Column Cards
    col_w = 3.7
    cards = [
        ("Single-Processor Systems", ACCENT_CYAN, [
            ("One Main CPU:", "Executes a general-purpose instruction set."),
            ("Special-Purpose Processors:", "Disk, keyboard, and graphics controllers run limited instruction sets."),
            ("OS Perspective:", "All user processes compete for execution on the single general-purpose CPU.")
        ]),
        ("Multiprocessor Systems", ACCENT_INDIGO, [
            ("Parallel / Tightly Coupled:", "Two or more processors in close communication sharing bus, clock, and memory."),
            ("Three Key Advantages:", "1. Increased Throughput\n2. Economy of Scale\n3. Graceful Degradation / Reliability"),
            ("Fault Tolerance:", "Failure of one processor does not halt the entire system.")
        ]),
        ("Multicore Systems", ACCENT_EMERALD, [
            ("Multiple Cores on One Chip:", "Modern approach integrating multiple computing cores onto a single processor package."),
            ("Faster Communication:", "On-chip interconnects operate faster than motherboard buses."),
            ("Power Efficient:", "Consumes significantly less energy than multiple discrete chips.")
        ])
    ]

    for i, (ctitle, ccol, citems) in enumerate(cards):
        cx = 0.8 + i * 4.0
        add_card(s3, cx, 1.8, col_w, 3.2, ctitle, border_color=ccol, accent_bar=ccol)
        tb = s3.shapes.add_textbox(Inches(cx + 0.25), Inches(2.2), Inches(col_w - 0.4), Inches(2.7))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (h, b) in enumerate(citems):
            p = tf.add_paragraph() if j > 0 else tf.paragraphs[0]
            p.text = h + "\n"
            p.font.name = FONT_HEADING
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = ccol
            if j > 0: p.space_before = Pt(4)
            run = p.add_run()
            run.text = b
            run.font.name = FONT_BODY
            run.font.size = Pt(10.5)
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Terminology Box
    term_card = add_card(s3, 0.8, 5.2, 11.733, 1.6, "Textbook Terminology (Silberschatz Definitions)", border_color=ACCENT_AMBER, bg_color=PILL_BG, accent_bar=ACCENT_AMBER)
    tb_term = s3.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.2), Inches(1.2))
    tf_term = tb_term.text_frame
    tf_term.word_wrap = True
    
    terms = [
        ("CPU:", " The hardware component that executes instructions."),
        ("Processor:", " A physical chip containing one or more CPUs."),
        ("Core:", " The basic computation unit inside a CPU."),
        ("Multicore:", " Multiple computing cores on one single CPU/chip."),
        ("Multiprocessor:", " A system containing multiple physical processor chips.")
    ]
    p_tline = tf_term.paragraphs[0]
    for k, v in terms[:3]:
        r_k = p_tline.add_run()
        r_k.text = k
        r_k.font.bold = True
        r_k.font.color.rgb = ACCENT_AMBER
        r_v = p_tline.add_run()
        r_v.text = v + "   |   "
        r_v.font.color.rgb = TEXT_WHITE
    
    p_tline2 = tf_term.add_paragraph()
    p_tline2.space_before = Pt(4)
    for k, v in terms[3:]:
        r_k = p_tline2.add_run()
        r_k.text = k
        r_k.font.bold = True
        r_k.font.color.rgb = ACCENT_AMBER
        r_v = p_tline2.add_run()
        r_v.text = v + "   |   "
        r_v.font.color.rgb = TEXT_WHITE

    add_footer(s3)
    set_speaker_notes(
        s3,
        "The textbook traces the progression of computer architecture from Single-Processor systems to Multiprocessor and Multicore designs. Single-processor systems have one main general-purpose CPU. Multiprocessor systems add multiple processors sharing buses and memory, providing three major advantages: increased throughput, economy of scale, and graceful degradation—which means if one processor fails, the system continues running. Finally, multicore technology puts multiple computing cores on a single physical chip.",
        "Definitions of CPU, Processor, Core, Multicore, Multiprocessor, and the 3 advantages of multiprocessor systems.",
        "Let's look more closely at multicore chips and how Symmetric Multiprocessing operates.",
        "Emphasize the precise textbook definitions in the bottom callout bar."
    )

    # =========================================================================
    # SLIDE 4: MULTICORE & SYMMETRIC MULTIPROCESSING (V. Ram Charan)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_transition(s4)
    add_header(s4, 4, 15, "Act I: Foundations", "V. Ram Charan", "Multicore & Symmetric Multiprocessing (SMP)", "On-Chip Parallelism & Resource Sharing (Silberschatz Figure 1.8)")

    # Left: Diagram
    diag_path_4 = os.path.join(ASSETS_DIR, "multicore_chip.png")
    if os.path.exists(diag_path_4):
        s4.shapes.add_picture(diag_path_4, Inches(0.8), Inches(1.8), width=Inches(5.7))

    # Right: Explanatory Cards
    right_x = 6.7
    c1 = add_card(s4, right_x, 1.8, 5.8, 2.4, "Why Modern Systems Use Multicore", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_c1 = s4.shapes.add_textbox(Inches(right_x + 0.3), Inches(2.2), Inches(5.3), Inches(1.9))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    
    pts_c1 = [
        ("On-Chip Communication:", "Significantly faster on-chip interconnects compared to inter-chip system buses."),
        ("Energy Efficiency:", "Consumes less power and produces less heat than multiple separate single-core chips."),
        ("SMP Architecture:", "All cores act as peers; each core can run all tasks including OS code and user processes.")
    ]
    for i, (h, b) in enumerate(pts_c1):
        p = tf_c1.add_paragraph() if i > 0 else tf_c1.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    c2 = add_card(s4, right_x, 4.4, 5.8, 2.4, "Core Memory Organization & OS View", border_color=ACCENT_INDIGO, accent_bar=ACCENT_INDIGO)
    tb_c2 = s4.shapes.add_textbox(Inches(right_x + 0.3), Inches(4.8), Inches(5.3), Inches(1.9))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True

    pts_c2 = [
        ("Private vs Shared Caches:", "Each core has dedicated registers and private L1 cache, while sharing on-chip L2/L3 cache and DRAM."),
        ("Logical CPU View:", "Operating system views each individual core as a separate logical processor unit."),
        ("Scheduling Support:", "Modern OS schedulers dynamically distribute threads across all available cores concurrently.")
    ]
    for i, (h, b) in enumerate(pts_c2):
        p = tf_c2.add_paragraph() if i > 0 else tf_c2.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s4)
    set_speaker_notes(
        s4,
        "Why has the computing industry transitioned entirely to multicore? As Silberschatz points out, on-chip communication between cores on the same silicon die is vastly faster and consumes far less power than broadcasting signals across motherboard buses. In a multicore SMP system, each core has its own private registers and L1 cache, while sharing lower-level caches and main memory. The operating system views each core as an independent logical CPU, scheduling threads across all cores simultaneously.",
        "Multicore chip organization, private L1 vs shared cache, and Symmetric Multiprocessing (SMP) peer scheduling.",
        "However, as we keep adding more processors to a single shared bus, we hit a major bottleneck. Let's see how NUMA architecture solves this.",
        "Point to the private core caches versus the shared interconnect on the diagram."
    )

    # =========================================================================
    # SLIDE 5: MULTIPROCESSOR & NUMA ARCHITECTURE (V. Ram Charan)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_transition(s5)
    add_header(s5, 5, 15, "Act I: Foundations", "V. Ram Charan", "Multiprocessor & NUMA Architecture", "Non-Uniform Memory Access for Highly Scalable Multiprocessing (Silberschatz Figure 1.9)")

    # Left: Diagram
    diag_path_5 = os.path.join(ASSETS_DIR, "numa_architecture.png")
    if os.path.exists(diag_path_5):
        s5.shapes.add_picture(diag_path_5, Inches(0.8), Inches(1.8), width=Inches(5.7))

    # Right: Structured Explanations
    right_x = 6.7
    n1 = add_card(s5, right_x, 1.8, 5.8, 2.4, "The Scaling Limit & Bus Bottleneck", border_color=ACCENT_ROSE, accent_bar=ACCENT_ROSE)
    tb_n1 = s5.shapes.add_textbox(Inches(right_x + 0.3), Inches(2.2), Inches(5.3), Inches(1.9))
    tf_n1 = tb_n1.text_frame
    tf_n1.word_wrap = True

    pts_n1 = [
        ("Shared Bus Contention:", "When multiple CPUs share a single memory bus, memory access contention slows the entire system down."),
        ("The Bottleneck:", "Adding more processors eventually yields diminishing returns because CPUs stall waiting for bus access."),
        ("The NUMA Solution:", "Distribute memory physically across CPU clusters while maintaining a single shared address space.")
    ]
    for i, (h, b) in enumerate(pts_n1):
        p = tf_n1.add_paragraph() if i > 0 else tf_n1.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    n2 = add_card(s5, right_x, 4.4, 5.8, 2.4, "Local vs Remote Memory & OS Role", border_color=ACCENT_AMBER, accent_bar=ACCENT_AMBER)
    tb_n2 = s5.shapes.add_textbox(Inches(right_x + 0.3), Inches(4.8), Inches(5.3), Inches(1.9))
    tf_n2 = tb_n2.text_frame
    tf_n2.word_wrap = True

    pts_n2 = [
        ("Local Memory Access:", "CPU accessing its own attached local memory is ultra-fast with zero bus contention."),
        ("Remote Memory Access:", "Accessing memory on another node traverses the system interconnect, incurring higher latency."),
        ("OS NUMA Awareness:", "Operating systems schedule processes on the CPU closest to where the process memory is allocated.")
    ]
    for i, (h, b) in enumerate(pts_n2):
        p = tf_n2.add_paragraph() if i > 0 else tf_n2.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s5)
    set_speaker_notes(
        s5,
        "When we scale to dozens of processors, connecting them all to a single shared bus causes severe contention. Silberschatz explains that NUMA—Non-Uniform Memory Access—overcomes this by giving each CPU its own local memory bank while still presenting a single unified address space. Local memory access is very fast; accessing remote memory over the system interconnect takes longer. The OS must be NUMA-aware to schedule threads near their allocated memory. That concludes Act I. I will now hand over to Vedhanth for Act II.",
        "NUMA architecture, bus contention bottleneck, local vs remote latency trade-off, and OS locality management.",
        "I will now pass the presentation to Vedhanth, who will explain how the operating system maintains hardware control through interrupts and dual-mode execution.",
        "Conclude Act I, hand presentation clicker/focus over to Vedhanth."
    )

    # =========================================================================
    # SLIDE 6: HOW THE OS OPERATES WITH HARDWARE (Vedhanth)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_transition(s6)
    add_header(s6, 6, 15, "Act II: OS Control & Memory", "Vedhanth", "How the OS Operates with Hardware", "Maintaining Control via the Interrupt Mechanism")

    # Flow Box across the top
    flow_card = add_card(s6, 0.8, 1.8, 11.733, 1.3, "The Hardware-to-OS Interrupt Chain", border_color=ACCENT_CYAN, bg_color=PILL_BG, accent_bar=ACCENT_CYAN)
    tb_flow = s6.shapes.add_textbox(Inches(1.1), Inches(2.15), Inches(11.2), Inches(0.8))
    tf_f = tb_flow.text_frame
    tf_f.word_wrap = True
    
    flow_steps = [
        ("1. Device Event", "Hardware generates signal"),
        ("2. CPU Interrupted", "Suspends current instruction"),
        ("3. State Saved", "Saves PC & Registers"),
        ("4. IVT Lookup", "Fetches handler address"),
        ("5. ISR Executes", "Kernel services event"),
        ("6. Return", "Restores user process")
    ]
    p_flow = tf_f.paragraphs[0]
    for i, (st, desc) in enumerate(flow_steps):
        r_st = p_flow.add_run()
        r_st.text = f"[{st}]"
        r_st.font.bold = True
        r_st.font.color.rgb = ACCENT_CYAN
        r_d = p_flow.add_run()
        r_d.text = f" {desc}"
        r_d.font.color.rgb = TEXT_WHITE
        if i < len(flow_steps) - 1:
            r_arr = p_flow.add_run()
            r_arr.text = "  →  "
            r_arr.font.bold = True
            r_arr.font.color.rgb = ACCENT_AMBER

    # Two Column Detail Cards
    c_w = 5.7
    d1 = add_card(s6, 0.8, 3.3, c_w, 3.5, "Event-Driven OS Operation", border_color=ACCENT_INDIGO, accent_bar=ACCENT_INDIGO)
    tb_d1 = s6.shapes.add_textbox(Inches(1.1), Inches(3.7), Inches(5.2), Inches(2.9))
    tf_d1 = tb_d1.text_frame
    tf_d1.word_wrap = True

    pts_d1 = [
        ("The Control Problem:", "The operating system must maintain control over computer hardware without wasting CPU cycles constantly polling devices."),
        ("Interrupt-Driven Execution:", "Modern operating systems are event-driven. If there are no processes to execute, no I/O requests, and no user input, the OS sits idle."),
        ("Asynchronous Signaling:", "Hardware devices signal the CPU asynchronously via system bus interrupt lines whenever an operation completes.")
    ]
    for i, (h, b) in enumerate(pts_d1):
        p = tf_d1.add_paragraph() if i > 0 else tf_d1.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(4)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    d2 = add_card(s6, 6.8, 3.3, c_w, 3.5, "Interrupt Handling & Vector Table", border_color=ACCENT_EMERALD, accent_bar=ACCENT_EMERALD)
    tb_d2 = s6.shapes.add_textbox(Inches(7.1), Inches(3.7), Inches(5.2), Inches(2.9))
    tf_d2 = tb_d2.text_frame
    tf_d2.word_wrap = True

    pts_d2 = [
        ("Interrupt Vector Table (IVT):", "An array of pointers stored in low memory containing the entry addresses of specialized Interrupt Service Routines (ISRs)."),
        ("Context Preservation:", "CPU hardware automatically pushes the Program Counter (PC) and CPU status registers onto the kernel stack before branching."),
        ("Handler Execution & Return:", "The OS handles the request, acknowledges the interrupt controller, and executes a return-from-interrupt instruction to resume the interrupted process seamlessly.")
    ]
    for i, (h, b) in enumerate(pts_d2):
        p = tf_d2.add_paragraph() if i > 0 else tf_d2.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(4)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s6)
    set_speaker_notes(
        s6,
        "Thank you Ram Charan. Hello everyone, I am Vedhanth, and in Act II we will look at how the Operating System controls and protects hardware. Silberschatz emphasizes that modern operating systems are completely interrupt-driven. When an I/O device finishes an operation, its controller asserts an interrupt signal. The CPU detects this, saves the current Program Counter and registers, looks up the corresponding service routine in the Interrupt Vector Table, executes the handler, and then resumes the user program.",
        "Interrupt mechanism as the core foundation of event-driven OS control and the role of the Interrupt Vector Table.",
        "Now let's distinguish between hardware interrupts, software exceptions, and system calls.",
        "Walk the audience step-by-step through the horizontal flow diagram at the top."
    )

    # =========================================================================
    # SLIDE 7: INTERRUPTS & SYSTEM CALLS (Vedhanth)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_transition(s7)
    add_header(s7, 7, 15, "Act II: OS Control & Memory", "Vedhanth", "Interrupts, Traps & System Calls", "Distinguishing Hardware Signals, Software Exceptions, and Kernel Requests")

    # 3 Category Cards
    col_w = 3.7
    categories = [
        ("Hardware Interrupt", ACCENT_CYAN, [
            ("Origin:", "Generated by physical hardware devices."),
            ("Timing:", "Asynchronous (can happen at any moment during instruction execution)."),
            ("Examples:", "Timer tick, keyboard keystroke, network packet arrival, disk transfer completion.")
        ]),
        ("Trap / Exception", ACCENT_AMBER, [
            ("Origin:", "Generated by the CPU or software execution."),
            ("Timing:", "Synchronous (occurs exactly at the execution of a specific instruction)."),
            ("Examples:", "Division by zero, invalid memory access (page fault), intentional software trap.")
        ]),
        ("System Call", ACCENT_EMERALD, [
            ("Origin:", "Programmatic request by user software."),
            ("Purpose:", "Allows user programs to request privileged operating system services."),
            ("Examples:", "File operations (read/write), process creation (fork/exec), network communication.")
        ])
    ]
    for i, (ctitle, ccol, citems) in enumerate(categories):
        cx = 0.8 + i * 4.0
        add_card(s7, cx, 1.8, col_w, 3.1, ctitle, border_color=ccol, accent_bar=ccol)
        tb = s7.shapes.add_textbox(Inches(cx + 0.25), Inches(2.2), Inches(col_w - 0.4), Inches(2.6))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (h, b) in enumerate(citems):
            p = tf.add_paragraph() if j > 0 else tf.paragraphs[0]
            p.text = h + " "
            p.font.name = FONT_HEADING
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = ccol
            if j > 0: p.space_before = Pt(3)
            run = p.add_run()
            run.text = b
            run.font.name = FONT_BODY
            run.font.size = Pt(10.5)
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Full-Width Card: System Call Execution Flow
    sc_card = add_card(s7, 0.8, 5.1, 11.733, 1.7, "The System-Call Execution Pipeline (Silberschatz Flow)", border_color=ACCENT_INDIGO, bg_color=PILL_BG, accent_bar=ACCENT_INDIGO)
    tb_sc = s7.shapes.add_textbox(Inches(1.1), Inches(5.45), Inches(11.2), Inches(1.2))
    tf_sc = tb_sc.text_frame
    tf_sc.word_wrap = True
    
    sc_flow = [
        "1. USER PROGRAM executes system call library wrapper",
        "2. TRAP INSTRUCTION triggers hardware mode switch",
        "3. KERNEL INDEXES Interrupt/Syscall Vector table",
        "4. KERNEL SERVICE ROUTINE executes privileged operation",
        "5. RETURN-FROM-TRAP restores User Mode & resumes application"
    ]
    p_sc = tf_sc.paragraphs[0]
    p_sc.text = "   →   ".join(sc_flow[:3])
    p_sc.font.name = FONT_BODY
    p_sc.font.size = Pt(10.5)
    p_sc.font.bold = True
    p_sc.font.color.rgb = TEXT_WHITE

    p_sc2 = tf_sc.add_paragraph()
    p_sc2.text = "   →   " + "   →   ".join(sc_flow[3:])
    p_sc2.font.name = FONT_BODY
    p_sc2.font.size = Pt(10.5)
    p_sc2.font.bold = True
    p_sc2.font.color.rgb = ACCENT_CYAN
    p_sc2.space_before = Pt(4)

    add_footer(s7)
    set_speaker_notes(
        s7,
        "It is crucial to distinguish between three terms that students often confuse: Hardware Interrupts, Traps, and System Calls. Hardware interrupts are asynchronous signals from physical devices. A Trap or exception is synchronous, triggered directly by an instruction—like a divide-by-zero error or a software-generated trap. A System Call is the official programmatic interface user applications use to request services reserved for the OS kernel, executing a trap that safely crosses the user-kernel boundary.",
        "Distinction between asynchronous hardware interrupts and synchronous software traps/syscalls, plus the system call execution sequence.",
        "To ensure user programs cannot bypass this boundary, the hardware enforces Dual-Mode Operation.",
        "Highlight the transition from user mode to kernel mode during a system call."
    )

    # =========================================================================
    # SLIDE 8: DUAL-MODE OPERATION (Vedhanth)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_transition(s8)
    add_header(s8, 8, 15, "Act II: OS Control & Memory", "Vedhanth", "Dual-Mode CPU Operation", "Hardware-Enforced Protection via the Mode Bit (Silberschatz Figure 1.14)")

    # Left: Diagram
    diag_path_8 = os.path.join(ASSETS_DIR, "dual_mode.png")
    if os.path.exists(diag_path_8):
        s8.shapes.add_picture(diag_path_8, Inches(0.8), Inches(1.8), width=Inches(5.7))

    # Right: Detailed Cards
    right_x = 6.7
    dm1 = add_card(s8, right_x, 1.8, 5.8, 2.4, "The Mode Bit Architecture", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_dm1 = s8.shapes.add_textbox(Inches(right_x + 0.3), Inches(2.2), Inches(5.3), Inches(1.9))
    tf_dm1 = tb_dm1.text_frame
    tf_dm1.word_wrap = True

    pts_dm1 = [
        ("Hardware Mode Bit:", "A dedicated bit in the processor status register indicating current execution privilege."),
        ("User Mode (Mode Bit = 1):", "Execution done on behalf of user applications. Hardware access is strictly restricted."),
        ("Kernel Mode (Mode Bit = 0):", "Also known as Supervisor, System, or Privileged mode. Unrestricted hardware and memory access for the OS kernel.")
    ]
    for i, (h, b) in enumerate(pts_dm1):
        p = tf_dm1.add_paragraph() if i > 0 else tf_dm1.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    dm2 = add_card(s8, right_x, 4.4, 5.8, 2.4, "Why Dual-Mode is Vital for OS Security", border_color=ACCENT_ROSE, accent_bar=ACCENT_ROSE)
    tb_dm2 = s8.shapes.add_textbox(Inches(right_x + 0.3), Inches(4.8), Inches(5.3), Inches(1.9))
    tf_dm2 = tb_dm2.text_frame
    tf_dm2.word_wrap = True

    pts_dm2 = [
        ("Fault Isolation:", "Prevents errant or malicious user programs from modifying operating system data structures or crashing other programs."),
        ("Privileged Instructions:", "Hardware permits sensitive instructions (I/O, timer, interrupt control) to execute ONLY when Mode Bit = 0."),
        ("Boot Sequence:", "System starts in Kernel Mode, loads the OS, sets Mode Bit = 1, and switches to User Mode to execute user applications.")
    ]
    for i, (h, b) in enumerate(pts_dm2):
        p = tf_dm2.add_paragraph() if i > 0 else tf_dm2.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s8)
    set_speaker_notes(
        s8,
        "Dual-mode operation is one of the most fundamental concepts in computer science. The CPU hardware contains a Mode Bit: when Mode Bit equals 1, the CPU is in User Mode; when Mode Bit equals 0, it is in Kernel Mode. Why is this necessary? If user applications could directly alter hardware registers or halt the processor, one buggy program could crash the entire computer. By enforcing dual modes in hardware, privileged instructions can only execute when the mode bit is zero.",
        "Dual-mode operation, the hardware Mode Bit (0=Kernel, 1=User), privileged instructions, and fault isolation.",
        "Let's look at exactly what constitutes a privileged instruction and what happens when an illegal operation occurs.",
        "Point to the mode bit toggling between 0 and 1 in the diagram."
    )

    # =========================================================================
    # SLIDE 9: PROTECTION & PRIVILEGED INSTRUCTIONS (Vedhanth)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_transition(s9)
    add_header(s9, 9, 15, "Act II: OS Control & Memory", "Vedhanth", "Protection & Privileged Instructions", "Hardware-Enforced Safeguards Against Illegal Operations")

    # 3 Column Cards of Privileged Examples
    col_w = 3.7
    priv_examples = [
        ("I/O Control Instructions", ACCENT_CYAN, [
            ("Direct Device Access:", "Instructions that communicate directly with device controllers or issue port I/O commands."),
            ("Protection Goal:", "Prevents user applications from directly reading raw disk sectors or tampering with other users' data."),
            ("Enforcement:", "All I/O must be requested through OS system calls.")
        ]),
        ("Timer & Clock Management", ACCENT_AMBER, [
            ("Modifying Timers:", "Instructions that load, reset, or stop the hardware interval timer."),
            ("Protection Goal:", "Prevents a user process from disabling the timer and monopolizing the CPU indefinitely."),
            ("Enforcement:", "Only the OS scheduler can configure timer intervals.")
        ]),
        ("Interrupt & Memory Control", ACCENT_ROSE, [
            ("Altering State:", "Instructions that disable/enable interrupts or modify base/limit memory registers."),
            ("Protection Goal:", "Prevents user code from blinding the OS to hardware events or accessing kernel memory."),
            ("Enforcement:", "Attempting these in user mode causes an instant Trap.")
        ])
    ]
    for i, (ctitle, ccol, citems) in enumerate(priv_examples):
        cx = 0.8 + i * 4.0
        add_card(s9, cx, 1.8, col_w, 3.2, ctitle, border_color=ccol, accent_bar=ccol)
        tb = s9.shapes.add_textbox(Inches(cx + 0.25), Inches(2.2), Inches(col_w - 0.4), Inches(2.7))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (h, b) in enumerate(citems):
            p = tf.add_paragraph() if j > 0 else tf.paragraphs[0]
            p.text = h + " "
            p.font.name = FONT_HEADING
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = ccol
            if j > 0: p.space_before = Pt(3)
            run = p.add_run()
            run.text = b
            run.font.name = FONT_BODY
            run.font.size = Pt(10.5)
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Flow Card: Illegal Instruction Trap
    trap_card = add_card(s9, 0.8, 5.2, 11.733, 1.6, "What Happens When a User Program Executes an Illegal Privileged Instruction?", border_color=ACCENT_ROSE, bg_color=PILL_BG, accent_bar=ACCENT_ROSE)
    tb_trap = s9.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.2), Inches(1.2))
    tf_trap = tb_trap.text_frame
    tf_trap.word_wrap = True

    trap_flow = [
        ("1. USER MODE:", "App executes privileged instruction (e.g. CLI, direct I/O)"),
        ("2. CPU HARDWARE:", "Detects Mode Bit == 1 → Refuses execution"),
        ("3. HARDWARE TRAP:", "Fires Illegal Instruction Exception to OS"),
        ("4. OS RESPONSE:", "Kernel intercepts trap and terminates the offending process")
    ]
    p_t1 = tf_trap.paragraphs[0]
    p_t1.text = "   →   ".join([f"[{k}] {v}" for k, v in trap_flow[:2]])
    p_t1.font.name = FONT_BODY
    p_t1.font.size = Pt(11)
    p_t1.font.bold = True
    p_t1.font.color.rgb = TEXT_WHITE

    p_t2 = tf_trap.add_paragraph()
    p_t2.text = "   →   ".join([f"[{k}] {v}" for k, v in trap_flow[2:]])
    p_t2.font.name = FONT_BODY
    p_t2.font.size = Pt(11)
    p_t2.font.bold = True
    p_t2.font.color.rgb = ACCENT_ROSE
    p_t2.space_before = Pt(4)

    add_footer(s9)
    set_speaker_notes(
        s9,
        "What instructions are strictly privileged? The textbook lists instructions that control I/O devices, modify timer registers, turn off interrupts, or change memory management registers. If a user program tries to execute any of these privileged instructions in User Mode, the hardware detects that the mode bit is 1, immediately blocks the instruction, and fires a trap to the OS. The operating system treats this as a fatal error and terminates the offending process, keeping the rest of the system safe.",
        "Privileged instruction categories (I/O, timer, interrupts, memory) and hardware trap generation on violation.",
        "Now, what happens if a user program enters an infinite loop and refuses to yield control? Let's look at the Timer mechanism.",
        "Emphasize that the hardware blocks the illegal instruction before it can cause harm."
    )

    # =========================================================================
    # SLIDE 10: TIMER & OS CONTROL (Vedhanth)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_transition(s10)
    add_header(s10, 10, 15, "Act II: OS Control & Memory", "Vedhanth", "The Hardware Timer & OS Control", "Guaranteeing Operating System Preemption & Preventing CPU Monopolization")

    # Left: The Infinite Loop Dilemma
    c_w = 5.7
    t1 = add_card(s10, 0.8, 1.8, c_w, 5.0, "The Problem: The Infinite Loop Dilemma", border_color=ACCENT_ROSE, accent_bar=ACCENT_ROSE)
    tb_t1 = s10.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.2), Inches(4.4))
    tf_t1 = tb_t1.text_frame
    tf_t1.word_wrap = True

    pts_t1 = [
        ("The Monopolization Risk:", "Once the CPU switches to User Mode to execute a program, how does the OS ensure it will ever regain control?"),
        ("The Malicious or Buggy App:", "A user program might enter an infinite loop (e.g. while(true){}) or fail to invoke any system calls."),
        ("Without a Hardware Timer:", "The CPU would stay trapped in the user program forever; the OS would never regain execution, freezing the system."),
        ("Key Silberschatz Insight:", '"We must ensure that the operating system maintains control over the CPU."')
    ]
    for i, (h, b) in enumerate(pts_t1):
        p = tf_t1.add_paragraph() if i > 0 else tf_t1.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(6)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(11)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: The Timer Solution
    t2 = add_card(s10, 6.8, 1.8, c_w, 5.0, "The Solution: The Hardware Timer", border_color=ACCENT_EMERALD, accent_bar=ACCENT_EMERALD)
    tb_t2 = s10.shapes.add_textbox(Inches(7.1), Inches(2.2), Inches(5.2), Inches(4.4))
    tf_t2 = tb_t2.text_frame
    tf_t2.word_wrap = True

    pts_t2 = [
        ("Hardware Interval Timer:", "A specialized clock circuit that decrements with every physical clock cycle. Can be configured only via privileged instructions."),
        ("Preemption Interrupt:", "When the counter reaches zero, the timer hardware generates an interrupt, forcing the CPU back into Kernel Mode (Mode Bit = 0)."),
        ("OS Scheduler Intervention:", "The OS scheduler regains CPU control, updates process accounting, and selects the next thread to run (Time Slicing)."),
        ("Guaranteed Control:", "The hardware timer guarantees that no single program can monopolize the CPU, ensuring fair multi-tasking.")
    ]
    for i, (h, b) in enumerate(pts_t2):
        p = tf_t2.add_paragraph() if i > 0 else tf_t2.paragraphs[0]
        p.text = "• " + h + "\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(6)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(11)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s10)
    set_speaker_notes(
        s10,
        "Imagine what would happen if a user program entered an infinite loop. If the OS had no way to intervene, the whole computer would hang forever. Silberschatz explains that the **Hardware Timer** solves this problem. Before handing the CPU to a user process, the OS sets a timer. As the CPU executes, the timer decrements. When it hits zero, a hardware interrupt fires, forcing control back to the OS scheduler. This guarantees preemption and makes multitasking possible. That concludes Act II. I will now pass to Lochan for Act III.",
        "The hardware timer as the guarantor of OS CPU control, preemption, and time-sharing.",
        "I will now pass the presentation to Lochan, who will cover the Memory Hierarchy, I/O systems, Clustered systems, and our final synthesis.",
        "Conclude Act II and hand the presentation clicker/focus over to Lochan."
    )

    # =========================================================================
    # SLIDE 11: MEMORY & STORAGE HIERARCHY (Lochan)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_transition(s11)
    add_header(s11, 11, 15, "Act III: Multiprocessors, I/O & Architecture", "Lochan", "Memory & Storage-Device Hierarchy", "Speed, Cost, and Volatility Trade-offs (Silberschatz Figure 1.10)")

    # Left: Diagram
    diag_path_11 = os.path.join(ASSETS_DIR, "storage_hierarchy.png")
    if os.path.exists(diag_path_11):
        s11.shapes.add_picture(diag_path_11, Inches(0.8), Inches(1.8), width=Inches(5.7))

    # Right: Structured Cards
    right_x = 6.7
    h1 = add_card(s11, right_x, 1.8, 5.8, 2.4, "Hierarchy Organization & Speed Gap", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_h1 = s11.shapes.add_textbox(Inches(right_x + 0.3), Inches(2.2), Inches(5.3), Inches(1.9))
    tf_h1 = tb_h1.text_frame
    tf_h1.word_wrap = True

    pts_h1 = [
        ("Registers & Caches:", "Fastest access times, smallest storage capacity, highest cost per bit, volatile (lost on power-off)."),
        ("Main Memory (DRAM):", "The only large storage medium the CPU can directly address and execute instructions from. Volatile."),
        ("Nonvolatile Storage:", "Solid-State Disks (NVM) and Hard Disks retain data indefinitely; slower access, lowest cost per bit.")
    ]
    for i, (h, b) in enumerate(pts_h1):
        p = tf_h1.add_paragraph() if i > 0 else tf_h1.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    h2 = add_card(s11, right_x, 4.4, 5.8, 2.4, "Two Fundamental Axioms (Silberschatz)", border_color=ACCENT_AMBER, accent_bar=ACCENT_AMBER)
    tb_h2 = s11.shapes.add_textbox(Inches(right_x + 0.3), Inches(4.8), Inches(5.3), Inches(1.9))
    tf_h2 = tb_h2.text_frame
    tf_h2.word_wrap = True

    pts_h2 = [
        ("Axiom 1 (Execution Requirement):", "Programs must be brought into Main Memory (RAM) to be executed by the CPU."),
        ("Axiom 2 (Speed vs Cost Trade-off):", "Higher tiers are faster and more expensive per bit; lower tiers offer massive capacity at lower cost."),
        ("The Caching Principle:", "Information is copied temporarily from slower storage to faster storage to accelerate access.")
    ]
    for i, (h, b) in enumerate(pts_h2):
        p = tf_h2.add_paragraph() if i > 0 else tf_h2.paragraphs[0]
        p.text = "• " + h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s11)
    set_speaker_notes(
        s11,
        "Thank you Vedhanth. Hello everyone, I am Lochan, and in Act III we will explore storage hierarchies, I/O systems, and clustered environments. As Silberschatz illustrates, memory is organized in a strict pyramid governed by speed, cost, and volatility. At the top, CPU registers and caches offer near-instant access but are small, expensive, and volatile. Main memory is the only large storage the CPU can directly address. Below that, nonvolatile SSDs and hard disks preserve data permanently. The OS must stage data across these tiers efficiently.",
        "Storage hierarchy trade-offs (speed, cost per bit, volatility) and the caching principle.",
        "Now let's examine how the operating system communicates with I/O devices.",
        "Trace the storage pyramid from top to bottom on the diagram."
    )

    # =========================================================================
    # SLIDE 12: I/O STRUCTURE (Lochan)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_transition(s12)
    add_header(s12, 12, 15, "Act III: Multiprocessors, I/O & Architecture", "Lochan", "I/O Structure & Device Controllers", "Bridging the Speed Gap Between CPU and Peripherals (Silberschatz Model)")

    # 3 Column Cards
    col_w = 3.7
    io_cards = [
        ("Device Controllers", ACCENT_CYAN, [
            ("Hardware Interface:", "Each device type is managed by a specialized controller (disk, keyboard, network)."),
            ("Local Buffers:", "Maintains local buffer storage and control registers for data staging."),
            ("Autonomous Operation:", "Moves data between the peripheral device and its local buffer independently.")
        ]),
        ("Device Drivers", ACCENT_INDIGO, [
            ("Software Interface:", "Operating system component that understands the controller's register layout."),
            ("Uniform OS Layer:", "Provides a standard, device-independent interface to the rest of the OS kernel."),
            ("I/O Dispatch:", "Loads controller registers to initiate physical I/O operations.")
        ]),
        ("Direct Memory Access (DMA)", ACCENT_EMERALD, [
            ("High-Speed Devices:", "Used for high-throughput block devices like disk controllers and network interfaces."),
            ("Bypassing the CPU:", "Transfers entire data blocks directly between device buffers and RAM without CPU intervention."),
            ("Single Interrupt per Block:", "Interrupts the CPU only once per complete block rather than once per byte.")
        ])
    ]
    for i, (ctitle, ccol, citems) in enumerate(io_cards):
        cx = 0.8 + i * 4.0
        add_card(s12, cx, 1.8, col_w, 3.2, ctitle, border_color=ccol, accent_bar=ccol)
        tb = s12.shapes.add_textbox(Inches(cx + 0.25), Inches(2.2), Inches(col_w - 0.4), Inches(2.7))
        tf = tb.text_frame
        tf.word_wrap = True
        for j, (h, b) in enumerate(citems):
            p = tf.add_paragraph() if j > 0 else tf.paragraphs[0]
            p.text = h + " "
            p.font.name = FONT_HEADING
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = ccol
            if j > 0: p.space_before = Pt(3)
            run = p.add_run()
            run.text = b
            run.font.name = FONT_BODY
            run.font.size = Pt(10.5)
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    # Bottom Flow Card: I/O Cycle
    io_flow_card = add_card(s12, 0.8, 5.2, 11.733, 1.6, "The Complete I/O Execution Cycle (Silberschatz Flow)", border_color=ACCENT_CYAN, bg_color=PILL_BG, accent_bar=ACCENT_CYAN)
    tb_io = s12.shapes.add_textbox(Inches(1.1), Inches(5.55), Inches(11.2), Inches(1.2))
    tf_io = tb_io.text_frame
    tf_io.word_wrap = True

    io_steps = [
        "1. APP calls read()/write()",
        "2. DEVICE DRIVER loads controller registers",
        "3. CONTROLLER transfers data to local buffer",
        "4. DMA transfers block to Main Memory",
        "5. INTERRUPT signals completion to CPU/OS"
    ]
    p_io1 = tf_io.paragraphs[0]
    p_io1.text = "   →   ".join(io_steps[:3])
    p_io1.font.name = FONT_BODY
    p_io1.font.size = Pt(11)
    p_io1.font.bold = True
    p_io1.font.color.rgb = TEXT_WHITE

    p_io2 = tf_io.add_paragraph()
    p_io2.text = "   →   " + "   →   ".join(io_steps[3:])
    p_io2.font.name = FONT_BODY
    p_io2.font.size = Pt(11)
    p_io2.font.bold = True
    p_io2.font.color.rgb = ACCENT_EMERALD
    p_io2.space_before = Pt(4)

    add_footer(s12)
    set_speaker_notes(
        s12,
        "How does the operating system coordinate with I/O devices? Each physical device is managed by a hardware **Device Controller** with its own local buffer storage. In the OS kernel, a corresponding **Device Driver** speaks the controller's language. For high-speed block devices like SSDs and network cards, transferring data byte-by-byte through the CPU would cause massive overhead. Silberschatz explains that **Direct Memory Access (DMA)** transfers entire blocks directly between the controller buffer and RAM, generating only one interrupt per block.",
        "Device Controller, Device Driver, local buffer storage, interrupt-driven I/O, and Direct Memory Access (DMA).",
        "Let's revisit multiprocessor systems and compare Symmetric Multiprocessing with NUMA in depth.",
        "Explain how DMA frees the CPU from byte-by-byte transfer duties."
    )

    # =========================================================================
    # SLIDE 13: MULTIPROCESSOR SYSTEMS & NUMA (Lochan)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_transition(s13)
    add_header(s13, 13, 15, "Act III: Multiprocessors, I/O & Architecture", "Lochan", "Multiprocessor Systems: SMP vs NUMA", "Architectural Trade-offs in Shared-Memory Multiprocessing (Silberschatz Comparison)")

    # Top: Comparative Table Card
    table_card = add_card(s13, 0.8, 1.8, 11.733, 2.7, "Direct Architectural Comparison: SMP vs NUMA", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    
    # Create Table Shape inside Card
    rows, cols = 4, 3
    left_t, top_t, width_t, height_t = Inches(1.1), Inches(2.2), Inches(11.1), Inches(2.1)
    tbl_shape = s13.shapes.add_table(rows, cols, left_t, top_t, width_t, height_t)
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
            if r_idx == 0:
                cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
            else:
                cell.fill.fore_color.rgb = RGBColor(17, 24, 39)
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_HEADING if r_idx == 0 else FONT_BODY
            p.font.size = Pt(10.5 if r_idx == 0 else 10)
            p.font.bold = True if r_idx == 0 or c_idx == 0 else False
            p.font.color.rgb = ACCENT_CYAN if r_idx == 0 else (TEXT_WHITE if c_idx == 0 else TEXT_MUTED)

    # Bottom Two Cards: Trade-off & OS Scheduling
    c_w = 5.7
    u1 = add_card(s13, 0.8, 4.7, c_w, 2.2, "The NUMA Latency Trade-Off", border_color=ACCENT_AMBER, accent_bar=ACCENT_AMBER)
    tb_u1 = s13.shapes.add_textbox(Inches(1.1), Inches(5.05), Inches(5.2), Inches(1.7))
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
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    u2 = add_card(s13, 6.8, 4.7, c_w, 2.2, "OS NUMA Memory & Thread Scheduling", border_color=ACCENT_EMERALD, accent_bar=ACCENT_EMERALD)
    tb_u2 = s13.shapes.add_textbox(Inches(7.1), Inches(5.05), Inches(5.2), Inches(1.7))
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
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s13)
    set_speaker_notes(
        s13,
        "Comparing SMP and NUMA side-by-side reveals a fundamental engineering trade-off. In pure Symmetric Multiprocessing, all CPUs share a single memory bus. While simple, bus contention caps scalability as processor counts increase. In NUMA, memory is partitioned across processor nodes. While this solves the bus bottleneck, it introduces variable latency: local access is fast, while remote access across the interconnect is slower. The operating system must be NUMA-aware to schedule threads on the same node where their memory lives.",
        "SMP vs NUMA comparison, uniform vs non-uniform memory access, and OS locality-aware scheduling.",
        "Beyond single machines, what happens when we connect independent computer systems together? This brings us to Clustered Systems.",
        "Guide the audience through the comparison table columns."
    )

    # =========================================================================
    # SLIDE 14: CLUSTERED SYSTEMS & ENVIRONMENTS (Lochan)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_transition(s14)
    add_header(s14, 14, 15, "Act III: Multiprocessors, I/O & Architecture", "Lochan", "Clustered Systems & Computing Environments", "Loosely Coupled Systems & Operating System Environments (Silberschatz Overview)")

    # Left: Clustered Systems Card
    c_w = 5.7
    cl1 = add_card(s14, 0.8, 1.8, c_w, 5.0, "Clustered Systems (Silberschatz Definition)", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_cl1 = s14.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.2), Inches(4.4))
    tf_cl1 = tb_cl1.text_frame
    tf_cl1.word_wrap = True

    pts_cl1 = [
        ("Loosely Coupled Nodes:", "Two or more individual computer systems/nodes connected via a high-speed network or LAN."),
        ("Shared Storage (SAN):", "Nodes typically share data across a Storage Area Network, providing uniform data access."),
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
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right: Computing Environments
    cl2 = add_card(s14, 6.8, 1.8, c_w, 5.0, "Diverse Computing Environments", border_color=ACCENT_INDIGO, accent_bar=ACCENT_INDIGO)
    tb_cl2 = s14.shapes.add_textbox(Inches(7.1), Inches(2.2), Inches(5.2), Inches(4.4))
    tf_cl2 = tb_cl2.text_frame
    tf_cl2.word_wrap = True

    pts_cl2 = [
        ("Traditional / Desktop Computing:", "Stand-alone PCs, laptops, and dedicated web/file servers running general-purpose multitasking OSes."),
        ("Mobile Computing:", "Smartphones and tablets with power-aware OSes (iOS/Android), wireless radios, and touch/sensor interfaces."),
        ("Distributed Systems:", "Networked collection of physically separate computational nodes presenting a unified system view."),
        ("Cloud Computing:", "Delivers computation, storage, and networking as an on-demand utility via virtualization across server clusters."),
        ("Embedded & Real-Time Systems:", "Specialized hardware (automotive, IoT, medical) where tasks must execute within rigid timing constraints.")
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
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    add_footer(s14)
    set_speaker_notes(
        s14,
        "While multiprocessor systems share a single chassis, **Clustered Systems** connect two or more independent computers together across a network, typically sharing a Storage Area Network (SAN). The textbook distinguishes asymmetric clustering—where one node acts as a hot-standby—and symmetric clustering—where all nodes run applications concurrently while monitoring each other for high availability. Silberschatz also outlines the spectrum of computing environments: traditional desktops, mobile systems, cloud infrastructures, and embedded real-time systems.",
        "Clustered systems (loosely coupled nodes, shared SAN, asymmetric vs symmetric) and computing environment categories.",
        "Now let's bring our entire presentation together into a final synthesis and open the floor for questions.",
        "Contrast clustered scale-out architecture with single-system multi-core scale-up architecture."
    )

    # =========================================================================
    # SLIDE 15: COMPLETE ARCHITECTURE & CONCLUSION + Q&A (All 3 Presenters)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_transition(s15)
    add_header(s15, 15, 15, "Synthesis & Conclusion", "V. Ram Charan · Vedhanth · Lochan", "Complete Architecture & Key Takeaways", "The Grand Synthesis & Interactive Discussion (Silberschatz Chapter 1 Summary)")

    # Left: Complete System Stack Box
    c_w = 5.7
    syn_card = add_card(s15, 0.8, 1.8, c_w, 5.0, "The Complete Computer-System Stack", border_color=ACCENT_CYAN, accent_bar=ACCENT_CYAN)
    tb_syn = s15.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.2), Inches(4.4))
    tf_syn = tb_syn.text_frame
    tf_syn.word_wrap = True

    stack_layers = [
        ("USERS", "People, programs, and machines requesting computation", ACCENT_CYAN),
        ("APPLICATION PROGRAMS", "Compilers, DBMS, Browsers solving user problems", ACCENT_INDIGO),
        ("OPERATING SYSTEM", "Process Management | Memory Management\nI/O Subsystem | Resource Allocation & Control", ACCENT_EMERALD),
        ("COMPUTER HARDWARE", "CPU / Multicore Cores | Main Memory (RAM)\nStorage Devices | I/O Controllers & Buses", ACCENT_AMBER)
    ]
    for i, (layer, desc, col) in enumerate(stack_layers):
        p = tf_syn.add_paragraph() if i > 0 else tf_syn.paragraphs[0]
        p.text = f"▼ {layer}\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = col
        if i > 0: p.space_before = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.size = Pt(10.5)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Top: 4 Core Takeaways
    tak_card = add_card(s15, 6.8, 1.8, c_w, 3.2, "Four Fundamental Takeaways", border_color=ACCENT_EMERALD, accent_bar=ACCENT_EMERALD)
    tb_tak = s15.shapes.add_textbox(Inches(7.1), Inches(2.2), Inches(5.2), Inches(2.7))
    tf_tak = tb_tak.text_frame
    tf_tak.word_wrap = True

    takeaways = [
        ("1. Hardware Provides Resources:", "CPU executes instructions; Memory holds active state; I/O connects peripherals."),
        ("2. The OS Coordinates & Controls:", "Acts as Resource Allocator (fairness/efficiency) and Control Program (safety)."),
        ("3. Interrupts & Syscalls Bridge Layers:", "Hardware interrupts signal devices; traps and syscalls allow safe kernel access."),
        ("4. Dual-Mode Protection Enforces Safety:", "Mode Bit (0/1) and privileged instructions isolate the kernel from user errors.")
    ]
    for i, (h, b) in enumerate(takeaways):
        p = tf_tak.add_paragraph() if i > 0 else tf_tak.paragraphs[0]
        p.text = h + " "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        if i > 0: p.space_before = Pt(3)
        run = p.add_run()
        run.text = b
        run.font.name = FONT_BODY
        run.font.size = Pt(10)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Bottom: Q&A / Thank You Card
    qa_card = add_card(s15, 6.8, 5.1, c_w, 1.7, "Thank You  •  Questions & Discussion", border_color=ACCENT_INDIGO, bg_color=PILL_BG, accent_bar=ACCENT_INDIGO)
    tb_qa = s15.shapes.add_textbox(Inches(7.1), Inches(5.35), Inches(5.2), Inches(1.3))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True
    
    p_qa1 = tf_qa.paragraphs[0]
    p_qa1.text = "PRESENTED BY:"
    p_qa1.font.name = FONT_HEADING
    p_qa1.font.size = Pt(10)
    p_qa1.font.bold = True
    p_qa1.font.color.rgb = ACCENT_CYAN

    p_qa2 = tf_qa.add_paragraph()
    p_qa2.text = "V. RAM CHARAN   •   VEDHANTH   •   LOCHAN"
    p_qa2.font.name = FONT_HEADING
    p_qa2.font.size = Pt(12)
    p_qa2.font.bold = True
    p_qa2.font.color.rgb = TEXT_WHITE
    p_qa2.space_before = Pt(2)

    p_qa3 = tf_qa.add_paragraph()
    p_qa3.text = "We welcome any questions on Computer System Architecture!"
    p_qa3.font.name = FONT_BODY
    p_qa3.font.size = Pt(10.5)
    p_qa3.font.italic = True
    p_qa3.font.color.rgb = ACCENT_EMERALD
    p_qa3.space_before = Pt(4)

    add_footer(s15)
    set_speaker_notes(
        s15,
        "To summarize our presentation: Users execute applications; applications request operating system services; the OS manages memory, processes, and I/O; and underlying hardware executes instructions under dual-mode protection. The four fundamental takeaways from Chapter 1 are: hardware provides resources, the OS coordinates them, interrupts link the software and hardware stacks, and dual-mode execution guarantees system protection. On behalf of Ram Charan, Vedhanth, and myself, thank you for your attention. We are now open for questions.",
        "Complete Chapter 1 synthesis: hardware resources, OS dual role, interrupt-driven operation, and hardware protection.",
        "End of presentation — open floor for Q&A.",
        "All three presenters step forward together, smile, and invite questions from the professor and classmates."
    )

    # Save PPTX Output
    out_pptx = os.path.join(ROOT_DIR, "computer_system_architecture.pptx")
    prs.save(out_pptx)
    print(f"Successfully generated 15-slide presentation: {out_pptx}")
    return out_pptx

if __name__ == "__main__":
    build_presentation()
