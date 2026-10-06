"""AI Memory Retrieval Assistant MVP View Module.

Deployment B: Consumer-Facing AI-Native Photo Retrieval Assistant
Validated research prototype built from qualitative discovery findings.
"""

import re
import streamlit as st
import pandas as pd
from typing import Optional
from src.ai.cue_extractor import extract_memory_cues
from src.retrieval.scoring import MemoryRetrievalEngine
from src.data.representative_dataset import get_representative_dataset
from src.models.mvp import MemoryCues
from src.ui.styles import MVP_ASSISTANT_CSS, GOOGLE_PHOTOS_ICON_SVG


def clean_display_title(title: str) -> str:
    """Removes internal evaluation/benchmark labels such as '(Target Task 1)' or '(Distractor Task 3)'."""
    return re.sub(r"\s*\((?:Target|Distractor)\s+Task\s+\d+\)", "", title).strip()


def render_mvp_assistant(show_navigation_link: bool = True):
    """Renders the complete AI Memory Retrieval Assistant consumer MVP view."""
    # Apply dedicated consumer photo product styling
    st.markdown(MVP_ASSISTANT_CSS, unsafe_allow_html=True)

    # Optional cross-deployment switcher banner
    if show_navigation_link:
        col_nav1, col_nav2 = st.columns([3, 1])
        with col_nav1:
            st.markdown(
                """
                <div class="app-switcher-banner">
                    <span>📸 DELIVERABLE 3 OF 3: DEPLOYED AI-NATIVE MVP</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_nav2:
            st.markdown(
                """
                <div style="text-align: right; padding-top: 2px;">
                    <a href="?app=discovery" target="_self" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; text-decoration: none;">
                        👉 Switch to Discovery Engine
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Header & Product Identity
    st.markdown(
        f"""
        <div class="mvp-main-header">
            {GOOGLE_PHOTOS_ICON_SVG}
            <span>AI Memory Retrieval Assistant</span>
        </div>
        <div class="mvp-subtitle">Photo Retrieval Research Prototype</div>
        <div class="mvp-prompt-hero">Can't remember the exact date or filename? Tell me what you remember about the photo.</div>
        <div class="mvp-hero-desc">Describe anything you remember — a person, place, event, object, activity, appearance, or approximate time.</div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "⚠️ **Prototype Notice**: This is an experimental prototype using a controlled representative photo archive (40 photos). "
        "It does **not** access your personal Google Photos."
    )

    with st.expander("ℹ️ How it works (5-Step Interaction Model)"):
        st.markdown(
            """
            1. **Tell me what you remember**: Speak or type what you remember in natural words.
            2. **AI turns your memory into multiple clues**: Translates your memory into people, places, times, activities, and visual cues.
            3. **See possible matches**: Review ranked candidates with transparent "Why this result?" rationales.
            4. **Add another clue if needed**: Iteratively refine without starting over.
            5. **Retrieve the intended photo**: The candidate set narrows until you find your photo.
            """
        )

    # Callbacks for state management
    def cb_apply_chip(keyword: str):
        st.session_state.mvp_main_search_textarea = keyword
        st.session_state.mvp_query_input = keyword
        st.session_state.mvp_scroll_to_search = True

    def cb_load_benchmark_task(task_id: str, prompt: str):
        st.session_state.mvp_main_search_textarea = prompt
        st.session_state.mvp_query_input = prompt
        st.session_state.mvp_active_task_id = task_id
        st.session_state.mvp_cues = None
        st.session_state.mvp_candidates = []
        st.session_state.mvp_rejected_ids = []
        st.session_state.mvp_has_searched = False
        st.session_state.mvp_prev_count = None
        st.session_state.mvp_scroll_to_search = True

    def cb_reset_search():
        st.session_state.mvp_main_search_textarea = ""
        st.session_state.mvp_query_input = ""
        st.session_state.mvp_cues = None
        st.session_state.mvp_candidates = []
        st.session_state.mvp_rejected_ids = []
        st.session_state.mvp_attempts = 0
        st.session_state.mvp_refinements = 0
        st.session_state.mvp_session_outcome = None
        st.session_state.mvp_has_searched = False
        st.session_state.mvp_prev_count = None
        st.session_state.mvp_active_task_id = "OPEN_ENDED"
        st.session_state.mvp_reject_notice = False
        st.session_state.mvp_engine = MemoryRetrievalEngine()

    # Session State Initialization
    st.session_state.mvp_engine = MemoryRetrievalEngine()
    if "mvp_cues" not in st.session_state:
        st.session_state.mvp_cues = None
    if "mvp_candidates" not in st.session_state:
        st.session_state.mvp_candidates = []
    if "mvp_rejected_ids" not in st.session_state:
        st.session_state.mvp_rejected_ids = []
    if "mvp_attempts" not in st.session_state:
        st.session_state.mvp_attempts = 0
    if "mvp_refinements" not in st.session_state:
        st.session_state.mvp_refinements = 0
    if "mvp_session_outcome" not in st.session_state:
        st.session_state.mvp_session_outcome = None
    if "mvp_has_searched" not in st.session_state:
        st.session_state.mvp_has_searched = False
    if "mvp_prev_count" not in st.session_state:
        st.session_state.mvp_prev_count = None
    if "mvp_active_task_id" not in st.session_state:
        st.session_state.mvp_active_task_id = "OPEN_ENDED"
    if "mvp_query_input" not in st.session_state:
        st.session_state.mvp_query_input = ""
    if "mvp_main_search_textarea" not in st.session_state:
        st.session_state.mvp_main_search_textarea = st.session_state.mvp_query_input
    if "mvp_reject_notice" not in st.session_state:
        st.session_state.mvp_reject_notice = False

    # Smooth scroll to search box if triggered
    if st.session_state.get("mvp_scroll_to_search", False):
        st.session_state.mvp_scroll_to_search = False
        st.components.v1.html(
            """
            <script>
            setTimeout(function() {
                var el = window.parent.document.querySelector('textarea[aria-label="What photo are you trying to find?"]');
                if (el) {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    el.focus();
                }
            }, 100);
            </script>
            """,
            height=0,
        )

    # ----------------- HERO OPEN-ENDED SEARCH BAR -----------------
    st.markdown("### What photo are you trying to find?")
    if st.session_state.mvp_active_task_id != "OPEN_ENDED":
        scenario_labels = {
            "TASK-1": "Scenario 1 — Fuzzy Travel Memory",
            "TASK-2": "Scenario 2 — Old Document",
            "TASK-3": "Scenario 3 — Specific Event Photo",
        }
        scen_name = scenario_labels.get(st.session_state.mvp_active_task_id, st.session_state.mvp_active_task_id)
        st.info(
            f"🎯 **{scen_name} Loaded**: "
            "You can freely edit this memory in the box below before clicking **Search Memories**."
        )

    user_query = st.text_area(
        "What photo are you trying to find?",
        key="mvp_main_search_textarea",
        placeholder="I remember a photo of a mountain from a trip...",
        height=85,
        label_visibility="collapsed",
        help="Use natural language: describe anything you remember.",
    )

    # 8 Interactive Example Chips
    st.caption("Not sure what to type? Try something like:")
    chip_cols = st.columns(8)
    chips_data = [
        ("🏔️ Mountain", "Mountain"),
        ("🪔 Navratri", "Navratri"),
        ("🏖️ Beach", "Beach"),
        ("🐶 Dog", "Dog"),
        ("🎂 Birthday", "Birthday"),
        ("🌅 Sunset", "Sunset"),
        ("👨‍👩‍👧 Family", "Family"),
        ("🎓 College", "College"),
    ]
    for i, (label, kw) in enumerate(chips_data):
        with chip_cols[i]:
            st.button(
                label,
                key=f"chip_btn_{i}",
                on_click=cb_apply_chip,
                args=(kw,),
                use_container_width=True,
            )

    st.markdown(
        "<small style='color: #94a3b8;'>You don't need the exact date, filename, or exact words.</small>",
        unsafe_allow_html=True,
    )

    # Action Buttons
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        search_clicked = st.button("🔍 Search Memories", type="primary", use_container_width=True)
    with col_btn2:
        st.button(
            "🔄 Reset Search",
            key="btn_reset_search",
            on_click=cb_reset_search,
            use_container_width=False,
            help="Start a new photo search and clear the current memory and results.",
        )

    # Execute Search
    query_to_search = user_query.strip() if user_query else ""
    if search_clicked and query_to_search:
        st.session_state.mvp_attempts += 1
        st.session_state.mvp_prev_count = None
        st.session_state.mvp_query_input = query_to_search
        st.session_state.mvp_reject_notice = False
        with st.spinner("Translating your memory into structured cues..."):
            extracted = extract_memory_cues(query_to_search)
            st.session_state.mvp_cues = extracted.cues
            res = st.session_state.mvp_engine.search(extracted.cues, rejected_ids=st.session_state.mvp_rejected_ids)
            st.session_state.mvp_candidates = res.results
            st.session_state.mvp_has_searched = True

    # ----------------- WHAT I UNDERSTOOD -----------------
    if st.session_state.mvp_cues:
        cues = st.session_state.mvp_cues
        st.markdown("### 🧠 What I understood")
        st.caption("I'll use these clues together to find possible matches:")

        cue_lines = []
        if cues.companions:
            cue_lines.append(f"**👤 Person**: {', '.join(cues.companions)}")
        if cues.approximate_time:
            cue_lines.append(f"**🕒 Approximate time**: {cues.approximate_time}")
        if cues.location:
            cue_lines.append(f"**📍 Location**: {cues.location}")
        if cues.activity:
            cue_lines.append(f"**🎯 Activity / Event**: {cues.activity}")
        if cues.visual_attributes:
            cue_lines.append(f"**🎨 Visual clue**: {', '.join(cues.visual_attributes)}")
        if cues.objects:
            cue_lines.append(f"**📦 Object**: {', '.join(cues.objects)}")
        if cues.text_ocr:
            cue_lines.append(f"**📄 Document / OCR text**: {cues.text_ocr}")
        if cues.uncertainty:
            cue_lines.append(f"**❓ Uncertainty**: {cues.uncertainty}")

        st.info("  \n".join(cue_lines) if cue_lines else "Interpreting general scene context...")

    # ----------------- ITERATIVE REFINEMENT -----------------
    if st.session_state.mvp_candidates or st.session_state.mvp_has_searched:
        st.markdown("---")
        st.markdown("#### 🔍 Didn't find the exact photo?")
        st.markdown(
            "Add another clue from what you remember — without starting over. "
            "*New clues are merged with your existing memory to narrow down the results.*"
        )

        if st.session_state.mvp_reject_notice:
            st.warning("Not the right photo? Add another clue to narrow the search.")

        refine_col1, refine_col2 = st.columns([3, 1])
        with refine_col1:
            refine_input = st.text_input(
                "What else do you remember?",
                placeholder="Maybe we were laughing...",
                key="mvp_refine_input",
                label_visibility="collapsed",
            )
        with refine_col2:
            if st.button("Apply New Clue", type="secondary", use_container_width=True) and refine_input.strip():
                st.session_state.mvp_refinements += 1
                st.session_state.mvp_attempts += 1
                st.session_state.mvp_prev_count = len(st.session_state.mvp_candidates)
                st.session_state.mvp_reject_notice = False
                refine_res = st.session_state.mvp_engine.refine(
                    previous_cues=st.session_state.mvp_cues or MemoryCues(),
                    new_clue_text=refine_input,
                    rejected_photo_ids=st.session_state.mvp_rejected_ids,
                    active_task_id=st.session_state.get("mvp_active_task_id"),
                )
                st.session_state.mvp_cues = refine_res.updated_cues
                st.session_state.mvp_candidates = refine_res.results
                st.success("Refined search with your additional clue!")
                st.rerun()

    # ----------------- SEARCH RESULTS SECTION -----------------
    if st.session_state.mvp_has_searched:
        if st.session_state.mvp_candidates:
            st.markdown("---")
            st.markdown("### 🔎 Possible matches")

            progression_text = ""
            if st.session_state.mvp_prev_count is not None:
                progression_text = f" *(Progression: {st.session_state.mvp_prev_count} → {len(st.session_state.mvp_candidates)} possible matches)*"

            st.markdown(f"**{len(st.session_state.mvp_candidates)} possible matches**{progression_text}")
            st.caption("I've ranked these based on the clues you provided.")

            # Display candidate cards (Cleaned of internal benchmark labels)
            for idx, cand in enumerate(st.session_state.mvp_candidates[:8]):
                p = cand.photo
                clean_title = clean_display_title(p.title)

                with st.container():
                    st.markdown("---")
                    c_img, c_info = st.columns([1, 2])
                    with c_img:
                        st.image(p.thumbnail_url, use_container_width=True)
                    with c_info:
                        st.markdown(f"##### {clean_title} ({p.approx_year})")
                        st.caption(f"Category: {p.category} | Location: {p.location}")
                        st.markdown(f"*{p.description}*")

                        st.markdown("**Why this result?**")
                        for r in cand.match_reasons[:4]:
                            clean_r = r.replace("✓", "").strip()
                            st.markdown(f"- ✓ {clean_r}")

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("✓ This is the photo", key=f"confirm_{p.id}"):
                                st.session_state.mvp_session_outcome = ("SUCCESS", p.id)
                                st.success(f"🎉 Selected: **{clean_title}**!")
                        with btn_col2:
                            if st.button("✕ Not this photo", key=f"reject_{p.id}"):
                                st.session_state.mvp_rejected_ids.append(p.id)
                                st.session_state.mvp_refinements += 1
                                st.session_state.mvp_prev_count = len(st.session_state.mvp_candidates)
                                st.session_state.mvp_reject_notice = True
                                refine_res = st.session_state.mvp_engine.refine(
                                    previous_cues=st.session_state.mvp_cues or MemoryCues(),
                                    new_clue_text="Rejected photo",
                                    rejected_photo_ids=st.session_state.mvp_rejected_ids,
                                    active_task_id=st.session_state.get("mvp_active_task_id"),
                                )
                                st.session_state.mvp_candidates = refine_res.results
                                st.rerun()

            # Abandonment option
            st.markdown("---")
            with st.expander("Cannot find the photo? End search & record telemetry"):
                abandon_reason = st.selectbox(
                    "Select abandonment reason:",
                    [
                        "Results were too irrelevant / false positives",
                        "Cannot remember more details to narrow it down",
                        "Too many similar-looking photos",
                        "Wanted to search external app instead",
                    ],
                )
                if st.button("Record Abandonment Telemetry"):
                    st.session_state.mvp_session_outcome = ("ABANDONED", abandon_reason)
                    st.error("Search ended. Session logged as Abandoned.")

        else:
            # ZERO MATCH STATE (DO NOT FABRICATE RESULTS)
            st.markdown("---")
            st.warning("### 🔍 No strong matches found for this memory.")
            st.markdown(
                "Our 40-photo representative archive couldn't find a confident match with the current clues.\n\n"
                "**Try adding another clue such as:**\n"
                "- • who was there\n"
                "- • where you were\n"
                "- • what was happening\n"
                "- • what someone was wearing\n"
                "- • what the photo looked like\n"
                "- • an approximate time"
            )

    # ----------------- SECONDARY SECTION: REALISTIC MEMORY SCENARIOS -----------------
    st.markdown("---")
    st.markdown("### 🧪 Try Realistic Memory Scenarios")
    st.markdown(
        "These are research scenarios, not separate features. They simulate situations where you "
        "remember a photo but don't remember the exact date or filename. Use them to test how well "
        "the AI understands your memory and helps you retrieve the right photo."
    )
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.88rem; margin-bottom: 6px;'>"
        "<strong>How to test:</strong> 1. Choose a scenario &nbsp;&nbsp;2. Load it &nbsp;&nbsp;"
        "3. Edit the memory if you want &nbsp;&nbsp;4. Search Memories &nbsp;&nbsp;5. Review and refine the results"
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color: #94a3b8; font-size: 0.82rem; font-style: italic; margin-bottom: 16px; opacity: 0.85;'>"
        "While testing, notice: Did the AI understand what you remembered? Were the results relevant? Did refinement help you get closer to the photo?"
        "</p>",
        unsafe_allow_html=True,
    )

    prompt_t1 = "I remember a photo from a Goa trip with my friend Rohan around 3 years ago. I don't remember the exact date."
    prompt_t2 = "I remember a university marksheet or grade-sheet scan from around 2022. I don't remember the exact date or filename."
    prompt_t3 = "I remember a college ramp walk photo where I was wearing a black and gold dress."

    bench_col1, bench_col2, bench_col3 = st.columns(3)
    with bench_col1:
        st.markdown("**📍 Scenario 1 — Fuzzy Travel Memory**")
        st.caption("You remember a Goa trip with a friend, but not the exact date.")
        st.button(
            "Load Scenario",
            key="btn_load_scenario_1",
            on_click=cb_load_benchmark_task,
            args=("TASK-1", prompt_t1),
            use_container_width=True,
        )

    with bench_col2:
        st.markdown("**📄 Scenario 2 — Old Document**")
        st.caption("You remember a university marksheet from around 2022, but not the exact filename or date.")
        st.button(
            "Load Scenario",
            key="btn_load_scenario_2",
            on_click=cb_load_benchmark_task,
            args=("TASK-2", prompt_t2),
            use_container_width=True,
        )

    with bench_col3:
        st.markdown("**🎭 Scenario 3 — Specific Event Photo**")
        st.caption("You remember a college ramp-walk photo with a black & gold dress, but there are similar photos.")
        st.button(
            "Load Scenario",
            key="btn_load_scenario_3",
            on_click=cb_load_benchmark_task,
            args=("TASK-3", prompt_t3),
            use_container_width=True,
        )

    # Dataset inspection expander
    with st.expander("🔍 Audit Controlled Representative Dataset (40 Photos)"):
        df_dataset = pd.DataFrame([p.model_dump() for p in get_representative_dataset()])
        df_dataset["clean_title"] = df_dataset["title"].apply(clean_display_title)
        st.dataframe(
            df_dataset[["id", "clean_title", "category", "approx_year", "location"]],
            use_container_width=True,
        )
