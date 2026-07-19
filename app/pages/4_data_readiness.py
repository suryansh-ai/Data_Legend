"""
Data Readiness — Data quality dashboard.
"""
import streamlit as st
import json, sys, os
_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_PAGES_DIR)
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
sys.path.insert(0, _APP_DIR)
sys.path.insert(0, _PROJECT_ROOT)
from components.css import inject_css, nav
from utils.data_loader import load_facilities
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Data Readiness — Data Legend", page_icon="📊", layout="wide")
inject_css()
nav("readiness")


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
    facilities = load_facilities()
    if facilities.empty:
        st.error("No data loaded.")
        return

    total = len(facilities)

    # ── HERO ──
    st.markdown("""
    <div class="hero">
        <div class="hero-pill">Data Readiness</div>
        <h1>How <span class="hl">clean</span> is the data?</h1>
        <p class="hero-sub" style="margin-bottom:0;">Before you trust any analysis, check the data quality. See what's missing, what contradicts, and what needs attention.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── OVERVIEW ──
    trust_dist = facilities["_trust_signal"].value_counts()
    avg_score = facilities["_trust_score"].mean()
    pct_high = (facilities["_trust_score"] >= 70).sum() / total * 100
    pct_low = (facilities["_trust_score"] < 40).sum() / total * 100

    st.markdown(f"""
    <div class="grid-4">
        <div class="tile"><div class="tile-top"><div class="tile-icon navy">☐</div></div><div class="tile-value">{total:,}</div><div class="tile-label">Total Facilities</div></div>
        <div class="tile"><div class="tile-top"><div class="tile-icon green">✓</div></div><div class="tile-value" style="color:#059669;">{pct_high:.1f}%</div><div class="tile-label">High Trust (≥70%)</div></div>
        <div class="tile"><div class="tile-top"><div class="tile-icon amber">!</div></div><div class="tile-value" style="color:#D97706;">{avg_score:.0f}%</div><div class="tile-label">Avg Trust Score</div></div>
        <div class="tile"><div class="tile-top"><div class="tile-icon rose">✗</div></div><div class="tile-value" style="color:#DC2626;">{pct_low:.1f}%</div><div class="tile-label">Low Trust (&lt;40%)</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── TRUST DISTRIBUTION DONUT ──
    st.markdown('<div class="sec-title">Trust Signal Distribution</div>', unsafe_allow_html=True)

    signal_colors = {"CORROBORATED": "#059669", "CLAIMED_ONLY": "#D97706", "WEAK": "#DC2626", "UNKNOWN": "#94A3B8"}
    signal_labels = {"CORROBORATED": "Corroborated", "CLAIMED_ONLY": "Claimed Only", "WEAK": "Weak", "UNKNOWN": "Unknown"}

    labels, values, colors = [], [], []
    for sig, count in trust_dist.items():
        labels.append(signal_labels.get(sig, sig))
        values.append(count)
        colors.append(signal_colors.get(sig, "#94A3B8"))

    fig_donut = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=colors, line=dict(width=0)),
        textinfo="label+percent", textposition="outside",
        textfont=dict(size=11, family="Inter, -apple-system, sans-serif"),
    ))
    fig_donut.update_layout(
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A"),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(text=f"<b>{total:,}</b><br>Total", x=0.5, y=0.5, font_size=16, showarrow=False, font=dict(color="#0F172A", family="Inter, -apple-system, sans-serif"))],
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── FIELD COMPLETENESS ──
    st.markdown('<div class="sec-title">Field Completeness</div>', unsafe_allow_html=True)

    key_fields = [
        ("name", "Name"),
        ("description", "Description"),
        ("address_stateOrRegion", "State"),
        ("address_city", "City"),
        ("address_zipOrPostcode", "PIN Code"),
        ("latitude", "Latitude"),
        ("longitude", "Longitude"),
        ("capability", "Capabilities"),
        ("procedure", "Procedures"),
        ("equipment", "Equipment"),
        ("specialties", "Specialties"),
        ("numberDoctors", "Doctor Count"),
        ("capacity", "Capacity"),
    ]

    field_stats = []
    for field, label in key_fields:
        non_null = facilities[field].notna().sum()
        non_empty = non_null
        if field in ["capability", "procedure", "equipment", "specialties"]:
            non_empty = facilities[field].apply(lambda x: bool(pjson(x))).sum()
        elif field == "description":
            non_empty = facilities[field].apply(lambda x: bool(str(x).strip()) if pd.notna(x) else False).sum()
        pct = non_empty / total * 100
        field_stats.append({"field": label, "pct": pct, "count": int(non_empty)})

    field_df = pd.DataFrame(field_stats).sort_values("pct", ascending=True)

    fig_bar = go.Figure()
    bar_colors = ["#059669" if p >= 90 else "#D97706" if p >= 50 else "#DC2626" for p in field_df["pct"]]
    fig_bar.add_trace(go.Bar(
        y=field_df["field"],
        x=field_df["pct"],
        orientation="h",
        marker_color=bar_colors,
        text=field_df["pct"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Complete: %{x:.1f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        height=450,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A"),
        xaxis=dict(title="% Complete", range=[0, 105], gridcolor="#F1F5F9", showgrid=True, gridwidth=1),
        yaxis=dict(showgrid=False),
        margin=dict(l=100, r=40, t=10, b=40),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── TRUST SCORE HISTOGRAM ──
    st.markdown('<div class="sec-title">Trust Score Distribution</div>', unsafe_allow_html=True)

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=facilities["_trust_score"],
        nbinsx=25,
        marker_color="#6366F1",
        opacity=0.8,
        hovertemplate="Score %{x:.0f}<br>Count: %{y}<extra></extra>",
    ))
    fig_hist.add_vline(x=70, line_dash="dash", line_color="#059669", annotation_text="High Trust (70%)", annotation_position="top right")
    fig_hist.add_vline(x=40, line_dash="dash", line_color="#D97706", annotation_text="Low Trust (40%)", annotation_position="top left")
    fig_hist.update_layout(
        height=350,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A"),
        xaxis=dict(title="Trust Score (%)", range=[0, 105], gridcolor="#F1F5F9"),
        yaxis=dict(title="Count", gridcolor="#F1F5F9"),
        margin=dict(l=40, r=20, t=20, b=40),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── SUSPICIOUS CLAIMS ──
    st.markdown('<div class="sec-title">Suspicious Claims</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body" style="margin-bottom:1rem;">Facilities where the description says "planned" or "under development" but claims to offer services — a sign of aspirational data.</div>', unsafe_allow_html=True)

    susp = facilities[facilities["_trust_score"] < 40].sort_values("_trust_score").head(10)
    if susp.empty:
        st.success("No suspicious claims found. All records have trust score ≥ 40%.")
    else:
        for _, row in susp.iterrows():
            name = row.get("name", "Unknown")
            city = row.get("address_city", "")
            state = row.get("address_stateOrRegion", "")
            score = row["_trust_score"]
            signal = row["_trust_signal"]
            sig_cls = "badge-red" if signal == "WEAK" else "badge-yellow"
            desc = str(row.get("description", ""))[:150]

            st.markdown(f"""
            <div class="fac-item" style="border-left-color:#DC2626;">
                <div class="fac-rank" style="color:#DC2626;">!</div>
                <div class="fac-info">
                    <div class="fac-name">{name}</div>
                    <div class="fac-loc">{city}, {state}</div>
                    <div class="fac-meta" style="margin-top:0.3rem;font-style:italic;">"{desc}..."</div>
                </div>
                <div class="fac-right">
                    <span class="badge {sig_cls}">{signal}</span>
                    <div class="fac-score" style="color:#DC2626;">{score:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sec-line"></div>', unsafe_allow_html=True)

    # ── HIGH-LEVERAGE RECORDS ──
    st.markdown('<div class="sec-title">High-Leverage Records</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-body" style="margin-bottom:1rem;">Records with 10+ verified claims that can anchor entire regions. These are your highest-confidence facilities.</div>', unsafe_allow_html=True)

    high = facilities[facilities["_corroborated"] >= 10].sort_values("_trust_score", ascending=False).head(10)
    if high.empty:
        st.info("No records with 10+ verified claims yet.")
    else:
        for _, row in high.iterrows():
            name = row.get("name", "Unknown")
            city = row.get("address_city", "")
            state = row.get("address_stateOrRegion", "")
            score = row["_trust_score"]
            corr = row["_corroborated"]
            claims = row["_total_claims"]

            st.markdown(f"""
            <div class="fac-item" style="border-left-color:#059669;">
                <div class="fac-rank" style="color:#059669;">★</div>
                <div class="fac-info">
                    <div class="fac-name">{name}</div>
                    <div class="fac-loc">{city}, {state}</div>
                    <div class="fac-meta">{corr} of {claims} claims verified</div>
                </div>
                <div class="fac-right">
                    <span class="badge badge-green">CORROBORATED</span>
                    <div class="fac-score" style="color:#059669;">{score:.0f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
