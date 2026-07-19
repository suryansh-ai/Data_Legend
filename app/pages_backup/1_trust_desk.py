"""
Trust Desk — Find facilities you can trust.
"""
import streamlit as st
import sys, os
_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_PAGES_DIR)
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
sys.path.insert(0, _APP_DIR)
sys.path.insert(0, _PROJECT_ROOT)

try:
    from components.css import inject_css, nav
    from utils.data_loader import load_facilities, get_unique_states, get_unique_cities
except Exception:
    pass

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except Exception:
    MLFLOW_AVAILABLE = False

st.set_page_config(page_title="Trust Desk — Data Legend", page_icon="🔍", layout="wide")
inject_css()
nav("trust")


def main():
    facilities = load_facilities()
    if facilities.empty:
        st.error("No data loaded.")
        return

    # ── HERO ──
    st.markdown("""
    <div class="hero">
        <div class="hero-pill">Trust Desk</div>
        <h1>Find facilities you can <span class="hl">trust.</span></h1>
        <p class="hero-sub" style="margin-bottom:0;">Pick a capability and region. We'll rank the facilities by how much evidence backs up their claims.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── FILTERS ──
    f1, f2, f3, f4 = st.columns([2, 2, 2, 0.8])
    with f1:
        cap = st.selectbox("Capability", ["All","ICU","NICU","Maternity","Emergency","Oncology","Trauma","Dialysis","Surgery","Pharmacy","Laboratory","Radiology","Cardiology","Ophthalmology","Orthopedics","Pediatrics","Dental"], label_visibility="collapsed")
    with f2:
        states = get_unique_states(facilities)
        state = st.selectbox("State", ["All States"] + states, label_visibility="collapsed")
    with f3:
        cities = get_unique_cities(facilities, state)
        city = st.selectbox("City", ["All Cities"] + cities, label_visibility="collapsed")
    with f4:
        sort = st.selectbox("Sort", ["Trust Score","Name","City"], label_visibility="collapsed")

    # ── FILTER DATA ──
    f = facilities.copy()
    if state != "All States":
        f = f[f["address_stateOrRegion"] == state]
    if city != "All Cities":
        f = f[f["address_city"] == city]

    if sort == "Trust Score":
        f = f.sort_values("_trust_score", ascending=False)
    elif sort == "Name":
        f = f.sort_values("name")
    else:
        f = f.sort_values("address_city")

    total = len(f)

    if MLFLOW_AVAILABLE:
        try:
            with mlflow.start_run(run_name="trust_desk_filter", nested=True):
                mlflow.log_param("capability", cap)
                mlflow.log_param("state", state)
                mlflow.log_param("city", city)
                mlflow.log_param("sort", sort)
                mlflow.log_metric("result_count", total)
        except Exception:
            pass

    if total > 0:
        corr_n = int((f["_trust_signal"] == "CORROBORATED").sum())
        claimed_n = int((f["_trust_signal"] == "CLAIMED_ONLY").sum())
        avg_t = f["_trust_score"].mean()

        st.markdown(f"""
        <div class="grid-4">
            <div class="tile"><div class="tile-top"><div class="tile-icon navy">🏥</div></div><div class="tile-value">{total:,}</div><div class="tile-label">Facilities</div></div>
            <div class="tile"><div class="tile-top"><div class="tile-icon green">✓</div></div><div class="tile-value" style="color:#059669;">{corr_n}</div><div class="tile-label">Corroborated</div></div>
            <div class="tile"><div class="tile-top"><div class="tile-icon amber">!</div></div><div class="tile-value" style="color:#D97706;">{claimed_n}</div><div class="tile-label">Claimed Only</div></div>
            <div class="tile"><div class="tile-top"><div class="tile-icon navy">◆</div></div><div class="tile-value">{avg_t:.0f}%</div><div class="tile-label">Avg Trust</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── RESULTS ──
    if f.empty:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">◎</div>
            <div class="empty-title">No results found</div>
            <div class="empty-desc">Try broadening your filters — remove the city or try a different state.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f'<div class="sec-title">Showing {min(total, 50)} of {total} facilities</div>', unsafe_allow_html=True)

    for idx, (_, row) in enumerate(f.head(50).iterrows()):
        name = row.get("name", "Unknown")
        ct = row.get("address_city", "")
        st_ = row.get("address_stateOrRegion", "")
        score = row["_trust_score"]
        signal = row["_trust_signal"]
        claims = row["_total_claims"]
        corr = row["_corroborated"]

        sig_cls = "badge-green" if signal == "CORROBORATED" else "badge-yellow" if signal == "CLAIMED_ONLY" else "badge-red" if signal == "WEAK" else "badge-gray"
        bar_cls = "teal" if score >= 70 else "amber" if score >= 40 else "rose" if score > 0 else "gray"
        score_color = "#059669" if score >= 70 else "#D97706" if score >= 40 else "#94A3B8"

        loc = f"{ct}, {st_}" if ct else "Location unknown"

        st.markdown(f"""
        <div class="fac-item">
            <div class="fac-rank">#{idx+1}</div>
            <div class="fac-info">
                <div class="fac-name">{name}</div>
                <div class="fac-loc">{loc}</div>
                <div class="bar-track" style="margin-top:0.5rem;">
                    <div class="bar-fill {bar_cls}" style="width:{score}%"></div>
                </div>
            </div>
            <div class="fac-right">
                <span class="badge {sig_cls}">{signal}</span>
                <div class="fac-score" style="color:{score_color};">{score:.0f}%</div>
                <div class="fac-meta">{claims} claims · {corr} verified</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uid = row.get("unique_id", "")
        if uid and st.button("View Details →", key=f"d{uid}", use_container_width=True):
            st.session_state.selected_facility = uid
            st.switch_page("pages/2_facility_detail.py")

    if total > 50:
        st.info(f"Showing top 50 of {total}. Use filters to narrow.")


if __name__ == "__main__":
    main()
