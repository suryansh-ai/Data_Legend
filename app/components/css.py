"""
Data Legend — Design System v4
Minimalist premium: Cool gradient bg, Indigo accent, system fonts, generous spacing.
"""

DESIGN = """
<style>
/* ═══════════════════════════════════════════
   RESET & GLOBALS
   ═══════════════════════════════════════════ */
*,
*::before,
*::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(160deg, #F8FAFC 0%, #F1F5F0 45%, #EFF6FF 100%);
    color: #0F172A;
    min-height: 100vh;
}

#MainMenu, footer, header { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }

.main .block-container {
    padding: 0 !important;
    max-width: 1100px !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* ═══════════════════════════════════════════
   TOP NAV — White, clean, minimal
   ═══════════════════════════════════════════ */
.topnav {
    position: sticky;
    top: 0;
    z-index: 9999;
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid #E2E8F0;
    padding: 0 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 52px;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    text-decoration: none;
}

.nav-logo {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: #6366F1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

.nav-wordmark {
    font-weight: 700;
    font-size: 0.95rem;
    color: #0F172A;
    letter-spacing: -0.02em;
}

.nav-wordmark span {
    color: #6366F1;
}

.nav-links {
    display: flex;
    gap: 0.15rem;
}

.nav-link {
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-size: 0.825rem;
    font-weight: 500;
    color: #64748B;
    text-decoration: none;
    cursor: pointer;
    transition: color 0.15s ease, background 0.15s ease;
    border: none;
    background: transparent;
}

.nav-link:hover {
    color: #0F172A;
    background: #F1F5F9;
}

.nav-link.active {
    color: #6366F1;
    background: #EEF2FF;
    font-weight: 600;
}

.nav-status {
    display: none;
}

/* ═══════════════════════════════════════════
   PAGE WRAPPER
   ═══════════════════════════════════════════ */
.page {
    padding: 2.5rem;
}

/* ═══════════════════════════════════════════
   HERO — Light, clean
   ═══════════════════════════════════════════ */
.hero {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 2rem 2rem;
    margin-bottom: 1.5rem;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #EEF2FF;
    border-radius: 9999px;
    padding: 0.3rem 0.8rem;
    font-size: 0.7rem;
    font-weight: 600;
    color: #6366F1;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1rem;
}

.hero h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.15;
    letter-spacing: -0.025em;
    margin: 0 0 0.75rem;
}

.hero h1 .hl {
    color: #6366F1;
}

.hero-sub {
    font-size: 0.95rem;
    color: #64748B;
    line-height: 1.65;
    max-width: 540px;
    margin-bottom: 1.5rem;
}

.hero-metrics {
    display: flex;
    gap: 2.5rem;
}

.hero-metric-val {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0F172A;
}

.hero-metric-lbl {
    font-size: 0.7rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
    margin-top: 0.15rem;
}

/* ═══════════════════════════════════════════
   GRIDS
   ═══════════════════════════════════════════ */
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem; }

/* ═══════════════════════════════════════════
   METRIC TILES
   ═══════════════════════════════════════════ */
.tile {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem 1.25rem 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.15s ease;
}

.tile::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: #6366F1;
    border-radius: 10px 10px 0 0;
}

.tile:hover {
    border-color: #C7D2FE;
}

.tile-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.tile-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
}

.tile-icon.teal { background: #ECFDF5; }
.tile-icon.amber { background: #FFFBEB; }
.tile-icon.rose { background: #FEF2F2; }
.tile-icon.green { background: #ECFDF5; }
.tile-icon.navy { background: #EEF2FF; }
.tile-icon.purple { background: #F5F3FF; }

.tile-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1;
}

.tile-label {
    font-size: 0.7rem;
    font-weight: 500;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.2rem;
}

/* ═══════════════════════════════════════════
   CARDS
   ═══════════════════════════════════════════ */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.5rem;
    transition: border-color 0.15s ease;
}

.card:hover {
    border-color: #C7D2FE;
}

.card-stripe {
    display: none;
}

.card-emoji {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    margin-bottom: 0.75rem;
}

.card-emoji.teal { background: #ECFDF5; }
.card-emoji.amber { background: #FFFBEB; }
.card-emoji.rose { background: #FEF2F2; }
.card-emoji.purple { background: #F5F3FF; }
.card-emoji.navy { background: #EEF2FF; }
.card-emoji.green { background: #ECFDF5; }

.card-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 0.3rem;
    line-height: 1.3;
}

.card-body {
    font-size: 0.825rem;
    color: #64748B;
    line-height: 1.6;
}

/* ═══════════════════════════════════════════
   SECTION TITLES
   ═══════════════════════════════════════════ */
.sec-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.sec-line {
    height: 1px;
    background: #E2E8F0;
    margin: 1.5rem 0;
}

/* ═══════════════════════════════════════════
   BADGES
   ═══════════════════════════════════════════ */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.2rem;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.badge-green { background: #ECFDF5; color: #047857; }
.badge-yellow { background: #FFFBEB; color: #B45309; }
.badge-red { background: #FEF2F2; color: #B91C1C; }
.badge-gray { background: #F1F5F9; color: #64748B; }

/* ═══════════════════════════════════════════
   PROGRESS BARS
   ═══════════════════════════════════════════ */
.bar-track {
    height: 4px;
    background: #F1F5F9;
    border-radius: 2px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.5s ease;
}

.bar-fill.teal { background: #059669; }
.bar-fill.amber { background: #D97706; }
.bar-fill.rose { background: #DC2626; }
.bar-fill.gray { background: #94A3B8; }

/* ═══════════════════════════════════════════
   FACILITY LIST ITEMS
   ═══════════════════════════════════════════ */
.fac-item {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #6366F1;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.15s ease;
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.fac-item:hover {
    border-color: #C7D2FE;
    border-left-color: #4F46E5;
}

.fac-rank {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94A3B8;
    min-width: 28px;
    text-align: center;
}

.fac-info {
    flex: 1;
    min-width: 0;
}

.fac-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #0F172A;
    margin-bottom: 0.15rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.fac-loc {
    font-size: 0.75rem;
    color: #94A3B8;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.fac-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.35rem;
    flex-shrink: 0;
}

.fac-score {
    font-size: 0.95rem;
    font-weight: 700;
}

.fac-meta {
    font-size: 0.68rem;
    color: #94A3B8;
    font-weight: 500;
}

/* ═══════════════════════════════════════════
   FILTERS BAR
   ═══════════════════════════════════════════ */
.filter-bar {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    gap: 1rem;
    align-items: flex-end;
}

.filter-item {
    flex: 1;
    min-width: 120px;
}

.filter-lbl {
    font-size: 0.65rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
}

/* ═══════════════════════════════════════════
   EVIDENCE BLOCKS
   ═══════════════════════════════════════════ */
.ev-block {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}

.ev-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.ev-row {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.4rem 0;
    font-size: 0.825rem;
    color: #64748B;
    line-height: 1.5;
    border-bottom: 1px solid #F1F5F9;
}

.ev-row:last-child {
    border-bottom: none;
}

.ev-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-top: 0.45rem;
    flex-shrink: 0;
}

.ev-dot.on { background: #059669; }
.ev-dot.off { background: #CBD5E1; }

/* ═══════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════ */
.empty {
    text-align: center;
    padding: 4rem 2rem;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
}

.empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.3; }
.empty-title { font-size: 1rem; font-weight: 600; color: #0F172A; margin-bottom: 0.4rem; }
.empty-desc { font-size: 0.85rem; color: #64748B; max-width: 360px; margin: 0 auto; }

/* ═══════════════════════════════════════════
   MAP WRAPPER
   ═══════════════════════════════════════════ */
.map-wrap {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}

/* ═══════════════════════════════════════════
   LEGEND
   ═══════════════════════════════════════════ */
.legend {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    justify-content: center;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.85rem 1.5rem;
}

.legend-item { display: flex; align-items: center; gap: 0.35rem; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-text { font-size: 0.75rem; color: #64748B; font-weight: 500; }

/* ═══════════════════════════════════════════
   ANIMATION — minimal
   ═══════════════════════════════════════════ */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.anim-1, .anim-2, .anim-3, .anim-4 {
    animation: fadeIn 0.3s ease both;
}

/* ═══════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

/* ═══════════════════════════════════════════
   STREAMLIT OVERRIDES
   ═══════════════════════════════════════════ */
.stSelectbox [data-baseweb="select"] {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    font-size: 0.85rem !important;
}

.stMultiSelect [data-baseweb="select"] {
    border-radius: 8px !important;
}

.stDataFrame {
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
}

.stButton button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
}

.stToast {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

.stExpander {
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    background: #FFFFFF !important;
}

/* Page link nav styling */
.stPageLink {
    margin-bottom: 0 !important;
}

.stPageLink section {
    padding: 0.3rem 0 !important;
}

.stPageLink a {
    font-size: 0.825rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 0.35rem 0.75rem !important;
    background: transparent !important;
    color: #64748B !important;
    border: none !important;
    text-decoration: none !important;
    white-space: nowrap !important;
}

.stPageLink a:hover {
    color: #0F172A !important;
    background: #F1F5F9 !important;
}

.stPageLink button[disabled] {
    color: #6366F1 !important;
    background: #EEF2FF !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

/* ═══════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════ */
@media (max-width: 900px) {
    .grid-4 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: 1fr; }
    .hero { padding: 1.5rem; }
    .hero h1 { font-size: 1.5rem; }
    .hero-metrics { gap: 1.5rem; flex-wrap: wrap; }
    .filter-bar { flex-direction: column; }
    .topnav { padding: 0 1rem; }
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(DESIGN, unsafe_allow_html=True)


def nav(active="home"):
    import streamlit as st

    brand_html = """
    <div class="topnav">
        <div class="nav-brand">
            <div class="nav-logo">DL</div>
            <div class="nav-wordmark">Data <span>Legend</span></div>
        </div>
    </div>
    """
    st.markdown(brand_html, unsafe_allow_html=True)

    pages = [
        ("main.py", "Home"),
        ("pages/1_trust_desk.py", "Trust Desk"),
        ("pages/3_medical_desert.py", "Medical Desert"),
        ("pages/4_data_readiness.py", "Data Readiness"),
    ]

    nav_icons = {"main.py": "🏠", "pages/1_trust_desk.py": "🔍", "pages/3_medical_desert.py": "🗺", "pages/4_data_readiness.py": "📊"}

    cols = st.columns(4)
    for i, (page, label) in enumerate(pages):
        with cols[i]:
            is_active = (
                (active == "home" and page == "main.py") or
                (active == "trust" and "1_trust" in page) or
                (active == "desert" and "3_medical" in page) or
                (active == "readiness" and "4_data" in page)
            )
            try:
                st.page_link(
                    page,
                    label=label,
                    icon=nav_icons.get(page, "📌"),
                    disabled=is_active,
                )
            except Exception:
                pass
