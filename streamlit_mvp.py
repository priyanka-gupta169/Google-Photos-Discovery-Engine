"""Dedicated Standalone Streamlit Entrypoint for Deployment B: AI Memory Retrieval Assistant (MVP).

Google Photos Core Experience — AI Memory Retrieval Assistant
Photo Retrieval Research Prototype.
"""

import sys
from pathlib import Path
import streamlit as st

# Configure Root Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import importlib
import src.data.representative_dataset
importlib.reload(src.data.representative_dataset)
import src.retrieval.scoring
importlib.reload(src.retrieval.scoring)

from src.ui.mvp_view import render_mvp_assistant
from src.ui.styles import GOOGLE_PHOTOS_ICON_SVG


def get_deployment_commit() -> str:
    """Returns the current git short commit hash."""
    try:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "0a2bed1"


# Dedicated Page Configuration
st.set_page_config(
    page_title="AI Memory Retrieval Assistant | Photo Retrieval Research Prototype",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sidebar: Prototype Scope & Interaction Model
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            {GOOGLE_PHOTOS_ICON_SVG}
            <div>
                <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; line-height: 1.2;">AI Memory Assistant</div>
                <div style="font-size: 0.76rem; color: #94a3b8; font-weight: 600;">Research Prototype</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Build: `{get_deployment_commit()}` • Photo Retrieval Research Prototype (not affiliated with Google LLC).")
    st.markdown("---")

    st.markdown("#### 🎯 Interaction Model")
    st.markdown("1. **Natural Memory Input**: Describe people, places, times, activities, or visual clues.")
    st.markdown("2. **AI Cue Understanding**: Extracts semantic anchors without needing exact keywords.")
    st.markdown("3. **Candidate Ranking**: Hybrid multi-cue retrieval with transparent rationales.")
    st.markdown("4. **Additive Refinement**: Add more clues without resetting previous context.")
    st.markdown("5. **Negative Feedback**: Rejection narrows candidate pool via negative scoring.")

    st.markdown("---")
    st.markdown("#### 📁 Evaluation Archive")
    st.markdown("- **Archive Size**: 40 representative photos")
    st.markdown("- **Scenarios Covered**: Travel, documents/receipts, ambiguous event attire")
    st.markdown("- **Privacy Boundary**: Operates in controlled prototype environment")


# Render Deployed MVP
render_mvp_assistant(show_navigation_link=False)
