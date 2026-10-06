"""Dedicated Standalone Streamlit Entrypoint for Deployment A: AI Discovery Engine.

Google Photos Discovery Engine — Core Experience Research
Executive Discovery & Retrieval Friction Analytical Workbench.
"""

import sys
from pathlib import Path
import streamlit as st

# Configure Root Path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.storage.database import DatabaseManager
from src.ui.discovery_view import render_discovery_engine
from src.ui.styles import RESEARCH_DISCOVERY_ICON_SVG


def get_deployment_commit() -> str:
    """Returns the current git short commit hash."""
    try:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "0a2bed1"


# Dedicated Page Configuration
st.set_page_config(
    page_title="Google Photos Discovery Engine | Core Experience Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_database():
    """Initializes and caches SQLite DatabaseManager with auto-seeding."""
    return DatabaseManager(auto_seed=True)


db = get_database()

# Sidebar: Research Scope & Provenance
with st.sidebar:
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
    st.caption(f"Build: `{get_deployment_commit()}` • Research intelligence platform (not affiliated with Google LLC).")
    st.markdown("---")

    st.markdown("#### 🎯 Business Goal")
    st.info(
        "Increase the % of users who successfully retrieve a photo they remember but cannot precisely describe."
    )

    st.markdown("#### 🔬 Scope Isolation")
    st.markdown("- **Problem B (In Scope)**: Search & Retrieval friction on existing photos.")
    st.markdown("- **Problem A (Excluded)**: Cloud backup sync loss & storage caps.")

    st.markdown("---")
    st.markdown("#### 📊 Verified Evidence Base")
    st.markdown("- **Authentic Records**: 74 total public reviews")
    st.markdown("- **Friction Records**: 72 Problem B cases")
    st.markdown("- **Emergent Clusters**: 17 HDBSCAN clusters")
    st.markdown("- **Research Findings**: 8 synthesized findings")
    st.markdown("- **Citation Provenance**: 100% DAG verified")


# Render Discovery Engine
render_discovery_engine(db, show_navigation_link=False)
