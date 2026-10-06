"""Design systems and CSS themes for Discovery Engine and Memory Retrieval Assistant.

Maintains distinct visual identities:
- Discovery Engine: Research & Analytics PM Dashboard (Obsidian slate, data cards, KPI highlights)
- Memory Assistant: Google Photos-inspired consumer photo search interface (Clean, photo-centric, light-dark balance)
"""

DISCOVERY_ENGINE_CSS = """
<style>
    /* Discovery Engine Executive Analytics Styling */
    .discovery-header {
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    .discovery-subhead {
        color: #94a3b8;
        font-size: 1.05rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .discovery-desc {
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 1.5rem;
        max-width: 900px;
        padding: 10px 16px;
        background: rgba(30, 41, 59, 0.4);
        border-left: 3px solid #38bdf8;
        border-radius: 0 8px 8px 0;
    }
    .research-workflow-card {
        background: #0f172a;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 1.5rem;
    }
    .workflow-step {
        display: inline-block;
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #38bdf8;
        margin: 4px;
    }
    .workflow-arrow {
        color: #64748b;
        font-weight: bold;
        margin: 0 4px;
        font-size: 0.85rem;
    }
    .kpi-card {
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-top: 3px solid #38bdf8;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
    }
    .kpi-num {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .kpi-label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .app-switcher-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        color: #a5b4fc;
        margin-bottom: 12px;
    }
</style>
"""

MVP_ASSISTANT_CSS = """
<style>
    /* Google Photos-Inspired Consumer Product Styling */
    .mvp-main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.15rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .mvp-subtitle {
        color: #94a3b8;
        font-size: 0.92rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .mvp-prompt-hero {
        font-size: 1.22rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
    }
    .mvp-hero-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    .search-card-container {
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .photo-result-card {
        background: #1e293b;
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 14px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .photo-result-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
    }
    .cue-pill {
        display: inline-block;
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 4px 10px;
        font-size: 0.8rem;
        color: #e2e8f0;
        margin: 3px;
    }
    .rationale-bullet {
        font-size: 0.85rem;
        color: #cbd5e1;
        margin-bottom: 3px;
    }
    .rationale-bullet span {
        color: #34d399;
        font-weight: bold;
    }
    .app-switcher-banner {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 1rem;
        font-size: 0.82rem;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
"""

# Google Photos Multicolor Research Logo SVG
GOOGLE_PHOTOS_ICON_SVG = """<svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; flex-shrink: 0; display: inline-block;">
  <rect width="34" height="34" rx="8" fill="#1e293b"/>
  <path d="M11 11h12l1.8 2.5h3.2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-10a2 2 0 0 1 2-2h3.2L11 11z" stroke="#94a3b8" stroke-width="1.6" fill="none"/>
  <circle cx="17" cy="18" r="6" stroke="#475569" stroke-width="1"/>
  <path d="M17 18 L17 12.5 A5.5 5.5 0 0 1 22.5 18 Z" fill="#4285F4"/>
  <path d="M17 18 L22.5 18 A5.5 5.5 0 0 1 17 23.5 Z" fill="#EA4335"/>
  <path d="M17 18 L17 23.5 A5.5 5.5 0 0 1 11.5 18 Z" fill="#FBBC05"/>
  <path d="M17 18 L11.5 18 A5.5 5.5 0 0 1 17 12.5 Z" fill="#34A853"/>
  <circle cx="17" cy="18" r="1.8" fill="#0f172a"/>
</svg>"""

RESEARCH_DISCOVERY_ICON_SVG = """<svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; flex-shrink: 0; display: inline-block;">
  <rect width="34" height="34" rx="8" fill="#0f172a" stroke="rgba(56, 189, 248, 0.3)" stroke-width="1.5"/>
  <circle cx="15" cy="15" r="7" stroke="#38bdf8" stroke-width="2" fill="none"/>
  <line x1="20" y1="20" x2="27" y2="27" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round"/>
  <circle cx="15" cy="15" r="2.5" fill="#c084fc"/>
</svg>"""
