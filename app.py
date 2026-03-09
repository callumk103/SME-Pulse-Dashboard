import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from sheets_backend import (
    get_gspread_client, get_spreadsheet, ensure_sheets,
    read_df, read_info, upload_excel, compute_metrics, sample_metrics
)

# ═══════════════════════════════════════════════════════════
# SME Pulse — Business Health Dashboard
# Atlantic Technological University · FunTech Project
# Callum Kidd · 2026
# ═══════════════════════════════════════════════════════════

ATU = {"teal": "#00838A", "green": "#4CA771", "navy": "#1B2A4A", "red": "#D94040",
       "amber": "#D4930D", "bg": "#F7F8FA", "white": "#FFFFFF", "mid": "#4A5568", "muted": "#8896AB"}

st.set_page_config(page_title="SME Pulse", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ── CSS ──
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp { background-color: #F7F8FA; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { background: white; border-right: 1px solid #E2E6EC; }
.block-container { padding-top: 0.5rem; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #F7F8FA; border-radius: 10px; padding: 3px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-weight: 600; }
.stTabs [aria-selected="true"] { background: #00838A !important; color: white !important; }
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════
# LOGIN SCREEN
# ═══════════════════════════════════════
def login_screen():
    """ATU-branded login page."""
    # Center the login form
    col_l, col_m, col_r = st.columns([1, 1.2, 1])

    with col_m:
        st.markdown("")
        st.markdown("")

        # ATU brand bar
        st.markdown('<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);border-radius:4px;margin-bottom:24px;"></div>', unsafe_allow_html=True)

        # Logo and title
        st.markdown("""
        <div style="text-align:center; margin-bottom:32px;">
            <div style="width:60px;height:60px;background:#00838A;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:16px;">
                <span style="color:white;font-size:28px;font-weight:700;font-family:'Playfair Display',serif;">S</span>
            </div>
            <h1 style="font-family:'Playfair Display',serif;color:#1B2A4A;font-size:32px;margin:0;">SME Pulse</h1>
            <p style="color:#8896AB;font-size:14px;margin-top:4px;">Business Health Dashboard</p>
            <p style="color:#00838A;font-size:11px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;margin-top:8px;">ATLANTIC TECHNOLOGICAL UNIVERSITY · FUNTECH</p>
        </div>
        """, unsafe_allow_html=True)

        # Login form card
        st.markdown("""
        <div style="background:white;border:1px solid #E2E6EC;border-radius:16px;padding:32px;box-shadow:0 2px 8px rgba(27,42,74,0.06);">
            <h3 style="font-family:'Source Sans 3',sans-serif;color:#1B2A4A;font-size:18px;margin:0 0 4px;">Welcome back</h3>
            <p style="color:#8896AB;font-size:13px;margin:0 0 20px;">Sign in to access your dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        # Use Streamlit native inputs (these render reliably)
        email = st.text_input("Email", placeholder="Enter your email", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        st.markdown("")

        if st.button("Sign In", use_container_width=True, type="primary"):
            if email.lower() == "callum@smepulse.com" and password == "Irishrover":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid email or password. Please try again.")

        st.markdown("")
        st.markdown('<p style="text-align:center;color:#8896AB;font-size:11px;">Demo: Callum@SMEPulse.Com</p>', unsafe_allow_html=True)

        # Footer
        st.markdown("")
        st.markdown("")
        st.markdown('<p style="text-align:center;color:#8896AB;font-size:11px;">© 2026 SME Pulse · Callum Kidd · Atlantic Technological University</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════
# CHECK AUTH
# ═══════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop()


# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("### 📊 SME Pulse")
    st.caption("Data Management")
    st.divider()

    gc = get_gspread_client()
    sp = None
    connected = False

    if gc:
        sheet_name = st.text_input("Sheet Name", value="SME Pulse Data")
        sp = get_spreadsheet(gc, sheet_name)
        if sp:
            ensure_sheets(sp)
            connected = True
            st.success("✓ Connected to Google Sheets")
        else:
            st.warning(f'Sheet "{sheet_name}" not found. Create it and share with service account.')
    else:
        st.info("📋 Demo mode — no Google Sheets")

    st.divider()

    # Template download
    st.markdown("**📥 Template**")
    tpl = os.path.join(os.path.dirname(__file__), "SME_Pulse_Template.xlsx")
    if os.path.exists(tpl):
        with open(tpl, "rb") as f:
            st.download_button("⬇ Download Template", f, "SME_Pulse_Template.xlsx",
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             use_container_width=True)

    st.divider()

    # Upload
    st.markdown("**📤 Upload Data**")
    up = st.file_uploader("Upload template", type=["xlsx", "xls"])

    if up and connected:
        if st.button("📊 Upload to Sheets", use_container_width=True, type="primary"):
            with st.spinner("Uploading..."):
                res = upload_excel(sp, up)
                if res["success"]:
                    st.success(f"✓ {', '.join(res['success'])}")
                if res["errors"]:
                    st.error(f"✗ {', '.join(res['errors'])}")
                st.rerun()
    elif up and not connected:
        if st.button("📊 Use for session", use_container_width=True):
            try:
                xls = pd.ExcelFile(up)
                if "Monthly Financials" in xls.sheet_names:
                    st.session_state["l_fin"] = pd.read_excel(xls, "Monthly Financials", header=3)
                if "Cash Flow" in xls.sheet_names:
                    st.session_state["l_cf"] = pd.read_excel(xls, "Cash Flow", header=3)
                if "Targets" in xls.sheet_names:
                    st.session_state["l_tgt"] = pd.read_excel(xls, "Targets", header=3)
                if "Business Info" in xls.sheet_names:
                    di = pd.read_excel(xls, "Business Info", header=2)
                    st.session_state["l_info"] = {str(r.iloc[0]): str(r.iloc[1]) for _, r in di.iterrows() if str(r.iloc[0]) not in ("", "nan")}
                st.success("✓ Loaded")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    st.divider()
    view_mode = st.radio("View", ["Owner", "Board"])

    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    st.caption("SME Pulse · ATU · 2026")


# ═══════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════
if connected:
    fin = read_df(sp, "Monthly Financials")
    cf = read_df(sp, "Cash Flow")
    tgt = read_df(sp, "Targets")
    info = read_info(sp)
    src = "sheets"
elif "l_fin" in st.session_state:
    fin = st.session_state.get("l_fin", pd.DataFrame())
    cf = st.session_state.get("l_cf", pd.DataFrame())
    tgt = st.session_state.get("l_tgt", pd.DataFrame())
    info = st.session_state.get("l_info", {})
    src = "upload"
else:
    fin = pd.DataFrame()
    cf = pd.DataFrame()
    tgt = pd.DataFrame()
    info = {}
    src = "demo"

M = compute_metrics(fin, cf, tgt, info)


# ═══════════════════════════════════════
# HEADER
# ═══════════════════════════════════════
# Brand bar
st.markdown('<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);margin:-0.5rem -1rem 0 -1rem;border-radius:0;"></div>', unsafe_allow_html=True)

h1, h2 = st.columns([7, 3])
with h1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:12px 0;">
        <div style="width:36px;height:36px;background:#00838A;border-radius:8px;display:flex;align-items:center;justify-content:center;">
            <span style="color:white;font-size:17px;font-weight:700;font-family:'Playfair Display',serif;">S</span>
        </div>
        <div>
            <span style="font-size:18px;font-weight:700;color:#1B2A4A;font-family:'Playfair Display',serif;">SME Pulse</span>
            <span style="font-size:10px;color:#00838A;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-left:8px;">ATU FunTech</span>
            <div style="font-size:10px;color:#8896AB;">Business Health Dashboard</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    labels = {"sheets": ("● Live · Google Sheets", ATU["green"]), "upload": ("● Session data", ATU["amber"]), "demo": ("● Demo data", ATU["muted"])}
    lbl, clr = labels[src]
    st.markdown(f'<div style="text-align:right;padding-top:16px;"><span style="color:{clr};font-weight:600;font-size:12px;">{lbl}</span></div>', unsafe_allow_html=True)

st.divider()

# Welcome
st.markdown(f"""
<h1 style="font-family:'Playfair Display',serif;color:#1B2A4A;font-size:24px;margin:0;">Good morning, {M['owner']}</h1>
<p style="color:#4A5568;font-size:13px;margin-top:4px;">{"Board summary" if view_mode == "Board" else "Operational overview"} · {M['latest_month']}</p>
""", unsafe_allow_html=True)

st.markdown("")


# ═══════════════════════════════════════
# DASHBOARD TABS
# ═══════════════════════════════════════
tab_ov, tab_cf, tab_rv, tab_al, tab_dt = st.tabs(["◉ Overview", "◈ Cash Flow", "◆ Revenue", "△ Alerts", "⚙ Data"])


# ═══ OVERVIEW TAB ═══
with tab_ov:

    # Health + Runway + Alerts row
    c1, c2, c3 = st.columns([1, 1, 2.5])

    with c1:
        hs = M["health_score"]
        hc = ATU["green"] if hs >= 70 else ATU["amber"] if hs >= 50 else ATU["red"]
        hl = "Healthy" if hs >= 70 else "Caution" if hs >= 50 else "At Risk"

        st.markdown(f"##### 🏥 Health Score")
        fig = go.Figure(go.Indicator(mode="gauge+number", value=hs,
            number={"font": {"size": 48, "color": hc}},
            gauge={"axis": {"range": [0, 100], "visible": False},
                   "bar": {"color": hc, "thickness": 0.8},
                   "bgcolor": "#EEF0F4", "borderwidth": 0}))
        fig.update_layout(height=180, margin=dict(l=20, r=20, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        if hs >= 70:
            st.success(f"● {hl}")
        elif hs >= 50:
            st.warning(f"● {hl}")
        else:
            st.error(f"● {hl}")

    with c2:
        rw = M["runway_months"]
        st.markdown("##### 💰 Cash Runway")
        st.markdown("")
        rc = ATU["green"] if rw >= 12 else ATU["amber"] if rw >= 6 else ATU["red"]
        st.markdown(f'<div style="text-align:center;padding:20px 0;"><div style="font-size:48px;font-weight:700;color:{rc};">{rw}</div><div style="font-size:13px;color:#4A5568;">months remaining</div></div>', unsafe_allow_html=True)
        if rw >= 12:
            st.success("● On Track — Target: 12+ months")
        elif rw >= 6:
            st.warning("● Watch — Target: 12+ months")
        else:
            st.error("● At Risk — Target: 12+ months")

        # Small sparkline
        fig_rw = go.Figure(go.Scatter(y=[14, 13, 12, 11, 10.5, 9.8, 9.2, 8.6, rw],
            mode="lines", line=dict(color=rc, width=2, shape="spline"),
            fill="tozeroy", fillcolor=f"{rc}18"))
        fig_rw.update_layout(height=50, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.plotly_chart(fig_rw, use_container_width=True, config={"displayModeBar": False})

    with c3:
        st.markdown("##### ⚠ Deviation Alerts")
        if M["expenses_change"] > 10:
            st.error(f"Costs up {M['expenses_change']:.0f}% vs last month — review spending")
        if M["runway_months"] < 12:
            st.warning(f"Runway at {M['runway_months']} months — below 12-month target")
        if M["revenue_change"] > 0:
            st.info(f"Revenue trending +{M['revenue_change']:.1f}% above last month")
        if M["margin"] < 20:
            st.warning(f"Profit margin at {M['margin']:.1f}% — consider cost review")
        if M["revenue_change"] < -5:
            st.error(f"Revenue declined {abs(M['revenue_change']):.1f}% — investigate")

    st.divider()

    # KPI Cards
    st.markdown("##### Key Performance Indicators")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("💰 Cash Balance", f"€{M['cash_balance']:,.0f}", "Available now")
        fig = go.Figure(go.Scatter(y=M["rev_hist"], mode="lines", line=dict(color=ATU["teal"], width=2, shape="spline"), fill="tozeroy", fillcolor=f"{ATU['teal']}14"))
        fig.update_layout(height=50, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with k2:
        delta = f"{'+' if M['revenue_change']>=0 else ''}{M['revenue_change']:.1f}% vs prev"
        st.metric("📈 Monthly Revenue", f"€{M['revenue']:,.0f}", delta)
        fig = go.Figure(go.Scatter(y=M["rev_hist"], mode="lines", line=dict(color=ATU["green"], width=2, shape="spline"), fill="tozeroy", fillcolor=f"{ATU['green']}14"))
        fig.update_layout(height=50, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with k3:
        st.metric("📊 Total Expenses", f"€{M['expenses']:,.0f}", f"+{M['expenses_change']:.1f}% vs prev", delta_color="inverse")
        fig = go.Figure(go.Scatter(y=M["exp_hist"], mode="lines", line=dict(color=ATU["red"], width=2, shape="spline"), fill="tozeroy", fillcolor=f"{ATU['red']}14"))
        fig.update_layout(height=50, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with k4:
        st.metric("✦ Net Profit", f"€{M['profit']:,.0f}", f"{M['margin']:.1f}% margin")
        profit_hist = [r - e for r, e in zip(M["rev_hist"], M["exp_hist"])]
        fig = go.Figure(go.Scatter(y=profit_hist, mode="lines", line=dict(color=ATU["navy"], width=2, shape="spline"), fill="tozeroy", fillcolor=f"{ATU['navy']}14"))
        fig.update_layout(height=50, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Milestones
    st.markdown("##### Operational Milestones")

    milestones = [
        ("Revenue Target", f"€{M['revenue']:,.0f}", "€43,000", M["revenue"] >= 43000),
        ("Gross Margin", f"{M['margin']:.1f}%", "28%", M["margin"] >= 28),
        ("Cash Runway", f"{M['runway_months']} mo", ">12 mo", M["runway_months"] >= 12),
        ("Expenses Change", f"{M['expenses_change']:+.1f}%", "<5%", M["expenses_change"] < 5),
    ]

    for label, actual, target, on_track in milestones:
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 1.5])
        with col_a:
            st.markdown(f"**{label}**")
        with col_b:
            st.markdown(f"`{actual}`")
        with col_c:
            st.caption(f"Target: {target}")
        with col_d:
            if on_track:
                st.success("On Track")
            else:
                st.warning("Watch")

    st.divider()

    # Charts
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("##### Revenue Trends")
        rv = [v / 1000 for v in M["rev_hist"]]
        fig = go.Figure(go.Bar(x=M["month_labels"], y=rv, marker_color=ATU["green"],
            text=[f"€{v:.0f}K" for v in rv], textposition="outside",
            textfont=dict(size=10, color=ATU["mid"])))
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=30),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(tickfont=dict(size=11)), yaxis=dict(visible=False),
            showlegend=False, bargap=0.35)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        st.markdown("##### Cost Breakdown")
        fig = go.Figure(go.Pie(
            labels=["Staff", "Rent", "Suppliers", "Other"],
            values=[M["staff_pct"], M["rent_pct"], M["supplier_pct"], M["other_pct"]],
            hole=0.6, marker=dict(colors=[ATU["teal"], ATU["green"], ATU["navy"], ATU["muted"]],
            line=dict(color="white", width=2)),
            textinfo="label+percent", textfont=dict(size=12)))
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ═══ CASH FLOW TAB ═══
with tab_cf:
    st.markdown("##### Cash Flow Timeline")

    if not cf.empty:
        for _, row in cf.iterrows():
            ft = str(row.get("Type", "")).strip().lower()
            is_in = ft == "in"
            amt = float(row.get("Amount", 0)) if pd.notna(row.get("Amount")) else 0

            c_a, c_b, c_c = st.columns([0.5, 6, 2])
            with c_a:
                st.markdown(f"{'🟢' if is_in else '🔴'}")
            with c_b:
                st.markdown(f"**{row.get('Description', '')}**")
                st.caption(str(row.get("Date", "")))
            with c_c:
                if is_in:
                    st.markdown(f'<span style="color:#4CA771;font-weight:600;font-size:15px;">+€{amt:,.0f}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span style="color:#D94040;font-weight:600;font-size:15px;">-€{amt:,.0f}</span>', unsafe_allow_html=True)
            st.divider()
    else:
        st.info("No cash flow data. Upload your template to see entries.")


# ═══ REVENUE TAB ═══
with tab_rv:
    st.markdown("##### Revenue vs Expenses Over Time")

    if len(M["rev_hist"]) > 1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=M["month_labels"], y=[v/1000 for v in M["rev_hist"]],
            mode="lines+markers", name="Revenue", line=dict(color=ATU["green"], width=3), marker=dict(size=8),
            fill="tozeroy", fillcolor="rgba(76,167,113,0.1)"))
        fig.add_trace(go.Scatter(x=M["month_labels"], y=[v/1000 for v in M["exp_hist"]],
            mode="lines+markers", name="Expenses", line=dict(color=ATU["red"], width=3), marker=dict(size=8)))
        fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            yaxis=dict(gridcolor="#EEF0F4", tickprefix="€", ticksuffix="K"),
            margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Upload at least 2 months of data to see trends.")


# ═══ ALERTS TAB ═══
with tab_al:
    st.markdown("##### All Active Alerts")
    count = 0
    if M["expenses_change"] > 10:
        st.error(f"**Critical:** Operating costs up {M['expenses_change']:.0f}% this month"); count += 1
    if M["runway_months"] < 6:
        st.error(f"**Critical:** Cash runway at {M['runway_months']} months — action needed"); count += 1
    if M["runway_months"] < 12:
        st.warning(f"**Warning:** Cash runway below 12-month target"); count += 1
    if M["margin"] < 20:
        st.warning(f"**Warning:** Profit margin at {M['margin']:.1f}%"); count += 1
    if M["revenue_change"] > 5:
        st.info(f"**Positive:** Revenue up {M['revenue_change']:.1f}% — strong growth"); count += 1
    if M["revenue_change"] < -5:
        st.error(f"**Critical:** Revenue declined {abs(M['revenue_change']):.1f}%"); count += 1
    if count == 0:
        st.success("All metrics within target ranges ✓")


# ═══ DATA TAB ═══
with tab_dt:
    st.markdown("##### Your Data")
    if src == "demo":
        st.info("📋 **Demo Mode** — Upload data via sidebar to see your real metrics.")
    elif src == "sheets":
        st.success("✓ **Live** — Showing data from Google Sheets.")
    else:
        st.warning("📁 **Session only** — Connect Google Sheets for persistence.")

    if not fin.empty:
        st.markdown("**Monthly Financials**")
        st.dataframe(fin, use_container_width=True, hide_index=True)
    if not cf.empty:
        st.markdown("**Cash Flow**")
        st.dataframe(cf, use_container_width=True, hide_index=True)
    if info:
        st.markdown("**Business Profile**")
        for k, v in info.items():
            st.markdown(f"- **{k}:** {v}")


# ═══ FOOTER ═══
st.divider()
f1, f2 = st.columns(2)
with f1:
    st.caption("**SME Pulse** · A FunTech Project · Atlantic Technological University")
with f2:
    st.markdown('<p style="text-align:right;font-size:12px;color:#8896AB;">Callum Kidd · 2026</p>', unsafe_allow_html=True)
