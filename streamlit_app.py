"""Unified Streamlit Cloud Deployment Router for Google Photos Project.

Provides two dedicated product experiences via direct URLs and query parameters:
- Deployment A (Default / ?app=discovery): Google Photos Discovery Engine (Core Experience Research)
- Deployment B (?app=mvp): AI Memory Retrieval Assistant (Deployed MVP)

Live Deployment URL:
https://app-photos-discovery-engine-fa3ckmfdn4mudlheyg2yxs.streamlit.app/
"""

import sys
from pathlib import Path
import streamlit as st

# Configure Root Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import importlib
from src.storage.database import DatabaseManager
import src.data.representative_dataset
importlib.reload(src.data.representative_dataset)
import src.retrieval.scoring
importlib.reload(src.retrieval.scoring)

from src.ui.discovery_view import render_discovery_engine
from src.ui.mvp_view import render_mvp_assistant
from src.ui.styles import GOOGLE_PHOTOS_ICON_SVG, RESEARCH_DISCOVERY_ICON_SVG


def get_deployment_commit() -> str:
    """Returns the current git short commit hash."""
    try:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "0a2bed1"


# Check query parameter for active application
current_param = st.query_params.get("app", "discovery").lower()
if current_param not in ["mvp", "discovery"]:
    current_param = "discovery"

# Page configuration based on active experience
if current_param == "mvp":
    st.set_page_config(
        page_title="AI Memory Retrieval Assistant | Photo Retrieval Research Prototype",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
else:
    st.set_page_config(
        page_title="Google Photos Discovery Engine",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )


@st.cache_resource
def get_database():
    """Initializes and caches SQLite DatabaseManager with auto-seeding."""
    return DatabaseManager(auto_seed=True)


db = get_database()

# Sidebar: Contextual identity and seamless switcher
with st.sidebar:
    if current_param == "mvp":
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
    else:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                {RESEARCH_DISCOVERY_ICON_SVG}
                <div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; line-height: 1.2;">Google Photos Discovery Engine</div>
                    <div style="font-size: 0.76rem; color: #38bdf8; font-weight: 600;">Core Experience Research</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"Build: `{get_deployment_commit()}` • Core Experience Research (not affiliated with Google LLC).")
    st.markdown("---")

    # Seamless View Switcher
    st.markdown("#### 🔀 Switch Application")
    selected_view = st.radio(
        "Active Application:",
        options=["🔬 AI Discovery Engine", "📸 AI Memory Assistant (MVP)"],
        index=1 if current_param == "mvp" else 0,
        label_visibility="collapsed",
    )

    # Synchronize query parameter with selection
    target_param = "mvp" if "MVP" in selected_view else "discovery"
    if target_param != current_param:
        st.query_params["app"] = target_param
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔗 Direct Public URLs")
    st.markdown("- **Deployment A (Discovery Engine)**:  \n  `?app=discovery` *(or root URL)*")
    st.markdown("- **Deployment B (Deployed MVP)**:  \n  `?app=mvp`")

    st.markdown("---")
    if current_param == "mvp":
        st.markdown("#### 🎯 Interaction Model")
        st.markdown("1. Natural Memory Input")
        st.markdown("2. AI Cue Understanding")
        st.markdown("3. Candidate Ranking")
        st.markdown("4. Additive Refinement")
        st.markdown("5. Negative Feedback")
        st.markdown("- **Dataset**: 40 representative photos")
    else:
        st.markdown("#### 🎯 Research Scope")
        st.markdown("- **Problem B (In Scope)**: Retrieval friction on existing photos")
        st.markdown("- **Problem A (Excluded)**: Cloud sync & backup loss")
        st.markdown("- **Evidence Base**: 74 reviews, 72 Problem B cases, 17 clusters, 8 findings")


# Render the selected application
if current_param == "mvp":
    render_mvp_assistant(show_navigation_link=True)
else:
    render_discovery_engine(db, show_navigation_link=True)
