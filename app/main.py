"""
Data Legend — Home
"""
import streamlit as st
from components.css import inject_css, nav
from utils.data_loader import load_facilities, get_dataset_stats

st.set_page_config(page_title="Data Legend", page_icon="🏥", layout="wide")
inject_css()
nav("home")


def main():
    facilities = load_facilities()
    stats = get_dataset_stats(facilities)

    total = stats["total"]
    states = stats["states"]
    cities = stats["cities"]

    # ── HERO ──
    st.markdown(f"""
    <div class="hero">
        <div class="hero-pill">Databricks × Hack-Nation</div>
        <h1>Healthcare data<br>you can <span class="hl">actually trust.</span></h1>
        <p class="hero-sub">India has thousands of hospitals. But how do you know which ones truly have the ICU, maternity ward, or emergency department they claim? Data Legend reads the records, checks the evidence, and tells you what's real.</p>
        <div class="hero-metrics">
            <div><div class="hero-metric-val">{total:,}</div><div class="hero-metric-lbl">Facilities</div></div>
            <div><div class="hero-metric-val">{states}</div><div class="hero-metric-lbl">States</div></div>
            <div><div class="hero-metric-val">{cities}</div><div class="hero-metric-lbl">Cities</div></div>
            <div><div class="hero-metric-val">5</div><div class="hero-metric-lbl">Evidence Fields</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── WHY IT MATTERS ──
    st.markdown('<div class="sec-title">Why does this matter?</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card">
            <div class="card-emoji rose">⚠</div>
            <div class="card-title">Families travel hours to hospitals without what they need</div>
            <div class="card-body">A clinic lists "ICU" and "24/7 emergency" — but when a family arrives at 2 AM, they're turned away. The ICU was planned, not built.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
            <div class="card-emoji amber">⚡</div>
            <div class="card-title">NGOs waste resources on bad data</div>
            <div class="card-body">Health organizations need to know where to build new facilities. But existing data is messy, contradictory, and hard to act on with confidence.</div>
        </div>""", unsafe_allow_html=True)

    # ── HOW IT HELPS ──
    st.markdown('<div class="sec-title" style="margin-top:2rem;">How Data Legend helps</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card">
            <div class="card-emoji teal">◎</div>
            <div class="card-title">Cross-checks every claim</div>
            <div class="card-body">Compares 5 data fields for each facility. If a hospital says "ICU" in one place but doesn't mention it elsewhere, we flag that.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card">
            <div class="card-emoji green">✓</div>
            <div class="card-title">Scores trust honestly</div>
            <div class="card-body">Every facility gets a score. Green means corroborated. Yellow means uncertain. We never pretend to know what we don't.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card">
            <div class="card-emoji purple">◈</div>
            <div class="card-title">Finds healthcare gaps</div>
            <div class="card-body">Shows which regions have real healthcare deserts — not just missing data, but genuinely underserved communities.</div>
        </div>""", unsafe_allow_html=True)

    # ── 3 STEPS ──
    st.markdown('<div class="sec-title" style="margin-top:2rem;">How it works</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="width:36px;height:36px;border-radius:50%;background:#EEF2FF;color:#6366F1;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;margin-bottom:0.75rem;">1</div>
            <div class="card-title">Reads facility records</div>
            <div class="card-body">Takes raw data — descriptions, equipment lists, specialties, and more — from thousands of Indian healthcare facilities.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="width:36px;height:36px;border-radius:50%;background:#EEF2FF;color:#6366F1;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;margin-bottom:0.75rem;">2</div>
            <div class="card-title">Cross-checks everything</div>
            <div class="card-body">Two sources agreeing = trustworthy. One source alone = uncertain. Contradictions = flagged for review.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="width:36px;height:36px;border-radius:50%;background:#EEF2FF;color:#6366F1;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;margin-bottom:0.75rem;">3</div>
            <div class="card-title">Gives you answers</div>
            <div class="card-body">Pick a capability (like ICU or maternity) and a region. See facilities ranked by how much evidence backs each claim.</div>
        </div>""", unsafe_allow_html=True)

    # ── TRUST BADGES ──
    st.markdown('<div class="sec-title" style="margin-top:2rem;">Trust levels explained</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    badges = [
        ("✓", "Corroborated", "Multiple sources confirm this. You can trust it.", "badge-green"),
        ("!", "Claimed Only", "One source says so. Verify before acting on it.", "badge-yellow"),
        ("✗", "Weak", "Contradicted or aspirational language. Treat with caution.", "badge-red"),
        ("—", "Unknown", "Not enough data. Could be real — we just can't confirm.", "badge-gray"),
    ]
    for i, (icon, title, desc, cls) in enumerate(badges):
        with [c1, c2, c3, c4][i]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:1.4rem;margin-bottom:0.5rem;opacity:0.6;">{icon}</div>
                <span class="badge {cls}" style="margin-bottom:0.5rem;">{title}</span>
                <div class="card-body" style="margin-top:0.4rem;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # ── EXPLORE ──
    st.markdown('<div class="sec-title" style="margin-top:2rem;">Explore the data</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="card" style="border-left:3px solid #6366F1;">
            <div style="font-size:1.2rem;margin-bottom:0.5rem;opacity:0.5;">◎</div>
            <div class="card-title">Trust Desk</div>
            <div class="card-body">Pick a capability and region. See facilities ranked by evidence.</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/1_trust_desk.py", label="Open Trust Desk", icon="🔍")
    with c2:
        st.markdown("""
        <div class="card" style="border-left:3px solid #6366F1;">
            <div style="font-size:1.2rem;margin-bottom:0.5rem;opacity:0.5;">◈</div>
            <div class="card-title">Medical Desert</div>
            <div class="card-body">Map showing where healthcare is missing across India.</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/3_medical_desert.py", label="Open Medical Desert", icon="🗺")
    with c3:
        st.markdown("""
        <div class="card" style="border-left:3px solid #6366F1;">
            <div style="font-size:1.2rem;margin-bottom:0.5rem;opacity:0.5;">▦</div>
            <div class="card-title">Data Readiness</div>
            <div class="card-body">Check data quality — what's missing, what contradicts.</div>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/4_data_readiness.py", label="Open Data Readiness", icon="📊")

    # ── FOOTER ──
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1rem;margin-top:2.5rem;border-top:1px solid #E2E8F0;">
        <div style="font-size:0.75rem;color:#94A3B8;font-weight:500;">
            Built for Databricks × Hack-Nation Challenge 04
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
