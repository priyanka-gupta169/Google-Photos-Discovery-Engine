"""
Refined Python script to generate the final 10-slide NextLeap Graduation Project Presentation:
'Google Photos Core Experience — AI-Powered Memory Retrieval'
Filename: NL_GooglePhotos_Core_Experience.pptx
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color System (Accessible, Colorblind-safe, Google-inspired)
    BG_COLOR = RGBColor(248, 249, 250)         # #F8F9FA Soft off-white canvas
    SURFACE_WHITE = RGBColor(255, 255, 255)    # #FFFFFF Card background
    BORDER_LIGHT = RGBColor(226, 232, 240)     # #E2E8F0 Subtle card border
    BORDER_SUBTLE = RGBColor(203, 213, 225)    # #CBD5E1 Divider border
    TEXT_MAIN = RGBColor(15, 23, 42)           # #0F172A Deep charcoal/navy
    TEXT_MUTED = RGBColor(71, 85, 105)         # #475569 Secondary text
    TEXT_SUBTLE = RGBColor(100, 116, 139)      # #64748B Subtitle/metadata

    GOOGLE_BLUE = RGBColor(26, 115, 232)       # #1A73E8 Action / Primary blue
    BLUE_TINT = RGBColor(232, 240, 254)        # #E8F0FE Chip light blue
    BLUE_BORDER = RGBColor(194, 220, 253)      # #C2DCFD Light blue border

    TEAL_ACCENT = RGBColor(13, 148, 136)       # #0D9488 AI / Insight Teal
    TEAL_TINT = RGBColor(204, 251, 241)        # #CCFBF1 Light Teal chip
    TEAL_BORDER = RGBColor(153, 246, 228)      # #99F6E4 Light teal border

    ORANGE_FRICTION = RGBColor(234, 88, 12)    # #EA580C Pain / Friction Orange
    ORANGE_TINT = RGBColor(255, 237, 213)      # #FFEDD5 Light Orange chip
    ORANGE_BORDER = RGBColor(254, 215, 170)    # #FED7AA Light orange border

    GREEN_SUCCESS = RGBColor(22, 163, 74)      # #16A34A Success Emerald
    GREEN_TINT = RGBColor(220, 252, 231)       # #DCFCE7 Light Emerald chip

    FONT_FAMILY = "Segoe UI"

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, tracker_text, title_text, subtitle_text=None, tracker_color=GOOGLE_BLUE):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.40), Inches(11.733), Inches(1.3))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        # Tracker category pill / super-title
        p_track = tf.paragraphs[0]
        p_track.text = tracker_text.upper()
        p_track.font.name = FONT_FAMILY
        p_track.font.size = Pt(11)
        p_track.font.bold = True
        p_track.font.color.rgb = tracker_color
        p_track.space_after = Pt(4)
        
        # Message-led slide title
        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = FONT_FAMILY
        p_title.font.size = Pt(25)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN
        
        # Context subtitle
        if subtitle_text:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.name = FONT_FAMILY
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED
            p_sub.space_before = Pt(3)

    def add_card(slide, left, top, width, height, bg_color=SURFACE_WHITE, border_color=BORDER_LIGHT, border_width=1):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(border_width)
        else:
            card.line.fill.background()
        return card

    # =========================================================================
    # SLIDE 1: HERO & STRATEGIC PROBLEM HOOK
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    add_header(
        s1,
        "Google Photos Core Experience · Product Discovery Case Study",
        "Users Remember the Moment — Not the Exact Search Terms",
        "Addressing core retrieval friction in personal cloud archives through AI-assisted episodic memory interpretation"
    )

    # Left Hero Narrative Card (Width: 6.8 in)
    add_card(s1, Inches(0.8), Inches(1.85), Inches(6.8), Inches(5.15))
    tb_l = s1.shapes.add_textbox(Inches(1.1), Inches(2.05), Inches(6.2), Inches(4.75))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0

    p = tf_l.paragraphs[0]
    p.text = "THE RETRIEVAL BREAKDOWN"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(8)

    p = tf_l.add_paragraph()
    p.text = "“I remember the moment vividly, but I don't know what words to search.”"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(12)

    p = tf_l.add_paragraph()
    p.text = (
        "Personal photo libraries grow into tens of thousands of items over years. When users want to find "
        "a specific past moment, human memory recalls episodic context — people present, general locations, "
        "approximate seasons, and emotional atmosphere."
    )
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(10)

    p = tf_l.add_paragraph()
    p.text = (
        "However, conventional search interfaces rely heavily on exact dates or isolated keywords. When vague searches "
        "fail, users fall back to manual timeline scrubbing or abandon the retrieval task entirely."
    )
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(16)

    # Goal Callout Box inside left card
    add_card(s1, Inches(1.1), Inches(4.9), Inches(6.2), Inches(1.85), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tb_g = s1.shapes.add_textbox(Inches(1.3), Inches(5.05), Inches(5.8), Inches(1.55))
    tf_g = tb_g.text_frame
    tf_g.word_wrap = True
    tf_g.margin_left = tf_g.margin_top = tf_g.margin_right = tf_g.margin_bottom = 0

    p = tf_g.paragraphs[0]
    p.text = "CORE BUSINESS GOAL"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(4)

    p = tf_g.add_paragraph()
    p.text = "Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(4)

    p = tf_g.add_paragraph()
    p.text = "Domain: Google Photos Core Retrieval Experience | Product Discovery & Validation"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Right Hero Card — Human Recall vs. Search Engine Mismatch (Width: 4.733 in)
    add_card(s1, Inches(7.8), Inches(1.85), Inches(4.733), Inches(5.15))
    tb_r = s1.shapes.add_textbox(Inches(8.1), Inches(2.05), Inches(4.133), Inches(1.0))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0

    p = tf_r.paragraphs[0]
    p.text = "THE COGNITIVE GAP"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(4)

    p = tf_r.add_paragraph()
    p.text = "Human Memory vs. Conventional Search"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    # Human Memory Fragment (Adjusted top to 2.95 for perfect clearance)
    add_card(s1, Inches(8.1), Inches(2.95), Inches(4.133), Inches(1.6), bg_color=TEAL_TINT, border_color=TEAL_BORDER)
    tb_m = s1.shapes.add_textbox(Inches(8.25), Inches(3.05), Inches(3.833), Inches(1.4))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_top = tf_m.margin_right = tf_m.margin_bottom = 0

    p = tf_m.paragraphs[0]
    p.text = "HUMAN EPISODIC MEMORY (MULTI-CUE)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(4)

    cues = [
        "• Companion: Rohan (Friend)",
        "• Setting: Anjuna Beach, Goa at sunset",
        "• Fuzzy Time: ~2-3 years ago (College trip)",
        "• Visual Cue: Ocean waves, golden sky, drinks"
    ]
    for c in cues:
        p = tf_m.add_paragraph()
        p.text = c
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN

    # Collides with indicator
    p_vs = s1.shapes.add_textbox(Inches(8.1), Inches(4.62), Inches(4.133), Inches(0.28))
    p_vs.text_frame.margin_left = p_vs.text_frame.margin_top = 0
    p_vs_p = p_vs.text_frame.paragraphs[0]
    p_vs_p.text = "▼  COLLIDES WITH  ▼"
    p_vs_p.font.name = FONT_FAMILY
    p_vs_p.font.size = Pt(9.5)
    p_vs_p.font.bold = True
    p_vs_p.font.color.rgb = ORANGE_FRICTION
    p_vs_p.alignment = PP_ALIGN.CENTER

    # Rigid System Box (Adjusted top to 4.95)
    add_card(s1, Inches(8.1), Inches(4.95), Inches(4.133), Inches(1.85), bg_color=ORANGE_TINT, border_color=ORANGE_BORDER)
    tb_s = s1.shapes.add_textbox(Inches(8.25), Inches(5.05), Inches(3.833), Inches(1.65))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0

    p = tf_s.paragraphs[0]
    p.text = "CONVENTIONAL SEARCH FRICTION"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(4)

    sys_frictions = [
        "• Rigid Exact Match: Requires date or single keyword",
        "• Trial-and-Error: Modifying query resets context",
        "• Workaround Fallback: 65% scroll timeline endlessly",
        "• High Drop-off: 70.6% abandon search sessions"
    ]
    for sf in sys_frictions:
        p = tf_s.add_paragraph()
        p.text = sf
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN


    # =========================================================================
    # SLIDE 2: METRIC DECOMPOSITION (THE SIX-STAGE JOURNEY)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(
        s2,
        "Part 2 · Metric Decomposition & Funnel Analysis",
        "Successful Retrieval is a Six-Stage Journey, Not a Single Search",
        "Deconstructing vague-memory photo retrieval reveals that success depends on iterative cue translation"
    )

    # 6 Funnel Cards across width
    stages = [
        {
            "num": "01",
            "name": "Memory\nFormulation",
            "prob": "P(E₁)",
            "desc": "User recalls fuzzy episodic fragments (person, place, vibe)",
            "stat": "94.1% no exact date"
        },
        {
            "num": "02",
            "name": "Candidate\nGeneration",
            "prob": "P(E₂)",
            "desc": "Translates memory into initial search query",
            "stat": "86.1% relevance failure"
        },
        {
            "num": "03",
            "name": "Visual\nInspection",
            "prob": "P(E₃)",
            "desc": "Scans image grid to evaluate top candidate matches",
            "stat": "3+ searches required"
        },
        {
            "num": "04",
            "name": "Secondary\nRefinement",
            "prob": "P(E₄)",
            "desc": "Adds or adjusts cues to narrow down results",
            "stat": "84.7% refinement issue"
        },
        {
            "num": "05",
            "name": "Workaround\nFallback",
            "prob": "P(E₅)",
            "desc": "Resorts to manual scrubbing or external apps",
            "stat": "65.3% scrub timeline"
        },
        {
            "num": "06",
            "name": "Goal\nCompletion",
            "prob": "P(E₆)",
            "desc": "Locates and confirms the intended photo",
            "stat": "69.4% failed retrieval"
        }
    ]

    card_w = Inches(1.85)
    card_gap = Inches(0.12)
    start_x = Inches(0.8)

    for i, st in enumerate(stages):
        x = start_x + i * (card_w + card_gap)
        bg = SURFACE_WHITE
        border = BORDER_LIGHT
        if i in [1, 3]:  # Stages where breakdown occurs most
            bg = ORANGE_TINT
            border = ORANGE_BORDER
        elif i == 5:
            bg = BLUE_TINT
            border = BLUE_BORDER

        add_card(s2, x, Inches(1.85), card_w, Inches(3.2), bg_color=bg, border_color=border)
        
        tb_st = s2.shapes.add_textbox(x + Inches(0.12), Inches(1.95), card_w - Inches(0.24), Inches(3.0))
        tf_st = tb_st.text_frame
        tf_st.word_wrap = True
        tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0
        
        p = tf_st.paragraphs[0]
        p.text = f"STAGE {st['num']}  ·  {st['prob']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = GOOGLE_BLUE if i not in [1, 3] else ORANGE_FRICTION
        p.space_after = Pt(4)

        p = tf_st.add_paragraph()
        p.text = st['name']
        p.font.name = FONT_FAMILY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(8)

        p = tf_st.add_paragraph()
        p.text = st['desc']
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(10)

        p = tf_st.add_paragraph()
        p.text = f"Observed Signal:\n{st['stat']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

    # Bottom Evidence & Insight Panel (2 Columns)
    add_card(s2, Inches(0.8), Inches(5.2), Inches(6.8), Inches(1.8), bg_color=SURFACE_WHITE)
    tb_b1 = s2.shapes.add_textbox(Inches(1.0), Inches(5.35), Inches(6.4), Inches(1.5))
    tf_b1 = tb_b1.text_frame
    tf_b1.word_wrap = True
    tf_b1.margin_left = tf_b1.margin_top = tf_b1.margin_right = tf_b1.margin_bottom = 0

    p = tf_b1.paragraphs[0]
    p.text = "EVIDENCE FROM 72 RETRIEVAL-FRICTION RECORDS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(6)

    stats_line = (
        "• 86.1% experienced candidate relevance failure during initial searches (Stage 2/3)\n"
        "• 84.7% encountered search refinement breakdown when trying to iterate (Stage 4)\n"
        "• 65.3% abandoned search to scrub timeline manually; 34.7% searched chat apps (Stage 5)"
    )
    p = tf_b1.add_paragraph()
    p.text = stats_line
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MAIN

    # Bottom Right Product Insight
    add_card(s2, Inches(7.8), Inches(5.2), Inches(4.733), Inches(1.8), bg_color=TEAL_TINT, border_color=TEAL_BORDER)
    tb_b2 = s2.shapes.add_textbox(Inches(8.0), Inches(5.35), Inches(4.333), Inches(1.5))
    tf_b2 = tb_b2.text_frame
    tf_b2.word_wrap = True
    tf_b2.margin_left = tf_b2.margin_top = tf_b2.margin_right = tf_b2.margin_bottom = 0

    p = tf_b2.paragraphs[0]
    p.text = "CRITICAL PRODUCT INSIGHT"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(4)

    p = tf_b2.add_paragraph()
    p.text = "Retrieval is a journey of signal translation, not a single query event."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(4)

    p = tf_b2.add_paragraph()
    p.text = (
        "If the system cannot help users translate fuzzy memory cues into structured retrieval filters "
        "and support additive refinement, the entire retrieval funnel collapses."
    )
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 3: AI DISCOVERY ENGINE WORKFLOW & EVIDENCE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(
        s3,
        "Part 1 · AI Discovery Engine Methodology & Public Evidence",
        "Public Evidence Showed That Relevance and Refinement Are Where Retrieval Repeatedly Breaks",
        "Analyzing 74 authentic public records through an AI-powered discovery pipeline revealed systemic friction points"
    )

    # 6-Step Pipeline Across Top
    pipe_steps = [
        ("01", "Feedback\nIngestion", "74 authentic user posts (Reddit, Google Help, X)", GOOGLE_BLUE),
        ("02", "AI Semantic\nClassification", "Zero-shot intent, stage & emotion tagging", GOOGLE_BLUE),
        ("03", "Behavioral\nExtraction", "Identified workarounds (scrubbing, chat logs)", ORANGE_FRICTION),
        ("04", "HDBSCAN\nClustering", "High-dimensional embeddings → 17 clusters", TEAL_ACCENT),
        ("05", "Opportunity\nMatrix", "Ranked frequency vs. user frustration severity", TEAL_ACCENT),
        ("06", "AI Synthesis\nFindings", "8 synthesized product opportunity findings", GREEN_SUCCESS),
    ]

    pw = Inches(1.85)
    pgap = Inches(0.12)
    for i, (pnum, pname, psub, pcol) in enumerate(pipe_steps):
        x = start_x + i * (pw + pgap)
        add_card(s3, x, Inches(1.85), pw, Inches(2.2), bg_color=SURFACE_WHITE)
        tb_p = s3.shapes.add_textbox(x + Inches(0.12), Inches(1.95), pw - Inches(0.24), Inches(2.0))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        tf_p.margin_left = tf_p.margin_top = tf_p.margin_right = tf_p.margin_bottom = 0
        
        p = tf_p.paragraphs[0]
        p.text = f"STEP {pnum}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = pcol
        p.space_after = Pt(4)

        p = tf_p.add_paragraph()
        p.text = pname
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(6)

        p = tf_p.add_paragraph()
        p.text = psub
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Bottom Half: Data Findings & Discovery Matrix
    # Bottom Left: Observed Outcomes Card
    add_card(s3, Inches(0.8), Inches(4.25), Inches(5.8), Inches(2.75), bg_color=SURFACE_WHITE)
    tb_o = s3.shapes.add_textbox(Inches(1.05), Inches(4.4), Inches(5.3), Inches(2.45))
    tf_o = tb_o.text_frame
    tf_o.word_wrap = True
    tf_o.margin_left = tf_o.margin_top = tf_o.margin_right = tf_o.margin_bottom = 0

    p = tf_o.paragraphs[0]
    p.text = "OBSERVED OUTCOMES IN PUBLIC EVIDENCE (72 FRICTION RECORDS)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(8)

    stats_outcomes = [
        ("69.4%", "Failed Retrieval", "User could not find intended photo"),
        ("9.7%", "Search Abandoned", "Exited app before completion"),
        ("18.1%", "Successful Retrieval", "Located photo after high effort"),
        ("2.8%", "Partial Match", "Located related event, not exact photo")
    ]
    for pct, lbl, sub in stats_outcomes:
        p = tf_o.add_paragraph()
        p.text = f"• {pct} — {lbl}: {sub}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

    p = tf_o.add_paragraph()
    p.text = "*Note: Across analyzed public records; directional evidence of friction, not statistically representative of all users."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.italic = True
    p.font.color.rgb = TEXT_SUBTLE
    p.space_before = Pt(6)

    # Bottom Right: Top Synthesized Problem Findings
    add_card(s3, Inches(6.8), Inches(4.25), Inches(5.733), Inches(2.75), bg_color=SURFACE_WHITE)
    tb_syn = s3.shapes.add_textbox(Inches(7.05), Inches(4.4), Inches(5.233), Inches(2.45))
    tf_syn = tb_syn.text_frame
    tf_syn.word_wrap = True
    tf_syn.margin_left = tf_syn.margin_top = tf_syn.margin_right = tf_syn.margin_bottom = 0

    p = tf_syn.paragraphs[0]
    p.text = "8 SYNTHESIZED PRODUCT FINDINGS · TOP 3 PATTERNS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(8)

    syn_items = [
        ("1. Multi-Cue Relevance Collapse (86.1%)", "When users enter compound descriptions (person + approximate place), search returns irrelevant items or zero results, forcing single-term queries."),
        ("2. Destructive Query Refinement (84.7%)", "Adding or editing words completely resets candidate results rather than progressively filtering down the existing pool."),
        ("3. Opaque Relevance Ranking (71.2%)", "Users cannot determine why specific photos appear or why their intended photo was excluded, creating black-box frustration.")
    ]
    for s_title, s_desc in syn_items:
        p = tf_syn.add_paragraph()
        p.text = s_title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(1)

        p = tf_syn.add_paragraph()
        p.text = s_desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(6)


    # =========================================================================
    # SLIDE 4: PRIMARY USER RESEARCH (N=17)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(
        s4,
        "Part 3 · Primary User Research & Behavioral Evidence (N=17)",
        "17 Users Confirmed That People Remember Context — Not Exact Search Terms",
        "Primary research validates that episodic human recall relies on companions, settings, and events, not dates"
    )

    # 4 Large Stat Cards
    stat_cards = [
        ("94.1%", "Searched Without Exact Date", "16 of 17 users recall approximate eras or seasons, never specific calendar dates", ORANGE_FRICTION),
        ("88.2%", "Attempted ≥3 Searches", "15 of 17 users engage in repeated trial-and-error reformulations per session", ORANGE_FRICTION),
        ("94.1%", "Searched Outside Google Photos", "16 of 17 use external workarounds (WhatsApp chats, Instagram) to find photo clues", GOOGLE_BLUE),
        ("70.6%", "Abandoned Retrieval Sessions", "12 of 17 users report frequently or sometimes abandoning searches due to fatigue", ORANGE_FRICTION),
    ]

    sc_w = Inches(2.8)
    sc_gap = Inches(0.18)
    for i, (val, title, desc, col) in enumerate(stat_cards):
        x = start_x + i * (sc_w + sc_gap)
        add_card(s4, x, Inches(1.85), sc_w, Inches(2.3), bg_color=SURFACE_WHITE)
        tb_sc = s4.shapes.add_textbox(x + Inches(0.15), Inches(1.95), sc_w - Inches(0.3), Inches(2.1))
        tf_sc = tb_sc.text_frame
        tf_sc.word_wrap = True
        tf_sc.margin_left = tf_sc.margin_top = tf_sc.margin_right = tf_sc.margin_bottom = 0
        
        p = tf_sc.paragraphs[0]
        p.text = val
        p.font.name = FONT_FAMILY
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)

        p = tf_sc.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(4)

        p = tf_sc.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED

    # Bottom Left: The Episodic Memory Fingerprint (Cue Frequencies)
    add_card(s4, Inches(0.8), Inches(4.35), Inches(6.4), Inches(2.65), bg_color=SURFACE_WHITE)
    tb_fp = s4.shapes.add_textbox(Inches(1.05), Inches(4.5), Inches(5.9), Inches(2.35))
    tf_fp = tb_fp.text_frame
    tf_fp.word_wrap = True
    tf_fp.margin_left = tf_fp.margin_top = tf_fp.margin_right = tf_fp.margin_bottom = 0

    p = tf_fp.paragraphs[0]
    p.text = "THE EPISODIC MEMORY FINGERPRINT (WHAT USERS RECALL)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(8)

    cues_data = [
        ("Person / Companion", "76.5% (13/17)", "Who was with them is the strongest emotional anchor"),
        ("Approximate Time", "47.1% (8/17)", "Relative timeframes: 'around 3 years ago', 'college days'"),
        ("Location / Setting", "47.1% (8/17)", "Broad geographic or contextual place: 'Goa', 'beach', 'cafe'"),
        ("Activity / Event", "41.2% (7/17)", "What was taking place: 'sunset', 'wedding', 'birthday dinner'")
    ]
    for c_name, c_pct, c_sub in cues_data:
        p = tf_fp.add_paragraph()
        p.text = f"• {c_name} — {c_pct}: {c_sub}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(4)

    # Bottom Right: Authentic User Quotes (Search Blockers)
    add_card(s4, Inches(7.4), Inches(4.35), Inches(5.133), Inches(2.65), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tb_bq = s4.shapes.add_textbox(Inches(7.65), Inches(4.5), Inches(4.633), Inches(2.35))
    tf_bq = tb_bq.text_frame
    tf_bq.word_wrap = True
    tf_bq.margin_left = tf_bq.margin_top = tf_bq.margin_right = tf_bq.margin_bottom = 0

    p = tf_bq.paragraphs[0]
    p.text = "AUTHENTIC USER SEARCH BLOCKERS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(8)

    quotes = [
        "“I don't know what words to search. I just remember who I was with and roughly where.”",
        "“I don't remember the exact date, so I end up having to scroll manually through years of photos.”",
        "“When search doesn't show it, I check my old WhatsApp messages to see when we took the photo.”"
    ]
    for q in quotes:
        p = tf_bq.add_paragraph()
        p.text = q
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(6)


    # =========================================================================
    # SLIDE 5: TARGET SEGMENT & ROOT-CAUSE HYPOTHESIS
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(
        s5,
        "Part 4 · Target Segment, Root Cause & Value Proposition",
        "The Episodic Personal Memory Searcher Needs Help Turning Fuzzy Cues Into a Retrieval Path",
        "Defining the target archetype, formulating the evidence-bound root cause, and articulating dual value"
    )

    # Left Column: Persona Profile
    add_card(s5, Inches(0.8), Inches(1.85), Inches(5.6), Inches(5.15), bg_color=SURFACE_WHITE)
    tb_p5 = s5.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(5.1), Inches(4.75))
    tf_p5 = tb_p5.text_frame
    tf_p5.word_wrap = True
    tf_p5.margin_left = tf_p5.margin_top = tf_p5.margin_right = tf_p5.margin_bottom = 0

    p = tf_p5.paragraphs[0]
    p.text = "TARGET USER SEGMENT ARCHETYPE"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(4)

    p = tf_p5.add_paragraph()
    p.text = "The Episodic Personal Memory Searcher"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(12)

    persona_traits = [
        ("Library Scale", "Holds 5,000+ personal photos accumulated over years across devices."),
        ("Memory Retrieval Style", "Remembers meaningful moments episodically — emotional anchors, companions, fuzzy seasons, and visual settings."),
        ("Knowledge Deficit", "Does NOT remember exact dates, specific months, or machine filenames."),
        ("Observed Search Behavior", "Attempts 3+ query reformulations; struggles to formulate search syntax."),
        ("Painful Fallback", "Resorts to manual timeline scrubbing (65.3%) or external chat app searching (34.7%) when initial queries fail.")
    ]
    for pt_title, pt_desc in persona_traits:
        p = tf_p5.add_paragraph()
        p.text = f"• {pt_title}: {pt_desc}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(8)

    # Right Column: Root Cause Hypothesis & Value Proposition
    # Top Right: Root-Cause Hypothesis Box
    add_card(s5, Inches(6.6), Inches(1.85), Inches(5.933), Inches(2.5), bg_color=ORANGE_TINT, border_color=ORANGE_BORDER)
    tb_rc = s5.shapes.add_textbox(Inches(6.85), Inches(2.05), Inches(5.433), Inches(2.1))
    tf_rc = tb_rc.text_frame
    tf_rc.word_wrap = True
    tf_rc.margin_left = tf_rc.margin_top = tf_rc.margin_right = tf_rc.margin_bottom = 0

    p = tf_rc.paragraphs[0]
    p.text = "EVIDENCE-BOUND ROOT-CAUSE HYPOTHESIS"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(6)

    p = tf_rc.add_paragraph()
    p.text = "“The observed retrieval experience does not consistently help users translate multiple fuzzy memory cues into an effective search or refinement path.”"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(8)

    p = tf_rc.add_paragraph()
    p.text = "*Formulated as a user-experience hypothesis grounded in observed research, without claiming internal Google technical or ranking defects."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.italic = True
    p.font.color.rgb = TEXT_MUTED

    # Bottom Right: Value Proposition (User vs. Business)
    add_card(s5, Inches(6.6), Inches(4.55), Inches(5.933), Inches(2.45), bg_color=SURFACE_WHITE)
    tb_vp = s5.shapes.add_textbox(Inches(6.85), Inches(4.7), Inches(5.433), Inches(2.15))
    tf_vp = tb_vp.text_frame
    tf_vp.word_wrap = True
    tf_vp.margin_left = tf_vp.margin_top = tf_vp.margin_right = tf_vp.margin_bottom = 0

    p = tf_vp.paragraphs[0]
    p.text = "DUAL VALUE PROPOSITION"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(6)

    p = tf_vp.add_paragraph()
    p.text = "User Value: Emotional Reassurance & Frictionless Recovery"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(2)

    p = tf_vp.add_paragraph()
    p.text = "Restores confidence in finding cherished personal memories; replaces exhausting manual scrolling with guided, natural language cue refinement."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(8)

    p = tf_vp.add_paragraph()
    p.text = "Business Value: Retention & Core Archive Utility"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(2)

    p = tf_vp.add_paragraph()
    p.text = "Reinforces Google Photos as the indispensable personal archive, driving Google One storage retention and recurring high-intent engagement."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 6: THE MVP SOLUTION ARCHITECTURE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(
        s6,
        "Part 5 · AI-Native MVP Architecture & Workflow",
        "The MVP Turns an Incomplete Memory Into Searchable Cues — Then Helps the User Refine",
        "Controlled research prototype combining 8-dimensional cue extraction, explainable ranking, and additive refinement"
    )

    # Left Column: Solution Architecture Flow (5.8 in)
    add_card(s6, Inches(0.8), Inches(1.85), Inches(5.8), Inches(5.15), bg_color=SURFACE_WHITE)
    tb_mvp = s6.shapes.add_textbox(Inches(1.05), Inches(2.05), Inches(5.3), Inches(4.75))
    tf_mvp = tb_mvp.text_frame
    tf_mvp.word_wrap = True
    tf_mvp.margin_left = tf_mvp.margin_top = tf_mvp.margin_right = tf_mvp.margin_bottom = 0

    p = tf_mvp.paragraphs[0]
    p.text = "AI MEMORY RETRIEVAL ASSISTANT WORKFLOW"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(8)

    flow_steps = [
        ("1. Freeform Episodic Memory Input", "User types natural language memory: 'I remember a photo with Rohan at Anjuna beach around sunset about 3 years ago.'"),
        ("2. 8-Facet Cue Interpretation", "NLP extracts structured signals: Person (Rohan), Location (Goa/Anjuna), Time (~2023), Activity (Sunset), Objects & Visuals."),
        ("3. Transparent Explainability", "Displays 'What I Understood' cue pills and 'Why this result?' rationale bullets showing exact match drivers for each photo."),
        ("4. Iterative Additive Refinement", "Users layer incremental clues ('+with evening drinks') or click '✕ Not this photo' to penalize visual distractors without resetting context."),
        ("5. Fast Candidate Convergence", "Dynamically updates candidate ranks, successfully surfacing the target photo in the top spots.")
    ]
    for fs_title, fs_desc in flow_steps:
        p = tf_mvp.add_paragraph()
        p.text = fs_title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(1)

        p = tf_mvp.add_paragraph()
        p.text = fs_desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

    # Right Column: UI Screenshot & Prototype Boundaries (5.733 in)
    img_path = "presentation_assets/mvp_ui_card_perfect.png"
    if os.path.exists(img_path):
        pic = s6.shapes.add_picture(img_path, Inches(6.8), Inches(1.85), width=Inches(5.733))
        pic.line.color.rgb = BORDER_LIGHT
        pic.line.width = Pt(1)

    # Prototype Boundaries Box at bottom right
    add_card(s6, Inches(6.8), Inches(5.45), Inches(5.733), Inches(1.55), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tb_pb = s6.shapes.add_textbox(Inches(7.0), Inches(5.55), Inches(5.333), Inches(1.35))
    tf_pb = tb_pb.text_frame
    tf_pb.word_wrap = True
    tf_pb.margin_left = tf_pb.margin_top = tf_pb.margin_right = tf_pb.margin_bottom = 0

    p = tf_pb.paragraphs[0]
    p.text = "CONTROLLED RESEARCH PROTOTYPE BOUNDARIES"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(2)

    pb_points = (
        "• Tested against a 40-photo curated representative dataset with diverse categories.\n"
        "• Evaluates memory-to-cue translation and refinement mechanics without live account sync.\n"
        "• Provides proof-of-concept validation for additive memory interpretation."
    )
    p = tf_pb.add_paragraph()
    p.text = pb_points
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MAIN


    # =========================================================================
    # SLIDE 7: REAL USER TESTING (N=4) & QUALITATIVE INSIGHT
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(
        s7,
        "Part 6 · Usability Testing & Core Product Learning (N=4)",
        "Users Found Refinement Useful — But Needed Help Knowing What Clue to Add Next",
        "Controlled usability testing of the deployed prototype demonstrates high satisfaction while revealing the next product vector"
    )

    # 5 Usability Scorecard Badges Across Top
    test_metrics = [
        ("4.75 / 5.0", "Memory Description Ease", "Users felt effortless articulating memories naturally", GREEN_SUCCESS),
        ("75%", "AI Understanding Positive", "3 of 4 participants confirmed AI accurately parsed their intent", GOOGLE_BLUE),
        ("4.00 / 5.0", "Candidate Result Relevance", "75% rated retrieved photo relevance 4 or 5 out of 5", GOOGLE_BLUE),
        ("4.25 / 5.0", "Refinement Ease", "Additive clue layering was intuitive and straightforward", GREEN_SUCCESS),
        ("100%", "Explanations Clear", "3 Yes, 1 Somewhat: all found rationale at least somewhat clear", TEAL_ACCENT),
    ]

    tm_w = Inches(2.23)
    tm_gap = Inches(0.14)
    for i, (val, title, desc, col) in enumerate(test_metrics):
        x = start_x + i * (tm_w + tm_gap)
        add_card(s7, x, Inches(1.85), tm_w, Inches(2.0), bg_color=SURFACE_WHITE)
        tb_tm = s7.shapes.add_textbox(x + Inches(0.12), Inches(1.95), tm_w - Inches(0.24), Inches(1.8))
        tf_tm = tb_tm.text_frame
        tf_tm.word_wrap = True
        tf_tm.margin_left = tf_tm.margin_top = tf_tm.margin_right = tf_tm.margin_bottom = 0
        
        p = tf_tm.paragraphs[0]
        p.text = val
        p.font.name = FONT_FAMILY
        p.font.size = Pt(30)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)

        p = tf_tm.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(3)

        p = tf_tm.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    # Centerpiece Qualitative Quote Banner (The Big Learning)
    add_card(s7, Inches(0.8), Inches(4.05), Inches(11.733), Inches(1.5), bg_color=ORANGE_TINT, border_color=ORANGE_BORDER)
    tb_q = s7.shapes.add_textbox(Inches(1.1), Inches(4.15), Inches(11.133), Inches(1.3))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    tf_q.margin_left = tf_q.margin_top = tf_q.margin_right = tf_q.margin_bottom = 0

    p = tf_q.paragraphs[0]
    p.text = "THE CENTERPIECE QUALITATIVE LEARNING (PARTICIPANT P3)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(4)

    p = tf_q.add_paragraph()
    p.text = "“The idea of refining the search was quite useful, but I had to figure out what kind of clue to add next.”"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(19)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(4)

    p = tf_q.add_paragraph()
    p.text = "Secondary Participant Feedback: Users requested smarter follow-up questions when results were ambiguous."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Bottom Strategic Takeaway Card
    add_card(s7, Inches(0.8), Inches(5.75), Inches(11.733), Inches(1.25), bg_color=TEAL_TINT, border_color=TEAL_BORDER)
    tb_st = s7.shapes.add_textbox(Inches(1.1), Inches(5.85), Inches(11.133), Inches(1.05))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True
    tf_st.margin_left = tf_st.margin_top = tf_st.margin_right = tf_st.margin_bottom = 0

    p = tf_st.paragraphs[0]
    p.text = "STRATEGIC PRODUCT LEARNING: FROM REACTIVE TO PROACTIVE REFINEMENT"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(3)

    p = tf_st.add_paragraph()
    p.text = (
        "While reactive refinement (user typing clues) is effective, the next breakthrough is proactive AI guidance. "
        "When candidates remain broad, the AI should identify remaining ambiguity across top results and prompt the user "
        "with targeted recognition questions ('Was it indoors or outdoors?', 'Who else was in the photo?')."
    )
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEXT_MAIN


    # =========================================================================
    # SLIDE 8: SUCCESS METRICS & MEASUREMENT FRAMEWORK
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(
        s8,
        "Part 7 · Success Metric Framework & Measurement Hierarchy",
        "Success Must Measure Both Retrieval Outcome and Progress Across the Journey",
        "A 3-tier measurement framework connecting core business impact, user journey progress, and system diagnostics"
    )

    # Tier 1: Primary Outcome Metric Banner
    add_card(s8, Inches(0.8), Inches(1.85), Inches(11.733), Inches(1.45), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tb_t1 = s8.shapes.add_textbox(Inches(1.1), Inches(1.95), Inches(11.133), Inches(1.25))
    tf_t1 = tb_t1.text_frame
    tf_t1.word_wrap = True
    tf_t1.margin_left = tf_t1.margin_top = tf_t1.margin_right = tf_t1.margin_bottom = 0

    p = tf_t1.paragraphs[0]
    p.text = "PRIMARY OUTCOME METRIC (NORTH STAR)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(2)

    p = tf_t1.add_paragraph()
    p.text = "Vague Retrieval Success Rate (VRSR)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(2)

    p = tf_t1.add_paragraph()
    p.text = (
        "Percentage of vague-memory retrieval sessions where the user successfully locates their intended photo without "
        "resorting to manual timeline scrubbing or external workarounds. (Reliable benchmark to be established via large-scale evaluation)."
    )
    p.font.name = FONT_FAMILY
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    # Tier 2: Leading Indicators (5 Cards)
    add_card(s8, Inches(0.8), Inches(3.45), Inches(11.733), Inches(1.75), bg_color=SURFACE_WHITE)
    tb_t2 = s8.shapes.add_textbox(Inches(1.1), Inches(3.55), Inches(11.133), Inches(1.55))
    tf_t2 = tb_t2.text_frame
    tf_t2.word_wrap = True
    tf_t2.margin_left = tf_t2.margin_top = tf_t2.margin_right = tf_t2.margin_bottom = 0

    p = tf_t2.paragraphs[0]
    p.text = "LEADING PROGRESS INDICATORS (USER JOURNEY ADVANCEMENT)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(6)

    leading_metrics = [
        ("AMUR", "AI Memory Understanding Rate", "% sessions where user confirms AI parsed memory accurately"),
        ("CRR@3", "Candidate Relevance Rate", "% of top-3 retrieved photos matching user memory context"),
        ("RSR", "Refinement Success Rate", "% of added clues that successfully increase candidate precision"),
        ("QRV", "Query Reformulation Velocity", "Average steps/seconds needed to converge onto target photo"),
        ("TSR", "Time to Success", "Active duration from initial prompt to photo selection")
    ]
    lm_w = Inches(2.15)
    lm_gap = Inches(0.18)
    for i, (code, title, desc) in enumerate(leading_metrics):
        lx = Inches(1.1) + i * (lm_w + lm_gap)
        tb_lm = s8.shapes.add_textbox(lx, Inches(3.85), lm_w, Inches(1.2))
        tf_lm = tb_lm.text_frame
        tf_lm.word_wrap = True
        tf_lm.margin_left = tf_lm.margin_top = tf_lm.margin_right = tf_lm.margin_bottom = 0
        
        p = tf_lm.paragraphs[0]
        p.text = code
        p.font.name = FONT_FAMILY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEAL_ACCENT
        
        p = tf_lm.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        
        p = tf_lm.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED

    # Tier 3: Diagnostic Metrics (5 Cards)
    add_card(s8, Inches(0.8), Inches(5.35), Inches(11.733), Inches(1.65), bg_color=SURFACE_WHITE)
    tb_t3 = s8.shapes.add_textbox(Inches(1.1), Inches(5.45), Inches(11.133), Inches(1.45))
    tf_t3 = tb_t3.text_frame
    tf_t3.word_wrap = True
    tf_t3.margin_left = tf_t3.margin_top = tf_t3.margin_right = tf_t3.margin_bottom = 0

    p = tf_t3.paragraphs[0]
    p.text = "DIAGNOSTIC & GUARDRAIL METRICS (SYSTEM HEALTH)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ORANGE_FRICTION
    p.space_after = Pt(6)

    diag_metrics = [
        ("ZHQR", "Zero-Hit Query Rate", "% queries returning 0 results (identifies vocabulary gaps)"),
        ("RSR-Stall", "Refinement Stall Rate", "% sessions where added clues fail to narrow down candidate pool"),
        ("EER", "Evaluation Effort Rate", "Excessive image clicks/enlargements indicating low confidence"),
        ("TFTR", "Timeline Fallback Rate", "% users abandoning search bar for manual date scrubbing"),
        ("SAR", "Session Abandonment Rate", "% search sessions ending with exit without photo selection")
    ]
    for i, (code, title, desc) in enumerate(diag_metrics):
        lx = Inches(1.1) + i * (lm_w + lm_gap)
        tb_dm = s8.shapes.add_textbox(lx, Inches(5.75), lm_w, Inches(1.1))
        tf_dm = tb_dm.text_frame
        tf_dm.word_wrap = True
        tf_dm.margin_left = tf_dm.margin_top = tf_dm.margin_right = tf_dm.margin_bottom = 0
        
        p = tf_dm.paragraphs[0]
        p.text = code
        p.font.name = FONT_FAMILY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ORANGE_FRICTION
        
        p = tf_dm.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        
        p = tf_dm.add_paragraph()
        p.text = desc
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_MUTED


    # =========================================================================
    # SLIDE 9: RISKS & MITIGATION MATRIX
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(
        s9,
        "Part 8 · Product Risks, Mitigations & Boundaries",
        "The MVP Direction is Promising, But Scale, Trust, and Refinement Burden Remain Open Risks",
        "Proactive risk management matrix addressing cognitive load, privacy, and evaluation boundaries"
    )

    # 4 Structured Risk Cards
    risks = [
        {
            "priority": "P0 · USER EXPERIENCE",
            "title": "Refinement Cognitive Burden (R3)",
            "impact": "Users struggle to think of additional clues when candidates remain broad, causing session abandonment.",
            "mitigation": "Built additive query state and 1-click rejection (✕ Not this photo).",
            "future": "Introduce proactive AI suggestion chips based on candidate visual divergence."
        },
        {
            "priority": "P0 · TRUST & PRIVACY",
            "title": "Privacy and User Data Trust (R6)",
            "impact": "Users may be hesitant to share intimate personal memories and photos with cloud AI models.",
            "mitigation": "Controlled synthetic evaluation dataset; clear zero-retention privacy disclosures.",
            "future": "Implement on-device edge processing (e.g. Gemini Nano) and encrypted private embeddings."
        },
        {
            "priority": "P1 · SYSTEM GENERALIZATION",
            "title": "Prototype Scale & Evaluation Generalization (R5)",
            "impact": "40-photo dataset cannot prove scalability or collision resistance across a 50,000-photo personal library.",
            "mitigation": "Controlled representative benchmark with diverse categories and distractors.",
            "future": "Evaluate scalable semantic retrieval and multi-cue re-ranking against larger photo libraries."
        },
        {
            "priority": "P1 · AI INTERPRETATION",
            "title": "AI Memory Misinterpretation & False Positives (R1/R4)",
            "impact": "Overconfident false matches degrade user trust; AI misinterpreting relative time or companions.",
            "mitigation": "Strict 8-facet schema validation + transparent 'Why this result?' rationale bullets.",
            "future": "Interactive user confirmation chips to verify extracted cues before execution."
        }
    ]

    r_w = Inches(5.75)
    r_h = Inches(2.25)
    coords = [
        (Inches(0.8), Inches(1.85)),
        (Inches(6.8), Inches(1.85)),
        (Inches(0.8), Inches(4.25)),
        (Inches(6.8), Inches(4.25))
    ]

    for i, (rx, ry) in enumerate(coords):
        rk = risks[i]
        add_card(s9, rx, ry, r_w, r_h, bg_color=SURFACE_WHITE)
        tb_rk = s9.shapes.add_textbox(rx + Inches(0.2), ry + Inches(0.15), r_w - Inches(0.4), r_h - Inches(0.3))
        tf_rk = tb_rk.text_frame
        tf_rk.word_wrap = True
        tf_rk.margin_left = tf_rk.margin_top = tf_rk.margin_right = tf_rk.margin_bottom = 0
        
        p = tf_rk.paragraphs[0]
        p.text = rk["priority"]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ORANGE_FRICTION if "P0" in rk["priority"] else GOOGLE_BLUE
        p.space_after = Pt(2)

        p = tf_rk.add_paragraph()
        p.text = rk["title"]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(4)

        p = tf_rk.add_paragraph()
        p.text = f"• Potential Impact: {rk['impact']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(2)

        p = tf_rk.add_paragraph()
        p.text = f"• Current Mitigation: {rk['mitigation']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(2)

        p = tf_rk.add_paragraph()
        p.text = f"• Future Evolution: {rk['future']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEAL_ACCENT

    # Bottom Boundaries Disclaimer Banner
    add_card(s9, Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.55), bg_color=BLUE_TINT, border_color=BLUE_BORDER)
    tb_bnd = s9.shapes.add_textbox(Inches(1.0), Inches(6.65), Inches(11.333), Inches(0.45))
    tf_bnd = tb_bnd.text_frame
    tf_bnd.word_wrap = True
    tf_bnd.margin_left = tf_bnd.margin_top = tf_bnd.margin_right = tf_bnd.margin_bottom = 0
    p = tf_bnd.paragraphs[0]
    p.text = "PROTOTYPE SCOPE BOUNDARIES: 40-photo curated representative dataset · N=4 usability study · Desktop web prototype · No live Google account integration"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.alignment = PP_ALIGN.CENTER


    # =========================================================================
    # SLIDE 10: STRATEGIC EVOLUTION & CLOSING OPPORTUNITY
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(
        s10,
        "Part 9 · Strategic Evolution & The Next Product Opportunity",
        "The Next Evolution is Not Smarter Search — It is Guided Memory Retrieval",
        "Transitioning from passive keyword search to multi-cue AI interpretation, and ultimately to proactive guided retrieval"
    )

    # 3-Phase Evolution Horizon (Cards)
    phases = [
        {
            "badge": "YESTERDAY",
            "title": "Keyword Search",
            "subtitle": "Rigid Single-Turn Search",
            "steps": [
                "• User remembers an episodic moment",
                "• User is forced to guess search keywords",
                "• System returns rigid exact matches",
                "• Query modification clears context",
                "• Fallback to manual timeline scrolling"
            ],
            "outcome": "High cognitive load & session abandonment",
            "col": TEXT_MUTED,
            "bg": SURFACE_WHITE,
            "border": BORDER_LIGHT
        },
        {
            "badge": "TODAY (OUR MVP)",
            "title": "Memory Assistant",
            "subtitle": "Natural Language & Explainability",
            "steps": [
                "• User describes memory in natural language",
                "• AI extracts 8 structured episodic cues",
                "• Transparent 'Why this result?' rationale",
                "• Additive clue layering preserves context",
                "• 1-click candidate rejection"
            ],
            "outcome": "Strong usability; users need clue guidance",
            "col": GOOGLE_BLUE,
            "bg": BLUE_TINT,
            "border": BLUE_BORDER
        },
        {
            "badge": "TOMORROW (NEXT OPPORTUNITY)",
            "title": "Guided Retrieval",
            "subtitle": "Proactive Recognition Prompts",
            "steps": [
                "• AI detects remaining candidate ambiguity",
                "• Proactively asks targeted recognition questions:",
                "  – 'Was it indoors or outdoors?'",
                "  – 'Who was with you on that trip?'",
                "  – 'What were you wearing?'",
                "• Dynamic multi-cue candidate convergence"
            ],
            "outcome": "Effortless, conversational memory retrieval",
            "col": TEAL_ACCENT,
            "bg": TEAL_TINT,
            "border": TEAL_BORDER
        }
    ]

    ph_w = Inches(3.75)
    ph_gap = Inches(0.24)
    for i, ph in enumerate(phases):
        px = start_x + i * (ph_w + ph_gap)
        add_card(s10, px, Inches(1.85), ph_w, Inches(3.9), bg_color=ph["bg"], border_color=ph["border"])
        tb_ph = s10.shapes.add_textbox(px + Inches(0.2), Inches(2.0), ph_w - Inches(0.4), Inches(3.6))
        tf_ph = tb_ph.text_frame
        tf_ph.word_wrap = True
        tf_ph.margin_left = tf_ph.margin_top = tf_ph.margin_right = tf_ph.margin_bottom = 0
        
        p = tf_ph.paragraphs[0]
        p.text = ph["badge"]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ph["col"]
        p.space_after = Pt(2)

        p = tf_ph.add_paragraph()
        p.text = ph["title"]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        
        p = tf_ph.add_paragraph()
        p.text = ph["subtitle"]
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(8)

        for s in ph["steps"]:
            p = tf_ph.add_paragraph()
            p.text = s
            p.font.name = FONT_FAMILY
            p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MAIN
            p.space_after = Pt(2)

        p = tf_ph.add_paragraph()
        p.text = f"\nTakeaway: {ph['outcome']}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = ph["col"]

    # Bottom Closing Vision & Supporting Links Card
    add_card(s10, Inches(0.8), Inches(5.9), Inches(11.733), Inches(1.2), bg_color=SURFACE_WHITE)
    tb_vis = s10.shapes.add_textbox(Inches(1.1), Inches(6.0), Inches(11.133), Inches(1.0))
    tf_vis = tb_vis.text_frame
    tf_vis.word_wrap = True
    tf_vis.margin_left = tf_vis.margin_top = tf_vis.margin_right = tf_vis.margin_bottom = 0

    p = tf_vis.paragraphs[0]
    p.text = "“From search → to memory understanding → to guided personal retrieval.”"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = GOOGLE_BLUE
    p.space_after = Pt(4)

    p = tf_vis.add_paragraph()
    # Clickable Live Link
    run1 = p.add_run()
    run1.text = "Live Deployed Prototype: "
    run1.font.name = FONT_FAMILY
    run1.font.size = Pt(11.5)
    run1.font.color.rgb = TEXT_MUTED

    run2 = p.add_run()
    run2.text = "https://app-photos-discovery-engine-fa3ckmfdn4mudlheyg2yxs.streamlit.app/"
    run2.font.name = FONT_FAMILY
    run2.font.size = Pt(11.5)
    run2.font.bold = True
    run2.font.color.rgb = GOOGLE_BLUE
    run2.hyperlink.address = "https://app-photos-discovery-engine-fa3ckmfdn4mudlheyg2yxs.streamlit.app/"

    p2 = tf_vis.add_paragraph()
    p2.text = "Supporting Case Study Artifacts: Discovery Engine (Part 1) · Metric Decomposition (Part 2) · User Research (Part 3) · Usability Benchmark (Part 6) · Metric Hierarchy (Part 7)"
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(11)
    p2.font.color.rgb = TEXT_SUBTLE

    # Save Presentation
    output_pptx = "NL_GooglePhotos_Core_Experience.pptx"
    prs.save(output_pptx)
    print(f"Successfully generated presentation: {output_pptx} with {len(prs.slides)} slides.")

if __name__ == "__main__":
    build_deck()
