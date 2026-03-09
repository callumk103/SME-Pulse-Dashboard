import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from sheets_backend import (
    get_gc, get_sp, ensure, read_df, read_info, upload_excel, quick_entry,
    compute, sample, get_features, get_bench,
    get_weather, get_ecb_rate, get_inflation, get_exchange, get_trends
)

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
T = {"teal":"#00838A","green":"#4CA771","navy":"#1B2A4A","red":"#D94040","amber":"#D4930D","mid":"#4A5568","muted":"#8896AB"}
st.set_page_config(page_title="SME Pulse", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

if "dark" not in st.session_state: st.session_state["dark"] = False
dk = st.session_state["dark"]
bg = "#0B0F1A" if dk else "#F7F8FA"
txt = "#F1F5F9" if dk else "#1B2A4A"
mut = "#94A3B8" if dk else "#8896AB"
bdr = "#1E293B" if dk else "#E2E6EC"
cbg = "#111827" if dk else "#FFFFFF"
gbg = "#1E293B" if dk else "#EEF0F4"

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp{{background:{bg};}}
[data-testid="stHeader"]{{display:none;}}
[data-testid="stSidebar"]{{background:{cbg};border-right:1px solid {bdr};}}
.stTabs [data-baseweb="tab-list"]{{gap:4px;background:{bg};border-radius:10px;padding:3px;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;font-weight:600;}}
.stTabs [aria-selected="true"]{{background:#00838A !important;color:white !important;}}
div[data-testid="stMetricValue"]{{color:{txt};}}
</style>""", unsafe_allow_html=True)

# ═══ SPARKLINE HELPER ═══
def spark(data, color, h=50):
    fig=go.Figure(go.Scatter(y=data,mode="lines",line=dict(color=color,width=2,shape="spline"),fill="tozeroy",fillcolor=f"{color}14"))
    fig.update_layout(height=h,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(visible=False),yaxis=dict(visible=False),showlegend=False)
    return fig

# ═══ LOGIN ═══
def login():
    _,col,_=st.columns([1,1.2,1])
    with col:
        st.markdown("")
        st.markdown(f'<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);border-radius:4px;margin-bottom:24px;"></div>',unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align:center;margin-bottom:28px;">
            <div style="width:60px;height:60px;background:#00838A;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:14px;">
                <span style="color:white;font-size:28px;font-weight:700;font-family:'Playfair Display',serif;">S</span></div>
            <h1 style="font-family:'Playfair Display',serif;color:{txt};font-size:32px;margin:0;">SME Pulse</h1>
            <p style="color:{mut};font-size:14px;margin-top:4px;">Business Health Dashboard</p>
            <p style="color:#00838A;font-size:11px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;margin-top:8px;">ATLANTIC TECHNOLOGICAL UNIVERSITY</p>
        </div>""",unsafe_allow_html=True)
        email=st.text_input("Email",placeholder="Enter your email")
        pw=st.text_input("Password",type="password",placeholder="Enter your password")
        st.markdown("")
        if st.button("Sign In",use_container_width=True,type="primary"):
            if email.lower()=="callum@smepulse.com" and pw=="Irishrover":
                st.session_state["auth"]=True;st.rerun()
            else: st.error("Invalid credentials")
        st.caption("Demo: Callum@SMEPulse.Com / Irishrover")

if "auth" not in st.session_state: st.session_state["auth"]=False
if not st.session_state["auth"]: login(); st.stop()

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("### 📊 SME Pulse")
    st.divider()
    gc=get_gc(); sp=None; connected=False
    if gc:
        sn=st.text_input("Sheet Name",value="SME Pulse Data")
        sp=get_sp(gc,sn)
        if sp: ensure(sp);connected=True;st.success("✓ Connected")
        else: st.warning(f'Sheet "{sn}" not found')
    else: st.info("📋 Demo mode")
    st.divider()
    tpl=os.path.join(os.path.dirname(__file__),"SME_Pulse_Template.xlsx")
    if os.path.exists(tpl):
        with open(tpl,"rb") as f:
            st.download_button("⬇ Download Template",f,"SME_Pulse_Template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    up=st.file_uploader("Upload data",type=["xlsx","xls"])
    if up and connected:
        if st.button("📊 Upload",use_container_width=True,type="primary"):
            with st.spinner("Uploading..."):
                res=upload_excel(sp,up)
                if res["success"]: st.success(f"✓ {', '.join(res['success'])}")
                if res["errors"]: st.error(f"✗ {', '.join(res['errors'])}")
                st.rerun()
    elif up:
        if st.button("📊 Use for session",use_container_width=True):
            try:
                xls=pd.ExcelFile(up)
                if "Monthly Financials" in xls.sheet_names: st.session_state["l_fin"]=pd.read_excel(xls,"Monthly Financials",header=3)
                if "Cash Flow" in xls.sheet_names: st.session_state["l_cf"]=pd.read_excel(xls,"Cash Flow",header=3)
                if "Business Info" in xls.sheet_names:
                    di=pd.read_excel(xls,"Business Info",header=2)
                    st.session_state["l_info"]={str(r.iloc[0]):str(r.iloc[1]) for _,r in di.iterrows() if str(r.iloc[0]) not in ("","nan")}
                st.success("✓");st.rerun()
            except Exception as e: st.error(str(e))
    st.divider()
    with st.expander("⚡ Quick Entry"):
        qm=st.selectbox("Month",["January","February","March","April","May","June","July","August","September","October","November","December"])
        qy=st.number_input("Year",value=2026,min_value=2020,max_value=2030)
        qr=st.number_input("Revenue €",value=0,min_value=0,step=500)
        qe=st.number_input("Expenses €",value=0,min_value=0,step=500)
        qs=st.number_input("Staff €",value=0,min_value=0,step=500)
        qn=st.number_input("Rent €",value=0,min_value=0,step=100)
        qu=st.number_input("Suppliers €",value=0,min_value=0,step=500)
        qo=st.number_input("Other €",value=0,min_value=0,step=100)
        if st.button("💾 Save",use_container_width=True):
            if connected and qr>0:
                if quick_entry(sp,qm,qy,qr,qe,qs,qn,qu,qo): st.success("✓");st.rerun()
            elif not connected: st.warning("Connect Sheets first")
    st.divider()
    view=st.radio("View",["Owner","Board"])
    if st.toggle("🌙 Dark Mode",value=dk): st.session_state["dark"]=True;st.rerun()
    elif dk: st.session_state["dark"]=False;st.rerun()
    st.divider()
    if st.button("🚪 Sign Out",use_container_width=True): st.session_state["auth"]=False;st.rerun()

# ═══ LOAD DATA ═══
if connected:
    fin=read_df(sp,"Monthly Financials");cf=read_df(sp,"Cash Flow");tgt=read_df(sp,"Targets");info=read_info(sp);src="sheets"
elif "l_fin" in st.session_state:
    fin=st.session_state.get("l_fin",pd.DataFrame());cf=st.session_state.get("l_cf",pd.DataFrame());tgt=pd.DataFrame();info=st.session_state.get("l_info",{});src="upload"
else:
    fin=pd.DataFrame();cf=pd.DataFrame();tgt=pd.DataFrame();info={};src="demo"

M=compute(fin,cf,tgt,info)
feat=get_features(M["industry"])
bench=get_bench(M["industry"])

# ═══ HEADER ═══
st.markdown(f'<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);margin:-0.5rem -1rem 0 -1rem;"></div>',unsafe_allow_html=True)
h1,h2=st.columns([7,3])
with h1:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:12px 0;">
        <div style="width:36px;height:36px;background:#00838A;border-radius:8px;display:flex;align-items:center;justify-content:center;">
            <span style="color:white;font-size:17px;font-weight:700;font-family:'Playfair Display',serif;">S</span></div>
        <div><span style="font-size:18px;font-weight:700;color:{txt};font-family:'Playfair Display',serif;">SME Pulse</span>
            <span style="font-size:10px;color:#00838A;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-left:8px;">ATU FunTech</span>
            <div style="font-size:10px;color:{mut};">Business Health Dashboard \u00B7 {M['industry']}</div></div></div>""",unsafe_allow_html=True)
with h2:
    lb={"sheets":("● Live","#4CA771"),"upload":("● Session","#D4930D"),"demo":("● Demo","#8896AB")}
    l,c=lb[src]
    st.markdown(f'<div style="text-align:right;padding-top:16px;"><span style="color:{c};font-weight:600;font-size:12px;">{l}</span></div>',unsafe_allow_html=True)
st.divider()
st.markdown(f'<h1 style="font-family:\'Playfair Display\',serif;color:{txt};font-size:24px;margin:0;">Good morning, {M["owner"]}</h1><p style="color:{mut};font-size:13px;margin-top:4px;">{"Board summary" if view=="Board" else "Operational overview"} \u00B7 {M["latest"]}</p>',unsafe_allow_html=True)
st.markdown("")

# ═══ TABS ═══
tab_names = ["◉ Overview","◈ Cash Flow","◆ Revenue","△ Alerts","🌍 Context","📊 Compare","⚙ Data"]
tabs=st.tabs(tab_names)

# ════════════ OVERVIEW ════════════
with tabs[0]:
    c1,c2,c3=st.columns([1,1,2.5])
    with c1:
        hs=M["health"];hc=T["green"] if hs>=70 else T["amber"] if hs>=50 else T["red"]
        st.markdown("##### 🏥 Health Score")
        fig=go.Figure(go.Indicator(mode="gauge+number",value=hs,number={"font":{"size":48,"color":hc}},
            gauge={"axis":{"range":[0,100],"visible":False},"bar":{"color":hc,"thickness":0.8},"bgcolor":gbg,"borderwidth":0}))
        fig.update_layout(height=180,margin=dict(l=20,r=20,t=30,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        (st.success if hs>=70 else st.warning if hs>=50 else st.error)(f"● {'Healthy' if hs>=70 else 'Caution' if hs>=50 else 'At Risk'}")
        st.caption(f"Industry avg margin: {bench['avg_margin']}% | Yours: {M['margin']:.1f}%")

    with c2:
        rw=M["runway"];rc=T["green"] if rw>=12 else T["amber"] if rw>=6 else T["red"]
        st.markdown("##### 💰 Cash Runway")
        st.markdown(f'<div style="text-align:center;padding:20px 0;"><div style="font-size:48px;font-weight:700;color:{rc};">{rw}</div><div style="font-size:13px;color:{mut};">months remaining</div></div>',unsafe_allow_html=True)
        (st.success if rw>=12 else st.warning if rw>=6 else st.error)(f"● {'On Track' if rw>=12 else 'Watch' if rw>=6 else 'At Risk'}")
        st.plotly_chart(spark(M["forecast"],rc,60),use_container_width=True,config={"displayModeBar":False})
        st.caption("4-week cash forecast")

    with c3:
        st.markdown("##### ⚠ Deviation Alerts")
        if M["exp_chg"]>10: st.error(f"Costs up {M['exp_chg']:.0f}% vs last month")
        if M["runway"]<12: st.warning(f"Runway {M['runway']} months, below 12mo target")
        if M["rev_chg"]>0: st.info(f"Revenue +{M['rev_chg']:.1f}% above last month")
        if M["margin"]<bench["avg_margin"]: st.warning(f"Margin {M['margin']:.1f}% below industry avg {bench['avg_margin']}%")
        if M["staff_pct"]>bench["avg_staff_pct"]+5: st.warning(f"Staff costs {M['staff_pct']}% above industry avg {bench['avg_staff_pct']}%")
        if M["rev_chg"]<-5: st.error(f"Revenue declined {abs(M['rev_chg']):.1f}%")

    st.divider()
    st.markdown("##### Key Performance Indicators")
    k1,k2,k3,k4=st.columns(4)
    with k1:
        st.metric("💰 Cash",f"€{M['cash']:,.0f}","Balance")
        st.plotly_chart(spark(M["rev_hist"],T["teal"]),use_container_width=True,config={"displayModeBar":False})
    with k2:
        st.metric("📈 Revenue",f"€{M['revenue']:,.0f}",f"{'+' if M['rev_chg']>=0 else ''}{M['rev_chg']:.1f}%")
        st.plotly_chart(spark(M["rev_hist"],T["green"]),use_container_width=True,config={"displayModeBar":False})
    with k3:
        st.metric("📊 Expenses",f"€{M['expenses']:,.0f}",f"+{M['exp_chg']:.1f}%",delta_color="inverse")
        st.plotly_chart(spark(M["exp_hist"],T["red"]),use_container_width=True,config={"displayModeBar":False})
    with k4:
        st.metric("✦ Profit",f"€{M['profit']:,.0f}",f"{M['margin']:.1f}%")
        st.plotly_chart(spark([r-e for r,e in zip(M["rev_hist"],M["exp_hist"])],T["navy"]),use_container_width=True,config={"displayModeBar":False})

    st.divider()
    st.markdown("##### Milestones vs Targets")
    for label,actual,target,ok in [
        ("Revenue",f"€{M['revenue']:,.0f}","€43,000",M["revenue"]>=43000),
        ("Margin",f"{M['margin']:.1f}%",f"{bench['avg_margin']}% (ind.)",M["margin"]>=bench["avg_margin"]),
        ("Runway",f"{M['runway']} mo",">12 mo",M["runway"]>=12),
        ("Staff %",f"{M['staff_pct']}%",f"<{bench['avg_staff_pct']}% (ind.)",M["staff_pct"]<=bench["avg_staff_pct"]),
    ]:
        a,b2,cc,d=st.columns([3,2,2,1.5])
        with a: st.markdown(f"**{label}**")
        with b2: st.markdown(f"`{actual}`")
        with cc: st.caption(f"Target: {target}")
        with d: st.success("✓") if ok else st.warning("!")

    st.divider()
    ch1,ch2=st.columns(2)
    with ch1:
        st.markdown("##### Revenue Trends")
        rv=[v/1000 for v in M["rev_hist"]]
        fig=go.Figure(go.Bar(x=M["labels"],y=rv,marker_color=T["green"],text=[f"€{v:.0f}K" for v in rv],textposition="outside",textfont=dict(size=10,color=mut)))
        fig.update_layout(height=280,margin=dict(l=0,r=0,t=10,b=30),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(tickfont=dict(size=11,color=mut)),yaxis=dict(visible=False),showlegend=False,bargap=0.35)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with ch2:
        st.markdown("##### Cost Breakdown")
        fig=go.Figure(go.Pie(labels=["Staff","Rent","Suppliers","Other"],values=[M["staff_pct"],M["rent_pct"],M["sup_pct"],M["oth_pct"]],hole=0.6,
            marker=dict(colors=[T["teal"],T["green"],T["navy"],T["muted"]],line=dict(color=bg,width=2)),textinfo="label+percent",textfont=dict(size=12)))
        fig.update_layout(height=280,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ════════════ CASH FLOW ════════════
with tabs[1]:
    st.markdown("##### Cash Flow Timeline")
    if not cf.empty:
        for _,row in cf.iterrows():
            ft=str(row.get("Type","")).strip().lower();ii=ft=="in"
            amt=float(row.get("Amount",0)) if pd.notna(row.get("Amount")) else 0
            a,b2,cc=st.columns([0.5,6,2])
            with a: st.markdown("🟢" if ii else "🔴")
            with b2: st.markdown(f"**{row.get('Description','')}**"); st.caption(str(row.get("Date","")))
            with cc: st.markdown(f'<span style="color:{T["green"] if ii else T["red"]};font-weight:600;font-size:15px;">{"+" if ii else "-"}€{amt:,.0f}</span>',unsafe_allow_html=True)
            st.divider()
    else: st.info("No cash flow data. Upload your template.")

    # Forecast chart
    st.markdown("##### 4-Week Cash Forecast")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=["Week 1","Week 2","Week 3","Week 4"],y=M["forecast"],mode="lines+markers",line=dict(color=T["teal"],width=3),marker=dict(size=10),fill="tozeroy",fillcolor=f"{T['teal']}18"))
    fig.add_hline(y=5000,line_dash="dash",line_color=T["red"],annotation_text="Safety threshold €5K")
    fig.update_layout(height=250,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(gridcolor=bdr,tickprefix="€"),margin=dict(l=20,r=20,t=10,b=30))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ════════════ REVENUE ════════════
with tabs[2]:
    st.markdown("##### Revenue vs Expenses")
    if len(M["rev_hist"])>1:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=M["labels"],y=[v/1000 for v in M["rev_hist"]],mode="lines+markers",name="Revenue",line=dict(color=T["green"],width=3),marker=dict(size=8),fill="tozeroy",fillcolor="rgba(76,167,113,0.1)"))
        fig.add_trace(go.Scatter(x=M["labels"],y=[v/1000 for v in M["exp_hist"]],mode="lines+markers",name="Expenses",line=dict(color=T["red"],width=3),marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=M["labels"],y=[(r-e)/1000 for r,e in zip(M["rev_hist"],M["exp_hist"])],mode="lines+markers",name="Profit",line=dict(color=T["navy"],width=2,dash="dot"),marker=dict(size=6)))
        fig.update_layout(height=400,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5),yaxis=dict(gridcolor=bdr,tickprefix="€",ticksuffix="K"),margin=dict(l=20,r=20,t=20,b=40))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("Need 2+ months of data for trends.")

# ════════════ ALERTS ════════════
with tabs[3]:
    st.markdown("##### All Active Alerts")
    ct=0
    if M["exp_chg"]>10: st.error(f"**Critical:** Costs up {M['exp_chg']:.0f}%");ct+=1
    if M["runway"]<6: st.error(f"**Critical:** Runway {M['runway']} months");ct+=1
    if M["runway"]<12: st.warning(f"**Warning:** Runway below target");ct+=1
    if M["margin"]<bench["avg_margin"]: st.warning(f"**Warning:** Margin {M['margin']:.1f}% below industry avg {bench['avg_margin']}%");ct+=1
    if M["staff_pct"]>bench["avg_staff_pct"]+5: st.warning(f"**Warning:** Staff costs above industry avg");ct+=1
    if M["rev_chg"]>5: st.info(f"**Positive:** Revenue up {M['rev_chg']:.1f}%");ct+=1
    if M["rev_chg"]<-5: st.error(f"**Critical:** Revenue down {abs(M['rev_chg']):.1f}%");ct+=1
    if ct==0: st.success("All metrics within target ✓")

# ════════════ MARKET CONTEXT (industry-aware) ════════════
with tabs[4]:
    st.markdown("##### Business Context")
    st.caption(f"Showing features relevant to: **{M['industry']}**")
    st.markdown("")

    # ECB & Inflation (always shown)
    ec1,ec2=st.columns(2)
    with ec1:
        st.markdown("##### 🏦 Economic Climate")
        rate=get_ecb_rate()
        infl=get_inflation()
        if rate is not None: st.metric("ECB Interest Rate",f"{rate}%")
        else: st.metric("ECB Interest Rate","N/A","API key needed")
        if infl is not None:
            st.metric("Irish Inflation (HICP)",f"{infl}%")
            if infl>3: st.warning(f"Inflation at {infl}% may push up supplier costs and wage expectations.")
            else: st.info(f"Inflation at {infl}% is moderate.")
        else: st.metric("Irish Inflation","N/A")

    with ec2:
        # Exchange rates (conditional)
        if feat["exchange"]:
            st.markdown("##### 💱 Exchange Rates")
            fx=get_exchange()
            if fx:
                st.metric("EUR/GBP",f"{fx['EUR_GBP']}")
                st.metric("EUR/USD",f"{fx['EUR_USD']}")
                st.caption("Relevant for imported goods and international customers.")
            else: st.info("Add exchange_api_key to secrets for live rates.")
        # Unit economics (conditional)
        elif feat["unit_econ"]:
            st.markdown("##### 📐 Unit Economics")
            cac=M["expenses"]*0.15  # estimate
            ltv=M["revenue"]*12  # estimate
            ratio=round(ltv/cac,1) if cac>0 else 0
            st.metric("Est. Customer Acq. Cost",f"€{cac:,.0f}","~15% of expenses")
            st.metric("Est. Lifetime Value (12mo)",f"€{ltv:,.0f}")
            st.metric("LTV:CAC Ratio",f"{ratio}:1","Target: >3:1")
            if ratio<3: st.warning("LTV:CAC ratio below 3:1. Consider reducing acquisition costs or increasing retention.")
            else: st.success("Healthy LTV:CAC ratio.")

    st.divider()

    # Weather (conditional)
    if feat["weather"]:
        st.markdown(f"##### 🌤 7-Day Forecast for {M['location']}")
        weather=get_weather(M["location"])
        if weather:
            cols=st.columns(min(7,len(weather)))
            for i,(date,w) in enumerate(weather[:7]):
                with cols[i]:
                    st.markdown(f"**{date[5:]}**")
                    st.markdown(f"🌡 {w['temp']}°C")
                    st.caption(w['desc'])
                    if w['rain']>0: st.caption(f"🌧 {w['rain']}mm")
        else: st.info("Add openweather_api_key to secrets for weather data.")
        st.divider()

    # Google Trends (conditional)
    if feat["trends"]:
        st.markdown(f"##### 📈 Search Interest: {M['industry']} in {M['location']}")
        keyword=f"{M['industry'].lower()} {M['location'].lower()}"
        trends=get_trends(keyword)
        if trends:
            fig=go.Figure(go.Scatter(y=trends,mode="lines",line=dict(color=T["teal"],width=2),fill="tozeroy",fillcolor=f"{T['teal']}18"))
            fig.update_layout(height=150,margin=dict(l=0,r=0,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(visible=False),xaxis=dict(visible=False))
            st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            if len(trends)>=2:
                chg=((trends[-1]-trends[-6])/trends[-6]*100) if trends[-6]>0 else 0
                if chg>10: st.info(f"Search interest up {chg:.0f}% over 6 months. Growing demand in your area.")
                elif chg<-10: st.warning(f"Search interest down {abs(chg):.0f}%. Monitor local competition.")
        else: st.caption("Trends data not available. pytrends may need time to load.")

    # Network metrics (conditional - for tech/platform businesses like John's)
    if feat["network"]:
        st.markdown("##### 🔗 Network Growth")
        st.caption("For platform businesses, network size drives value.")
        n1,n2,n3=st.columns(3)
        with n1: st.metric("Active Customers",M.get("employees","15"),"Est. from profile")
        with n2: st.metric("Platform Health","Strong" if M["health"]>=70 else "Monitor","Based on health score")
        with n3: st.metric("5yr Survival Rate",f"{bench['survival_5yr']}%",f"{M['industry']} sector")

    # Industry benchmark summary
    st.divider()
    st.markdown("##### 📊 Industry Benchmarks (CSO Ireland)")
    b1,b2,b3,b4=st.columns(4)
    with b1: st.metric("Avg Margin",f"{bench['avg_margin']}%",f"Yours: {M['margin']:.1f}%")
    with b2: st.metric("Avg Staff %",f"{bench['avg_staff_pct']}%",f"Yours: {M['staff_pct']}%")
    with b3: st.metric("Avg Rent %",f"{bench['avg_rent_pct']}%",f"Yours: {M['rent_pct']}%")
    with b4: st.metric("5yr Survival",f"{bench['survival_5yr']}%",f"{M['industry']}")

# ════════════ COMPARE ════════════
with tabs[5]:
    st.markdown("##### Period Comparison")
    if len(M["labels"])>=2:
        c1,c2=st.columns(2)
        with c1: p1=st.selectbox("Period 1",M["labels"],index=max(0,len(M["labels"])-2))
        with c2: p2=st.selectbox("Period 2",M["labels"],index=len(M["labels"])-1)
        i1=M["labels"].index(p1);i2=M["labels"].index(p2)
        r1=M["rev_hist"][i1];r2=M["rev_hist"][i2]
        e1=M["exp_hist"][i1];e2=M["exp_hist"][i2]
        st.divider()
        m1,m2,m3=st.columns(3)
        with m1:
            st.metric("Revenue",f"€{r2:,.0f}",f"{((r2-r1)/r1*100):+.1f}%" if r1>0 else "N/A")
        with m2:
            st.metric("Expenses",f"€{e2:,.0f}",f"{((e2-e1)/e1*100):+.1f}%" if e1>0 else "N/A",delta_color="inverse")
        with m3:
            p1v=r1-e1;p2v=r2-e2
            st.metric("Profit",f"€{p2v:,.0f}",f"{((p2v-p1v)/abs(p1v)*100):+.1f}%" if p1v!=0 else "N/A")

        fig=go.Figure()
        fig.add_trace(go.Bar(name=p1,x=["Revenue","Expenses","Profit"],y=[r1/1000,e1/1000,(r1-e1)/1000],marker_color=T["muted"]))
        fig.add_trace(go.Bar(name=p2,x=["Revenue","Expenses","Profit"],y=[r2/1000,e2/1000,(r2-e2)/1000],marker_color=T["teal"]))
        fig.update_layout(height=300,barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(gridcolor=bdr,tickprefix="€",ticksuffix="K"),margin=dict(l=20,r=20,t=20,b=40))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("Need 2+ months for comparison.")

# ════════════ DATA ════════════
with tabs[6]:
    st.markdown("##### Your Data")
    if src=="demo": st.info("📋 Demo mode. Upload data via sidebar.")
    elif src=="sheets": st.success("✓ Live from Google Sheets.")
    else: st.warning("📁 Session only.")
    if not fin.empty: st.markdown("**Monthly Financials**");st.dataframe(fin,use_container_width=True,hide_index=True)
    if not cf.empty: st.markdown("**Cash Flow**");st.dataframe(cf,use_container_width=True,hide_index=True)
    if info: st.markdown("**Business Profile**")
    for k,v in info.items(): st.markdown(f"- **{k}:** {v}")

# ═══ FOOTER ═══
st.divider()
f1,f2=st.columns(2)
with f1: st.caption(f"**SME Pulse** \u00B7 FunTech \u00B7 Atlantic Technological University")
with f2: st.markdown(f'<p style="text-align:right;font-size:12px;color:{mut};">Callum Kidd \u00B7 2026</p>',unsafe_allow_html=True)
