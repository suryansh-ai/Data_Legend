"""
Facility Detail — Full evidence breakdown.
"""
import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.css import inject_css, nav
from utils.data_loader import load_facilities, get_facility_by_id
from utils.lakebase import LakebaseClient
from pipeline.trust_engine import TrustEngine

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

st.set_page_config(page_title="Facility Detail — Data Legend", page_icon="🏥", layout="wide")
inject_css()
nav("trust")

engine = TrustEngine()
db = LakebaseClient()

def pjson(v):
    if v is None: return []
    if isinstance(v, list): return v
    if isinstance(v, str):
        try:
            p = json.loads(v)
            if isinstance(p, list): return p
        except: pass
        return [x.strip() for x in v.split(",") if x.strip()]
    return []


def main():
    if "selected_facility" not in st.session_state:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">🏥</div>
            <div class="empty-title">No facility selected</div>
            <div class="empty-desc">Go to Trust Desk and click on a facility.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("← Trust Desk"):
            st.switch_page("pages/1_trust_desk.py")
        return

    fid = st.session_state.selected_facility
    facilities = load_facilities()
    fac = get_facility_by_id(facilities, fid)
    if not fac:
        st.error("Not found.")
        return

    trust = engine.score_facility(fac)
    name = fac.get("name", "Unknown")
    city = fac.get("address_city", "")
    state = fac.get("address_stateOrRegion", "")
    pin = fac.get("address_zipOrPostcode", "N/A")
    score = trust["overall_trust"]
    signal = trust["overall_signal"]

    sig_cls = "badge-green" if signal == "CORROBORATED" else "badge-yellow" if signal == "CLAIMED_ONLY" else "badge-red" if signal == "WEAK" else "badge-gray"
    bar_cls = "teal" if score >= 70 else "amber" if score >= 40 else "rose" if score > 0 else "gray"
    score_color = "#059669" if score >= 70 else "#D97706" if score >= 40 else "#94A3B8"

    # ── HEADER ──
    st.markdown(f"""
    <div class="hero">
        <h1 style="margin-top:0;">{name}</h1>
        <p class="hero-sub" style="margin-bottom:0;">{city}, {state} · PIN {pin}</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_trust_desk.py", label="Back to Trust Desk", icon="◀")

    # ── SCORE TILES ──
    st.markdown(f"""
    <div class="grid-4">
        <div class="tile" style="grid-column:span 2;">
            <div class="tile-top"><div class="tile-icon teal"><div style="width:10px;height:10px;border-radius:50%;background:{'#34D399' if score>=70 else '#FBBF24' if score>=40 else '#9CA3AF'};"></div></div></div>
            <div class="tile-value" style="color:{score_color};">{score:.0f}/100</div>
            <div class="tile-label">Trust Score</div>
            <div class="bar-track" style="height:6px;margin-top:0.6rem;">
                <div class="bar-fill {bar_cls}" style="width:{score}%"></div>
            </div>
            <div style="margin-top:0.5rem;"><span class="badge {sig_cls}">{signal}</span></div>
        </div>
        <div class="tile"><div class="tile-top"><div class="tile-icon navy">☐</div></div><div class="tile-value">{trust['metadata']['total_claims']}</div><div class="tile-label">Claims</div></div>
        <div class="tile"><div class="tile-top"><div class="tile-icon green">✓</div></div><div class="tile-value" style="color:#059669;">{trust['metadata']['corroborated_claims']}</div><div class="tile-label">Corroborated</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── EVIDENCE ──
    st.markdown('<div class="sec-title">Evidence by Field</div>', unsafe_allow_html=True)

    fields = [
        ("description", "Description", "Narrative text", "High"),
        ("capability", "Capabilities", "Extracted claims", "Medium"),
        ("procedure", "Procedures", "Extracted claims", "Medium"),
        ("equipment", "Equipment", "Extracted claims", "Medium"),
        ("specialties", "Specialties", "Structured tags", "Supporting"),
    ]

    for field, label, desc, weight in fields:
        value = fac.get(field, "")
        items = pjson(value) if field != "description" else ([value] if value else [])
        cap_info = trust["capabilities"].get(field, {})
        evidence = cap_info.get("evidence", [])
        ev_fields = [e["field"] for e in evidence]

        with st.expander(f"{label} — {weight} weight · {desc}", expanded=(field == "description")):
            if field == "description":
                if value:
                    st.markdown(f'<div class="ev-block"><div style="font-size:0.85rem;color:#64748B;line-height:1.7;">{value}</div></div>', unsafe_allow_html=True)
                else:
                    st.info("No description available.")
            else:
                if items:
                    h = "".join([f'<div class="ev-row"><div class="ev-dot {"on" if field in ev_fields else "off"}"></div><span>{x}</span></div>' for x in items])
                    st.markdown(f'<div class="ev-block"><div class="ev-label">{len(items)} items</div>{h}</div>', unsafe_allow_html=True)
                else:
                    st.info(f"No {label.lower()} data.")

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── GAPS ──
    st.markdown('<div class="sec-title">What we don\'t know</div>', unsafe_allow_html=True)
    gaps = [l for f, l in [("description","Description"),("capability","Capability"),("procedure","Procedure"),("equipment","Equipment"),("specialties","Specialties")] if not fac.get(f)]
    if gaps:
        h = "".join([f'<div class="ev-row"><div class="ev-dot off"></div><span><strong>{g}</strong> — Not reported</span></div>' for g in gaps])
        st.markdown(f'<div class="ev-block" style="border-left:3px solid #FBBF24;">{h}</div>', unsafe_allow_html=True)
    else:
        st.success("All key fields have data.")

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── ACTIONS ──
    st.markdown('<div class="sec-title">Actions</div>', unsafe_allow_html=True)

    # Show existing override if present
    existing_override = db.get_override(fid)
    if existing_override:
        st.info(f"Current override: {existing_override['original_score']:.0f}% → {existing_override['new_score']:.0f}% ({existing_override['reason']})")

    # Show existing notes
    existing_notes = db.get_notes(fid)
    if existing_notes:
        with st.expander(f"Notes ({len(existing_notes)})", expanded=False):
            for note in existing_notes:
                st.markdown(f'<div style="padding:0.4rem 0;border-bottom:1px solid #F1F5F9;font-size:0.825rem;color:#64748B;">{note["note"]} <span style="color:#94A3B8;font-size:0.7rem;">{note["created_at"]}</span></div>', unsafe_allow_html=True)

    # Show if shortlisted
    shortlisted = fid in st.session_state.get("shortlist", [])

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        if st.button("Override", use_container_width=True):
            st.session_state.show_override = True
    with a2:
        if st.button("Add Note", use_container_width=True):
            st.session_state.show_note = True
    with a3:
        label = "Remove from Shortlist" if shortlisted else "Shortlist"
        if st.button(label, use_container_width=True):
            sl = st.session_state.setdefault("shortlist", [])
            if fid not in sl:
                db.add_to_shortlist(fid)
                sl.append(fid)
                st.toast("Added to shortlist!")
            else:
                db.remove_from_shortlist(fid)
                sl.remove(fid)
                st.toast("Removed from shortlist.")
            st.rerun()
    with a4:
        if st.button("Flag", use_container_width=True):
            st.session_state.show_flag = True

    if st.session_state.get("show_override"):
        with st.form("ov"):
            st.markdown("**Override Trust Score**")
            ns = st.slider("Score", 0, 100, int(score))
            r = st.text_area("Reason")
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Save", type="primary"):
                    db.add_override(fid, score, ns, r)
                    if MLFLOW_AVAILABLE:
                        try:
                            mlflow.log_param("action", "override")
                            mlflow.log_param("facility_id", fid)
                            mlflow.log_metric("original_score", score)
                            mlflow.log_metric("override_score", ns)
                        except Exception:
                            pass
                    st.toast(f"Override saved: {score:.0f}% → {ns}%")
                    st.session_state.show_override = False
                    st.rerun()
            with c2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_override = False
                    st.rerun()

    if st.session_state.get("show_note"):
        with st.form("nt"):
            st.markdown("**Add Note**")
            n = st.text_area("Note")
            if st.form_submit_button("Save", type="primary"):
                if n.strip():
                    db.add_note(fid, n.strip())
                    if MLFLOW_AVAILABLE:
                        try:
                            mlflow.log_param("action", "note")
                            mlflow.log_param("facility_id", fid)
                        except Exception:
                            pass
                    st.toast("Note saved!")
                st.session_state.show_note = False
                st.rerun()

    if st.session_state.get("show_flag"):
        with st.form("fl"):
            st.markdown("**Flag for Review**")
            ft = st.selectbox("Flag Type", ["Inconsistent Data", "Missing Capability", "Outdated Record", "Wrong Location", "Other"])
            fr = st.text_area("Reason")
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Flag", type="primary"):
                    db.flag_for_review(fid, ft, fr)
                    if MLFLOW_AVAILABLE:
                        try:
                            mlflow.log_param("action", "flag")
                            mlflow.log_param("facility_id", fid)
                            mlflow.set_tag("flag_type", ft)
                        except Exception:
                            pass
                    st.toast(f"Flagged: {ft}")
                    st.session_state.show_flag = False
                    st.rerun()
            with c2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_flag = False
                    st.rerun()


if __name__ == "__main__":
    main()
