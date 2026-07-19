"""
Medical Desert — Map healthcare gaps across India.
"""
import streamlit as st
import pandas as pd
import sys, os
_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_PAGES_DIR)
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
sys.path.insert(0, _APP_DIR)
sys.path.insert(0, _PROJECT_ROOT)
from components.css import inject_css, nav
from utils.data_loader import load_facilities, get_dataset_stats

st.set_page_config(page_title="Medical Desert — Data Legend", page_icon="🗺️", layout="wide")
inject_css()
nav("desert")


def main():
    facilities = load_facilities()
    if facilities.empty:
        st.error("No data loaded.")
        return

    # ── HERO ──
    st.markdown("""
    <div class="hero">
        <div class="hero-pill">Medical Desert Mapper</div>
        <h1>Where is healthcare <span class="hl">missing?</span></h1>
        <p class="hero-sub" style="margin-bottom:0;">This view shows facility density and potential healthcare deserts across India. Green = well-served, red = underserved, gray = no data.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── STATE SUMMARY ──
    st.markdown('<div class="sec-title">State-by-State Overview</div>', unsafe_allow_html=True)

    state_data = (
        facilities.groupby("address_stateOrRegion")
        .agg(total=("unique_id", "count"),
             avg_trust=("_trust_score", "mean"),
             high_trust=("_trust_score", lambda x: int((x >= 70).sum())),
             low_trust=("_trust_score", lambda x: int((x < 40).sum())))
        .reset_index()
        .rename(columns={"address_stateOrRegion": "state"})
        .sort_values("total", ascending=False)
    )

    # ── BAR CHART ──
    st.markdown('<div class="sec-title" style="margin-top:1.5rem;">Facility Distribution</div>', unsafe_allow_html=True)

    import plotly.graph_objects as go

    top_states = state_data.head(25)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_states["state"],
        y=top_states["total"],
        marker_color=["#059669" if s >= 70 else "#D97706" if s >= 40 else "#DC2626" for s in top_states["avg_trust"]],
        text=top_states["total"].astype(str),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Facilities: %{y}<br>Avg Trust: %{customdata:.0f}%<extra></extra>",
        customdata=top_states["avg_trust"],
    ))
    fig.update_layout(
        height=420,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A"),
        xaxis=dict(tickangle=-45, tickfont=dict(size=10), showgrid=False),
        yaxis=dict(title="Number of Facilities", gridcolor="#F1F5F9", showgrid=True, gridwidth=1),
        margin=dict(l=40, r=20, t=20, b=100),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── TREEMAP ──
    st.markdown('<div class="sec-title">Facility Distribution Treemap</div>', unsafe_allow_html=True)

    city_state = facilities.groupby(["address_stateOrRegion", "address_city"]).agg(
        count=("unique_id", "count"),
        avg_trust=("_trust_score", "mean")
    ).reset_index().dropna(subset=["address_city"])

    import plotly.express as px
    fig2 = px.treemap(
        city_state,
        path=["address_stateOrRegion", "address_city"],
        values="count",
        color="avg_trust",
        color_continuous_scale=["#DC2626", "#FBBF24", "#059669"],
        range_color=[0, 100],
    )
    fig2.update_layout(
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color="#0F172A"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    fig2.update_traces(
        textinfo="label+value",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Facilities: %{value}<br>Avg Trust: %{color:.0f}%<extra></extra>",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── STATE TABLE ──
    st.markdown('<div class="sec-title">All States</div>', unsafe_allow_html=True)

    st.dataframe(
        state_data.style.background_gradient(subset=["total"], cmap="Blues").background_gradient(subset=["avg_trust"], cmap="RdYlGn"),
        use_container_width=True,
        height=400,
        column_config={
            "state": "State",
            "total": "Facilities",
            "avg_trust": st.column_config.NumberColumn("Avg Trust %", format="%.1f%%"),
            "high_trust": "High Trust (≥70%)",
            "low_trust": "Low Trust (<40%)",
        },
        hide_index=True,
    )

    # ── TOP 10 UNDERSERVED ──
    st.markdown('<div class="sec-title" style="margin-top:1.5rem;">Top 10 Most Underserved States</div>', unsafe_allow_html=True)

    underserved = state_data.copy()
    underserved["underserved_score"] = (
        (1 - underserved["avg_trust"] / 100) * 0.6 +
        (underserved["low_trust"] / underserved["total"]) * 0.4
    ).fillna(0)
    underserved = underserved.sort_values("underserved_score", ascending=False).head(10)

    cols = st.columns(5)
    for i, (_, row) in enumerate(underserved.iterrows()):
        with cols[i % 5]:
            bar_cls = "rose" if row["underserved_score"] > 0.5 else "amber"
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div class="card-title" style="font-size:0.85rem;">{row['state']}</div>
                <div class="card-body">{int(row['total'])} facilities</div>
                <div class="bar-track" style="height:4px;margin:0.5rem 0;">
                    <div class="bar-fill {bar_cls}" style="width:{row['underserved_score']*100}%"></div>
                </div>
                <div class="card-body" style="font-size:0.7rem;">Underserved: {row['underserved_score']:.0%}</div>
            </div>""", unsafe_allow_html=True)

    # ── METHODOLOGY ──
    st.markdown('<div class="sec-title" style="margin-top:1.5rem;">Methodology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="border-left:3px solid #6366F1;">
        <div class="card-title">How we classify underserved areas</div>
        <div class="card-body">
            <strong style="color:#0F172A;">Underserved Score</strong> = 60% × (1 - avg_trust) + 40% × (low_trust / total)<br><br>
            <strong>Low trust</strong> means trust score below 40%. <strong>High trust</strong> means 70%+.<br>
            States with few facilities and low average trust scores are flagged as most underserved.
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
