import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# SME Pulse — Business Health Dashboard
# Atlantic Technological University · FunTech Project
# Callum Kidd · 2026
# ═══════════════════════════════════════════════════════════

# ATU Brand Colours
ATU_TEAL = "#00838A"
ATU_GREEN = "#4CA771"
ATU_NAVY = "#1B2A4A"
ATU_RED = "#D94040"
ATU_AMBER = "#D4930D"
ATU_BG = "#F7F8FA"
ATU_WHITE = "#FFFFFF"
ATU_BORDER = "#E2E6EC"
ATU_TEXT_MID = "#4A5568"
ATU_TEXT_MUTED = "#8896AB"

# ── Page config ──
st.set_page_config(
    page_title="SME Pulse · Business Health Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for ATU branding ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    /* Global */
    .stApp {
        background-color: #F7F8FA;
        font-family: 'Source Sans 3', sans-serif;
    }

    /* ATU Brand Bar */
    .atu-brand-bar {
        height: 4px;
        background: linear-gradient(90deg, #00838A, #4CA771, #1B2A4A);
        margin: -1rem -1rem 0 -1rem;
        border-radius: 0;
    }

    /* Header */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0 16px;
        border-bottom: 1px solid #E2E6EC;
        margin-bottom: 20px;
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-mark {
        width: 36px; height: 36px;
        background: #00838A;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 18px; font-weight: 700;
        font-family: 'Playfair Display', serif;
    }
    .header-title {
        font-size: 20px; font-weight: 700; color: #1B2A4A;
        font-family: 'Playfair Display', serif; letter-spacing: -0.3px;
    }
    .header-sub {
        font-size: 11px; color: #00838A; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1.2px;
    }
    .header-desc {
        font-size: 10px; color: #8896AB; margin-top: -2px;
    }

    /* Welcome */
    .welcome-title {
        font-size: 24px; font-weight: 700; color: #1B2A4A;
        font-family: 'Playfair Display', serif; margin: 0;
    }
    .welcome-sub {
        font-size: 13px; color: #4A5568; margin-top: 4px;
    }
    .live-badge {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 11px; color: #8896AB;
    }
    .live-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: #4CA771; display: inline-block;
        box-shadow: 0 0 6px rgba(76,167,113,0.6);
        animation: pulse 2s infinite;
    }

    /* Cards */
    .metric-card {
        background: white;
        border: 1px solid #E2E6EC;
        border-radius: 14px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(27,42,74,0.04);
    }
    .metric-card .top-accent {
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
    }
    .card-label {
        font-size: 11px; color: #8896AB; text-transform: uppercase;
        letter-spacing: 1px; font-weight: 600; margin-bottom: 4px;
    }
    .card-value {
        font-size: 28px; font-weight: 700; color: #1B2A4A;
        letter-spacing: -0.5px; font-family: 'Source Sans 3', sans-serif;
    }
    .card-sub {
        font-size: 11px; color: #4A5568; margin-top: 2px;
    }

    /* RAG badges */
    .rag-badge {
        display: inline-flex; align-items: center; gap: 5px;
        font-size: 11px; font-weight: 600; padding: 3px 10px;
        border-radius: 20px;
    }
    .rag-green { color: #4CA771; background: #E8F5ED; }
    .rag-amber { color: #D4930D; background: #FEF7E8; }
    .rag-red { color: #D94040; background: #FDF0F0; }

    .rag-dot {
        width: 7px; height: 7px; border-radius: 50%; display: inline-block;
    }

    /* Alert rows */
    .alert-row {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 14px; border-radius: 10px;
        font-size: 13px; line-height: 1.4; margin-bottom: 8px;
    }
    .alert-danger { background: #FDF0F0; border: 1px solid rgba(217,64,64,0.13); color: #D94040; }
    .alert-warning { background: #FEF7E8; border: 1px solid rgba(212,147,13,0.13); color: #D4930D; }
    .alert-info { background: #E0F4F4; border: 1px solid rgba(0,131,138,0.13); color: #00838A; }
    .alert-deviation {
        font-size: 11px; font-weight: 700; white-space: nowrap;
        margin-left: auto; opacity: 0.8;
    }

    /* Section headers */
    .section-header {
        font-size: 13px; font-weight: 700; color: #8896AB;
        text-transform: uppercase; letter-spacing: 1.5px;
        margin: 20px 0 12px; font-family: 'Source Sans 3', sans-serif;
    }

    /* Milestone table */
    .milestone-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 11px 0; border-bottom: 1px solid #EEF0F4;
    }
    .milestone-row:last-child { border-bottom: none; }
    .milestone-label {
        display: flex; align-items: center; gap: 10px;
        font-size: 13px; font-weight: 500; color: #1B2A4A;
    }
    .milestone-values {
        display: flex; align-items: center; gap: 14px;
    }
    .milestone-actual {
        font-size: 13px; font-weight: 600; color: #1B2A4A;
    }
    .milestone-target {
        font-size: 11px; color: #8896AB;
    }

    /* Cashflow rows */
    .cashflow-row {
        display: flex; align-items: center; justify-content: space-between;
        padding: 11px 0; border-bottom: 1px solid #EEF0F4;
    }
    .cashflow-row:last-child { border-bottom: none; }
    .cf-left { display: flex; align-items: center; gap: 10px; }
    .cf-dot { width: 7px; height: 7px; border-radius: 50%; }
    .cf-desc { font-size: 13px; font-weight: 500; color: #1B2A4A; }
    .cf-date { font-size: 10px; color: #8896AB; }
    .cf-amount-in { font-size: 13px; font-weight: 600; color: #4CA771; }
    .cf-amount-out { font-size: 13px; font-weight: 600; color: #D94040; }

    /* Action buttons */
    .action-btn {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 12px; margin-bottom: 6px;
        background: #F7F8FA; border: 1px solid #E2E6EC;
        border-radius: 9px; width: 100%; cursor: pointer;
        transition: all 0.2s;
    }
    .action-btn:hover {
        border-color: #00838A; background: rgba(0,131,138,0.06);
    }
    .action-label { font-size: 12px; font-weight: 600; color: #1B2A4A; }
    .action-desc { font-size: 10px; color: #8896AB; }

    /* Snapshot card */
    .snapshot-card {
        background: rgba(0,131,138,0.06);
        border: 1px solid rgba(0,131,138,0.1);
        border-radius: 14px; padding: 18px;
    }
    .snapshot-title {
        font-size: 10px; color: #00838A; text-transform: uppercase;
        letter-spacing: 1.1px; font-weight: 600; margin-bottom: 10px;
    }
    .snapshot-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 5px 0;
    }
    .snapshot-label { font-size: 11px; color: #4A5568; }
    .snapshot-value { font-size: 12px; font-weight: 600; color: #1B2A4A; }

    /* Footer */
    .footer {
        margin-top: 32px; padding-top: 16px;
        border-top: 1px solid #E2E6EC;
        display: flex; justify-content: space-between;
        font-size: 11px; color: #8896AB;
    }
    .footer-brand { font-weight: 600; color: #00838A; }

    /* Streamlit overrides */
    .stMetric { background: transparent; }
    div[data-testid="stMetricValue"] { font-family: 'Source Sans 3', sans-serif; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1rem; }

    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.35; }
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #F7F8FA;
        border-radius: 10px;
        padding: 3px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 16px;
        font-family: 'Source Sans 3', sans-serif;
    }
    .stTabs [aria-selected="true"] {
        background: #00838A !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ATU BRAND BAR
# ══════════════════════════════════════════════
st.markdown('<div class="atu-brand-bar"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
header_col1, header_col2 = st.columns([8, 4])
with header_col1:
    st.markdown("""
    <div class="header-logo">
        <div class="logo-mark">S</div>
        <div>
            <span class="header-title">SME Pulse</span>
            <span class="header-sub" style="margin-left: 8px;">ATU FunTech</span>
            <div class="header-desc">Business Health Dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with header_col2:
    st.markdown("""
    <div style="text-align: right; padding-top: 8px;">
        <span class="live-badge">
            Live · updated 2 min ago
            <span class="live-dot"></span>
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr style="margin: 8px 0 16px; border: none; border-top: 1px solid #E2E6EC;">', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# VIEW TOGGLE
# ══════════════════════════════════════════════
view_col1, view_col2 = st.columns([8, 4])
with view_col1:
    st.markdown(f"""
    <h1 class="welcome-title">Good morning, Liam</h1>
    <p class="welcome-sub">Here's how your business is doing · <span style="color: #8896AB;">March 9, 2026</span></p>
    """, unsafe_allow_html=True)
with view_col2:
    view_mode = st.radio("View", ["Owner", "Board"], horizontal=True, label_visibility="collapsed")


# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab_overview, tab_cashflow, tab_revenue, tab_alerts = st.tabs(["◉ Overview", "◈ Cash Flow", "◆ Revenue", "△ Alerts"])

with tab_overview:

    # ── HEALTH SCORE + RUNWAY + ALERTS ──
    col_health, col_runway, col_alerts = st.columns([1, 1, 2.5])

    with col_health:
        st.markdown('<div class="metric-card"><div class="top-accent" style="background: linear-gradient(90deg, #4CA771, transparent);"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-label" style="text-align:center;">Business Health Score</div>', unsafe_allow_html=True)

        fig_health = go.Figure(go.Indicator(
            mode="gauge+number",
            value=74,
            number={"font": {"size": 42, "color": ATU_GREEN, "family": "Source Sans 3"}},
            gauge={
                "axis": {"range": [0, 100], "visible": False},
                "bar": {"color": ATU_GREEN, "thickness": 0.82},
                "bgcolor": "#EEF0F4",
                "borderwidth": 0,
                "steps": [],
                "shape": "angular",
            },
        ))
        fig_health.update_layout(
            height=160, margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Source Sans 3"},
        )
        st.plotly_chart(fig_health, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div style="text-align:center;">
            <span style="font-size:12px; color:#4CA771; font-weight:600;">● Healthy</span><br>
            <span style="font-size:10px; color:#8896AB;">+3 pts vs last month</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_runway:
        st.markdown('<div class="metric-card"><div class="top-accent" style="background: linear-gradient(90deg, #D4930D, transparent);"></div>', unsafe_allow_html=True)
        st.markdown('<div class="card-label" style="text-align:center;">Cash Runway</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; padding: 16px 0 8px;">
            <div style="font-size:42px; font-weight:700; color:{ATU_AMBER};">8.2</div>
            <div style="font-size:12px; color:{ATU_TEXT_MID}; margin-top:-4px;">months remaining</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;"><span class="rag-badge rag-amber"><span class="rag-dot" style="background:#D4930D;"></span> Watch</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; margin-top:6px;"><span style="font-size:10px; color:{ATU_TEXT_MUTED};">Target: 12+ months</span></div>', unsafe_allow_html=True)

        runway_data = [14, 13, 12, 11, 10.5, 9.8, 9.2, 8.6, 8.2]
        fig_runway = go.Figure(go.Scatter(
            y=runway_data, mode="lines",
            line=dict(color=ATU_AMBER, width=2, shape="spline"),
            fill="tozeroy", fillcolor="rgba(212,147,13,0.08)",
        ))
        fig_runway.update_layout(
            height=50, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            showlegend=False,
        )
        st.plotly_chart(fig_runway, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_alerts:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span class="card-label">Deviation Alerts</span>
            <span class="rag-badge rag-red">3 active</span>
        </div>
        <div class="alert-row alert-danger">
            <span>⚠</span>
            <span>Onboarding cost per customer hit €1,800 — target is €1,200</span>
            <span class="alert-deviation">+50% vs plan</span>
        </div>
        <div class="alert-row alert-warning">
            <span>◈</span>
            <span>New customer acquisitions at 6 of 10 target with 3 weeks left</span>
            <span class="alert-deviation">-40% vs plan</span>
        </div>
        <div class="alert-row alert-danger">
            <span>⚠</span>
            <span>Supplier payment of €4,200 due Mar 12 — cash buffer tight</span>
            <span class="alert-deviation">3 days</span>
        </div>
        <div class="alert-row alert-info">
            <span>ℹ</span>
            <span>Revenue trending 8% above forecast — consider restocking inventory</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # ── KPI CARDS ──
    st.markdown('<div class="section-header">Key Performance Indicators</div>', unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpis = [
        {"col": kpi1, "label": "Cash Balance", "value": "€23,450", "sub": "Available now", "trend": "↑ +€2,180 this week", "trend_color": ATU_GREEN, "color": ATU_TEAL, "data": [42, 38, 45, 41, 52, 48, 55, 60, 58, 63, 67, 72], "rag": "green"},
        {"col": kpi2, "label": "Monthly Revenue", "value": "€45,200", "sub": "Feb 2026 · MRR", "trend": "↑ +8.2% vs Jan", "trend_color": ATU_GREEN, "color": ATU_GREEN, "data": [32, 35, 34, 38, 36, 41, 39, 43, 42, 45, 48, 51], "rag": "green"},
        {"col": kpi3, "label": "Total Expenses", "value": "€31,800", "sub": "Feb 2026", "trend": "↓ +12% vs Jan", "trend_color": ATU_RED, "color": ATU_RED, "data": [22, 24, 23, 26, 25, 28, 27, 30, 29, 32, 33, 34], "rag": "amber"},
        {"col": kpi4, "label": "Net Profit", "value": "€13,400", "sub": "29.6% gross margin", "trend": "↑ +2.1% margin", "trend_color": ATU_GREEN, "color": ATU_NAVY, "data": [10, 11, 10, 12, 11, 13, 12, 13, 13, 13, 14, 15], "rag": "green"},
    ]

    for kpi in kpis:
        with kpi["col"]:
            rag_class = f"rag-{kpi['rag']}"
            rag_label = {"green": "On Track", "amber": "Watch", "red": "At Risk"}[kpi["rag"]]

            st.markdown(f"""
            <div class="metric-card">
                <div class="top-accent" style="background: linear-gradient(90deg, {kpi['color']}, transparent);"></div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="card-label">{kpi['label']}</span>
                    <span class="rag-badge {rag_class}"><span class="rag-dot" style="background:{kpi['trend_color'] if kpi['rag'] != 'amber' else ATU_AMBER};"></span> {rag_label}</span>
                </div>
                <div class="card-value">{kpi['value']}</div>
                <div class="card-sub">{kpi['sub']}</div>
                <div style="font-size:11px; color:{kpi['trend_color']}; font-weight:600; margin-top:3px;">{kpi['trend']}</div>
            </div>
            """, unsafe_allow_html=True)

            fig_spark = go.Figure(go.Scatter(
                y=kpi["data"], mode="lines",
                line=dict(color=kpi["color"], width=2, shape="spline"),
                fill="tozeroy", fillcolor=f"rgba{tuple(int(kpi['color'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.08,)}",
            ))
            fig_spark.update_layout(
                height=50, margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                showlegend=False,
            )
            st.plotly_chart(fig_spark, use_container_width=True, config={"displayModeBar": False})


    # ── MILESTONES ──
    st.markdown('<div class="section-header">Operational Milestones</div>', unsafe_allow_html=True)

    milestones = [
        {"label": "Revenue Target", "status": "green", "actual": "€45.2K", "target": "€43K"},
        {"label": "New Customers", "status": "amber", "actual": "6", "target": "10"},
        {"label": "Gross Margin", "status": "green", "actual": "29.6%", "target": "28%"},
        {"label": "Churn Rate", "status": "green", "actual": "2.1%", "target": "<5%"},
        {"label": "Onboarding Costs", "status": "red", "actual": "€1,800", "target": "€1,200"},
        {"label": "Cash Runway", "status": "amber", "actual": "8.2 mo", "target": ">12 mo"},
    ]

    rag_colors = {"green": ATU_GREEN, "amber": ATU_AMBER, "red": ATU_RED}
    rag_labels = {"green": "On Track", "amber": "Watch", "red": "At Risk"}

    milestone_html = '<div class="metric-card">'
    for m in milestones:
        rc = rag_colors[m["status"]]
        rl = rag_labels[m["status"]]
        milestone_html += f"""
        <div class="milestone-row">
            <div class="milestone-label">
                <span class="rag-dot" style="background:{rc};"></span>
                {m['label']}
            </div>
            <div class="milestone-values">
                <span class="milestone-actual">{m['actual']}</span>
                <span class="milestone-target">/ {m['target']}</span>
                <span class="rag-badge rag-{m['status']}"><span class="rag-dot" style="background:{rc};"></span> {rl}</span>
            </div>
        </div>
        """
    milestone_html += '</div>'
    st.markdown(milestone_html, unsafe_allow_html=True)


    # ── CHARTS ROW ──
    st.markdown("", unsafe_allow_html=True)
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown('<div class="section-header">Revenue Trends + Forecast</div>', unsafe_allow_html=True)
        months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar*", "Apr*"]
        values = [34, 31, 42, 38, 45, 48, 51]
        colors = [ATU_GREEN] * 5 + ["rgba(76,167,113,0.35)"] * 2

        fig_rev = go.Figure(go.Bar(
            x=months, y=values,
            marker_color=colors,
            marker_line_width=0,
            text=[f"€{v}K" for v in values],
            textposition="outside",
            textfont=dict(size=10, color=ATU_TEXT_MID),
        ))
        fig_rev.update_layout(
            height=260, margin=dict(l=0, r=0, t=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=10, color=ATU_TEXT_MUTED)),
            yaxis=dict(visible=False),
            showlegend=False,
            bargap=0.35,
        )
        st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})
        st.caption("*Forecast months shown with lighter bars. Revenue trending +14% over 6 months.")

    with chart2:
        st.markdown('<div class="section-header">Cost Breakdown</div>', unsafe_allow_html=True)
        labels = ["Staff", "Rent", "Suppliers", "Other"]
        values = [42, 22, 24, 12]
        colors = [ATU_TEAL, ATU_GREEN, ATU_NAVY, ATU_TEXT_MUTED]

        fig_cost = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="white", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, family="Source Sans 3"),
            hoverinfo="label+value+percent",
        ))
        fig_cost.update_layout(
            height=260, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(family="Source Sans 3"),
        )
        st.plotly_chart(fig_cost, use_container_width=True, config={"displayModeBar": False})
        st.caption("Staff costs remain the largest expense at 42%. Supplier costs +3% QoQ.")


    # ── CASHFLOW + SIDEBAR ──
    cf_col, action_col = st.columns([2, 1])

    with cf_col:
        st.markdown('<div class="section-header">Cash Flow Forecast</div>', unsafe_allow_html=True)

        cashflow_items = [
            {"date": "Mar 10", "desc": "Staff wages", "amount": "-€8,400", "type": "out"},
            {"date": "Mar 12", "desc": "Client payment — Galway Hotel Group", "amount": "+€6,200", "type": "in"},
            {"date": "Mar 13", "desc": "Supplier payment — Atlantic Goods", "amount": "-€4,200", "type": "out"},
            {"date": "Mar 18", "desc": "Client payment — Bay Fitness", "amount": "+€3,800", "type": "in"},
            {"date": "Mar 20", "desc": "Rent payment", "amount": "-€2,600", "type": "out"},
            {"date": "Mar 25", "desc": "Client payment — West Pro Services", "amount": "+€5,100", "type": "in"},
        ]

        cf_html = '<div class="metric-card">'
        for item in cashflow_items:
            dot_color = ATU_GREEN if item["type"] == "in" else ATU_RED
            amount_class = "cf-amount-in" if item["type"] == "in" else "cf-amount-out"
            cf_html += f"""
            <div class="cashflow-row">
                <div class="cf-left">
                    <span class="cf-dot" style="background:{dot_color};"></span>
                    <div>
                        <div class="cf-desc">{item['desc']}</div>
                        <div class="cf-date">{item['date']}</div>
                    </div>
                </div>
                <span class="{amount_class}">{item['amount']}</span>
            </div>
            """
        cf_html += '</div>'
        st.markdown(cf_html, unsafe_allow_html=True)

    with action_col:
        st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)

        actions = [
            {"label": "Export Report", "icon": "📄", "desc": "Board pack PDF" if view_mode == "Board" else "Download summary"},
            {"label": "Share with Accountant", "icon": "👤", "desc": "Send latest data"},
            {"label": "Set Alert Threshold", "icon": "🔔", "desc": "Custom deviation %"},
            {"label": "Compare Periods", "icon": "📊", "desc": "Month vs month"},
        ]

        actions_html = '<div class="metric-card">'
        for a in actions:
            actions_html += f"""
            <div class="action-btn">
                <span style="font-size:16px;">{a['icon']}</span>
                <div>
                    <div class="action-label">{a['label']}</div>
                    <div class="action-desc">{a['desc']}</div>
                </div>
            </div>
            """
        actions_html += '</div>'
        st.markdown(actions_html, unsafe_allow_html=True)

        st.markdown("", unsafe_allow_html=True)

        # Snapshot
        snapshot_items = [
            ("Invoices Sent", "12"),
            ("Invoices Paid", "9"),
            ("Avg Payment Time", "14 days"),
            ("Headcount" if view_mode == "Board" else "Staff Hours", "15" if view_mode == "Board" else "1,240 hrs"),
            ("Customer Acq. Cost", "€1,800"),
        ]

        snap_html = '<div class="snapshot-card"><div class="snapshot-title">This Month</div>'
        for label, value in snapshot_items:
            snap_html += f"""
            <div class="snapshot-row">
                <span class="snapshot-label">{label}</span>
                <span class="snapshot-value">{value}</span>
            </div>
            """
        snap_html += '</div>'
        st.markdown(snap_html, unsafe_allow_html=True)


# ── Cash Flow Tab ──
with tab_cashflow:
    st.markdown('<div class="section-header">Monthly Cash Flow Analysis</div>', unsafe_allow_html=True)

    months_cf = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
    inflows = [38, 42, 39, 48, 44, 51]
    outflows = [32, 35, 34, 38, 36, 39]
    net = [i - o for i, o in zip(inflows, outflows)]

    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(name="Inflows", x=months_cf, y=inflows, marker_color=ATU_GREEN, text=[f"€{v}K" for v in inflows], textposition="outside"))
    fig_cf.add_trace(go.Bar(name="Outflows", x=months_cf, y=outflows, marker_color=ATU_RED, text=[f"€{v}K" for v in outflows], textposition="outside"))
    fig_cf.add_trace(go.Scatter(name="Net", x=months_cf, y=net, mode="lines+markers", line=dict(color=ATU_TEAL, width=3), marker=dict(size=8)))
    fig_cf.update_layout(
        height=350, barmode="group", bargap=0.25,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        font=dict(family="Source Sans 3", color=ATU_TEXT_MID),
        yaxis=dict(gridcolor="#EEF0F4", tickprefix="€", ticksuffix="K"),
        xaxis=dict(tickfont=dict(size=12)),
    )
    st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False})


# ── Revenue Tab ──
with tab_revenue:
    st.markdown('<div class="section-header">Revenue by Source</div>', unsafe_allow_html=True)

    sources = ["Retail Sales", "Services", "Online", "Wholesale"]
    rev_values = [22, 12, 7, 4]
    fig_src = go.Figure(go.Bar(
        x=rev_values, y=sources, orientation="h",
        marker_color=[ATU_TEAL, ATU_GREEN, ATU_NAVY, ATU_TEXT_MUTED],
        text=[f"€{v}K" for v in rev_values], textposition="outside",
    ))
    fig_src.update_layout(
        height=250, margin=dict(l=10, r=40, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(tickfont=dict(size=13, color=ATU_NAVY)),
        showlegend=False, font=dict(family="Source Sans 3"),
    )
    st.plotly_chart(fig_src, use_container_width=True, config={"displayModeBar": False})


# ── Alerts Tab ──
with tab_alerts:
    st.markdown('<div class="section-header">All Active Alerts</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="alert-row alert-danger">
        <span>⚠</span>
        <span><strong>Critical:</strong> Onboarding cost per customer hit €1,800 — target is €1,200</span>
        <span class="alert-deviation">+50% vs plan</span>
    </div>
    <div class="alert-row alert-danger">
        <span>⚠</span>
        <span><strong>Critical:</strong> Supplier payment of €4,200 due Mar 12 — cash buffer tight</span>
        <span class="alert-deviation">3 days</span>
    </div>
    <div class="alert-row alert-warning">
        <span>◈</span>
        <span><strong>Warning:</strong> New customer acquisitions at 6 of 10 target with 3 weeks left</span>
        <span class="alert-deviation">-40% vs plan</span>
    </div>
    <div class="alert-row alert-warning">
        <span>◈</span>
        <span><strong>Warning:</strong> Cash runway projected at 8.2 months — below 12-month target</span>
        <span class="alert-deviation">-32% vs plan</span>
    </div>
    <div class="alert-row alert-info">
        <span>ℹ</span>
        <span><strong>Info:</strong> Revenue trending 8% above forecast — consider restocking inventory</span>
    </div>
    <div class="alert-row alert-info">
        <span>ℹ</span>
        <span><strong>Info:</strong> Staff overtime hours up 15% — review scheduling efficiency</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <div><span class="footer-brand">SME Pulse</span> · A FunTech Project · Atlantic Technological University</div>
    <div>Callum Kidd · 2026</div>
</div>
""", unsafe_allow_html=True)
