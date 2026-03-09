import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="SME Pulse", page_icon="📊", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
.stApp{background:#F7F8FA;}
[data-testid="stHeader"]{display:none;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#F7F8FA;border-radius:10px;padding:3px;}
.stTabs [aria-selected="true"]{background:#00838A !important;color:white !important;}
</style>""", unsafe_allow_html=True)

T = {"teal":"#00838A","green":"#4CA771","navy":"#1B2A4A","red":"#D94040","amber":"#D4930D","mid":"#4A5568","muted":"#8896AB"}

# ═══ LOGIN ═══
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _,col,_ = st.columns([1,1.2,1])
    with col:
        st.markdown("")
        st.markdown('<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);border-radius:4px;margin-bottom:24px;"></div>', unsafe_allow_html=True)
        st.markdown("""<div style="text-align:center;margin-bottom:28px;">
            <div style="width:60px;height:60px;background:#00838A;border-radius:14px;display:inline-flex;align-items:center;justify-content:center;margin-bottom:14px;">
                <span style="color:white;font-size:28px;font-weight:700;font-family:'Playfair Display',serif;">S</span></div>
            <h1 style="font-family:'Playfair Display',serif;color:#1B2A4A;font-size:32px;margin:0;">SME Pulse</h1>
            <p style="color:#8896AB;font-size:14px;margin-top:4px;">Business Health Dashboard</p>
            <p style="color:#00838A;font-size:11px;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;margin-top:8px;">ATLANTIC TECHNOLOGICAL UNIVERSITY</p>
        </div>""", unsafe_allow_html=True)
        email = st.text_input("Email", placeholder="Enter your email")
        pw = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("")
        if st.button("Sign In", use_container_width=True, type="primary"):
            if email.lower() == "callum@smepulse.com" and pw == "Irishrover":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Invalid credentials")
        st.caption("Demo: Callum@SMEPulse.Com / Irishrover")
    st.stop()

# ═══ SAMPLE DATA ═══
M = {
    "revenue": 45200, "expenses": 31800, "profit": 13400, "margin": 29.6,
    "rev_chg": 8.2, "exp_chg": 12.0, "cash": 23450, "runway": 8.2,
    "staff_pct": 42, "rent_pct": 22, "sup_pct": 24, "oth_pct": 12,
    "rev_hist": [38000, 42000, 39000, 48000, 44000, 45200],
    "exp_hist": [30000, 33000, 31500, 36000, 34000, 31800],
    "labels": ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"],
    "forecast": [22100, 20800, 19500, 18200],
    "health": 74, "owner": "Liam", "latest": "February 2026",
    "industry": "Retail",
}

bench = {"avg_margin": 22.0, "avg_staff_pct": 38.0, "avg_rent_pct": 18.0}

# ═══ TRY GOOGLE SHEETS ═══
connected = False
sp = None
fin = pd.DataFrame()
cf = pd.DataFrame()
info = {}
src = "demo"

try:
    import gspread
    creds = st.secrets.get("gcp_service_account", None)
    if creds:
        gc = gspread.service_account_from_dict(dict(creds))
        sp = gc.open("SME Pulse Data")
        connected = True
        src = "sheets"
        # Read data
        d = sp.worksheet("Monthly Financials").get_all_records()
        if d:
            fin = pd.DataFrame(d)
        d2 = sp.worksheet("Cash Flow").get_all_records()
        if d2:
            cf = pd.DataFrame(d2)
        d3 = sp.worksheet("Business Info").get_all_records()
        if d3:
            info = {str(r.get("Field","")): str(r.get("Value","")) for r in d3 if str(r.get("Field","")).strip()}
except Exception as e:
    st.sidebar.warning(f"Sheets: {e}")

# Compute from real data if available
if not fin.empty:
    try:
        for c in ["Revenue","Expenses","Staff Costs","Rent","Supplier Costs","Other Costs","Year"]:
            if c in fin.columns:
                fin[c] = pd.to_numeric(fin[c].astype(str).str.replace(",","").str.replace("€",""), errors="coerce").fillna(0)
        fin = fin[fin["Month"].astype(str).str.strip() != ""]
        if not fin.empty:
            mo = {m:i for i,m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"])}
            fin["_s"] = fin["Month"].map(mo).fillna(99)
            fin = fin.sort_values(["Year","_s"]).drop(columns=["_s"])
            L = fin.iloc[-1]
            P = fin.iloc[-2] if len(fin) > 1 else L
            M["revenue"] = float(L.get("Revenue",0))
            M["expenses"] = float(L.get("Expenses",0))
            M["profit"] = M["revenue"] - M["expenses"]
            M["margin"] = (M["profit"]/M["revenue"]*100) if M["revenue"] > 0 else 0
            pr = float(P.get("Revenue",0))
            M["rev_chg"] = ((M["revenue"]-pr)/pr*100) if pr > 0 else 0
            pe = float(P.get("Expenses",0))
            M["exp_chg"] = ((M["expenses"]-pe)/pe*100) if pe > 0 else 0
            if M["expenses"] > 0:
                M["staff_pct"] = round(float(L.get("Staff Costs",0))/M["expenses"]*100,1)
                M["rent_pct"] = round(float(L.get("Rent",0))/M["expenses"]*100,1)
                M["sup_pct"] = round(float(L.get("Supplier Costs",0))/M["expenses"]*100,1)
                M["oth_pct"] = round(100-M["staff_pct"]-M["rent_pct"]-M["sup_pct"],1)
            M["rev_hist"] = fin["Revenue"].tolist()
            M["exp_hist"] = fin["Expenses"].tolist()
            M["labels"] = fin["Month"].tolist()
            M["latest"] = f"{L.get('Month','')} {int(L.get('Year',0))}"
            M["owner"] = info.get("Owner Name", "Liam")
            M["industry"] = info.get("Industry", "Retail")
            cs = info.get("Monthly Cash Balance (€)", info.get("Monthly Cash Balance","23450"))
            try: M["cash"] = float(str(cs).replace(",","").replace("€",""))
            except: pass
            burn = (M["expenses"]-M["revenue"]) if M["expenses"]>M["revenue"] else M["expenses"]*0.1
            M["runway"] = round(M["cash"]/burn,1) if burn > 0 else 99
            wb = M["expenses"]/4.33; wi = M["revenue"]/4.33
            M["forecast"] = []; bal = M["cash"]
            for w in range(4):
                bal = bal - wb + wi
                M["forecast"].append(round(bal))
            sc = 50
            if M["margin"]>25: sc+=15
            elif M["margin"]>15: sc+=10
            if M["rev_chg"]>0: sc+=10
            if M["runway"]>12: sc+=15
            elif M["runway"]>6: sc+=8
            if M["exp_chg"]<5: sc+=10
            M["health"] = min(sc,100)
    except Exception as e:
        st.sidebar.warning(f"Data: {e}")

# ═══ SIDEBAR ═══
with st.sidebar:
    st.markdown("### 📊 SME Pulse")
    st.divider()
    if connected:
        st.success("✓ Google Sheets connected")
    else:
        st.info("📋 Demo mode")

    # Upload
    import os
    tpl = os.path.join(os.path.dirname(__file__), "SME_Pulse_Template.xlsx")
    if os.path.exists(tpl):
        with open(tpl,"rb") as f:
            st.download_button("⬇ Template", f, "SME_Pulse_Template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

    up = st.file_uploader("Upload data", type=["xlsx","xls"])
    if up and connected:
        if st.button("📊 Upload", use_container_width=True, type="primary"):
            try:
                xls = pd.ExcelFile(up)
                for tab, h in {"Monthly Financials":["Month","Year","Revenue","Expenses","Staff Costs","Rent","Supplier Costs","Other Costs"],"Cash Flow":["Date","Description","Type","Amount","Category","Status"]}.items():
                    if tab in xls.sheet_names:
                        df = pd.read_excel(xls, tab, header=3)
                        df.columns = [str(c).split("(")[0].strip().replace("€","").strip() for c in df.columns]
                        df = df.dropna(subset=[df.columns[0]])
                        w = sp.worksheet(tab); w.clear(); w.append_row(h)
                        for _,r in df.iterrows(): w.append_row([str(r.get(hh,"")) for hh in h])
                if "Business Info" in xls.sheet_names:
                    df = pd.read_excel(xls,"Business Info",header=2)
                    if len(df.columns)>=2:
                        w = sp.worksheet("Business Info"); w.clear(); w.append_row(["Field","Value"])
                        for _,r in df.iterrows():
                            k=str(r.iloc[0]).strip()
                            if k and k!="nan": w.append_row([k,str(r.iloc[1]).strip()])
                st.success("✓ Uploaded"); st.rerun()
            except Exception as e:
                st.error(str(e))

    st.divider()
    view = st.radio("View", ["Owner", "Board"])
    st.divider()
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["auth"] = False; st.rerun()

# ═══ HEADER ═══
st.markdown('<div style="height:4px;background:linear-gradient(90deg,#00838A,#4CA771,#1B2A4A);margin:-0.5rem -1rem 0 -1rem;"></div>', unsafe_allow_html=True)
h1,h2 = st.columns([7,3])
with h1:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:12px 0;">
        <div style="width:36px;height:36px;background:#00838A;border-radius:8px;display:flex;align-items:center;justify-content:center;">
            <span style="color:white;font-size:17px;font-weight:700;font-family:'Playfair Display',serif;">S</span></div>
        <div><span style="font-size:18px;font-weight:700;color:#1B2A4A;font-family:'Playfair Display',serif;">SME Pulse</span>
            <span style="font-size:10px;color:#00838A;font-weight:600;text-transform:uppercase;letter-spacing:1.2px;margin-left:8px;">ATU FunTech</span>
            <div style="font-size:10px;color:#8896AB;">Business Health Dashboard · {M['industry']}</div></div></div>""", unsafe_allow_html=True)
with h2:
    c = T["green"] if src=="sheets" else T["muted"]
    l = "● Live" if src=="sheets" else "● Demo"
    st.markdown(f'<div style="text-align:right;padding-top:16px;"><span style="color:{c};font-weight:600;font-size:12px;">{l}</span></div>', unsafe_allow_html=True)

st.divider()
st.markdown(f'<h1 style="font-family:\'Playfair Display\',serif;color:#1B2A4A;font-size:24px;margin:0;">Good morning, {M["owner"]}</h1><p style="color:#8896AB;font-size:13px;margin-top:4px;">{"Board summary" if view=="Board" else "Operational overview"} · {M["latest"]}</p>', unsafe_allow_html=True)
st.markdown("")

# ═══ HELPER ═══
def spark(data, color, h=50):
    fig=go.Figure(go.Scatter(y=data,mode="lines",line=dict(color=color,width=2,shape="spline"),fill="tozeroy",fillcolor=f"{color}14"))
    fig.update_layout(height=h,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(visible=False),yaxis=dict(visible=False),showlegend=False)
    return fig

# ═══ TABS ═══
tabs = st.tabs(["◉ Overview","◈ Cash Flow","◆ Revenue","△ Alerts","🌍 Context","📊 Compare","⚙ Data"])

# ════ OVERVIEW ════
with tabs[0]:
    c1,c2,c3 = st.columns([1,1,2.5])
    with c1:
        hs=M["health"]; hc=T["green"] if hs>=70 else T["amber"] if hs>=50 else T["red"]
        st.markdown("##### 🏥 Health Score")
        fig=go.Figure(go.Indicator(mode="gauge+number",value=hs,number={"font":{"size":48,"color":hc}},gauge={"axis":{"range":[0,100],"visible":False},"bar":{"color":hc,"thickness":0.8},"bgcolor":"#EEF0F4","borderwidth":0}))
        fig.update_layout(height=180,margin=dict(l=20,r=20,t=30,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        (st.success if hs>=70 else st.warning if hs>=50 else st.error)(f"● {'Healthy' if hs>=70 else 'Caution' if hs>=50 else 'At Risk'}")
        st.caption(f"Industry avg margin: {bench['avg_margin']}% | Yours: {M['margin']:.1f}%")

    with c2:
        rw=M["runway"]; rc=T["green"] if rw>=12 else T["amber"] if rw>=6 else T["red"]
        st.markdown("##### 💰 Cash Runway")
        st.markdown(f'<div style="text-align:center;padding:20px 0;"><div style="font-size:48px;font-weight:700;color:{rc};">{rw}</div><div style="font-size:13px;color:#8896AB;">months remaining</div></div>',unsafe_allow_html=True)
        (st.success if rw>=12 else st.warning if rw>=6 else st.error)(f"● {'On Track' if rw>=12 else 'Watch' if rw>=6 else 'At Risk'}")
        st.plotly_chart(spark(M["forecast"],rc,60),use_container_width=True,config={"displayModeBar":False})
        st.caption("4-week cash forecast")

    with c3:
        st.markdown("##### ⚠ Alerts")
        if M["exp_chg"]>10: st.error(f"Costs up {M['exp_chg']:.0f}% vs last month")
        if M["runway"]<12: st.warning(f"Runway {M['runway']} months, below 12mo target")
        if M["rev_chg"]>0: st.info(f"Revenue +{M['rev_chg']:.1f}%")
        if M["margin"]<bench["avg_margin"]: st.warning(f"Margin {M['margin']:.1f}% below industry avg {bench['avg_margin']}%")

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
    for label,actual,target,ok in [("Revenue",f"€{M['revenue']:,.0f}","€43,000",M["revenue"]>=43000),("Margin",f"{M['margin']:.1f}%",f"{bench['avg_margin']}%",M["margin"]>=bench["avg_margin"]),("Runway",f"{M['runway']} mo",">12 mo",M["runway"]>=12)]:
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
        fig=go.Figure(go.Bar(x=M["labels"],y=rv,marker_color=T["green"],text=[f"€{v:.0f}K" for v in rv],textposition="outside",textfont=dict(size=10,color=T["muted"])))
        fig.update_layout(height=280,margin=dict(l=0,r=0,t=10,b=30),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis=dict(tickfont=dict(size=11,color=T["muted"])),yaxis=dict(visible=False),showlegend=False,bargap=0.35)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with ch2:
        st.markdown("##### Cost Breakdown")
        fig=go.Figure(go.Pie(labels=["Staff","Rent","Suppliers","Other"],values=[M["staff_pct"],M["rent_pct"],M["sup_pct"],M["oth_pct"]],hole=0.6,marker=dict(colors=[T["teal"],T["green"],T["navy"],T["muted"]],line=dict(color="#F7F8FA",width=2)),textinfo="label+percent",textfont=dict(size=12)))
        fig.update_layout(height=280,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ════ CASH FLOW ════
with tabs[1]:
    st.markdown("##### Cash Flow")
    if not cf.empty:
        for _,row in cf.iterrows():
            ft=str(row.get("Type","")).strip().lower(); ii=ft=="in"
            amt=float(row.get("Amount",0)) if pd.notna(row.get("Amount")) else 0
            a,b2,cc=st.columns([0.5,6,2])
            with a: st.markdown("🟢" if ii else "🔴")
            with b2: st.markdown(f"**{row.get('Description','')}**");st.caption(str(row.get("Date","")))
            with cc: st.markdown(f'<span style="color:{T["green"] if ii else T["red"]};font-weight:600;">{"+" if ii else "-"}€{amt:,.0f}</span>',unsafe_allow_html=True)
            st.divider()
    else:
        st.info("Upload data to see cash flow.")
    st.markdown("##### 4-Week Forecast")
    fig=go.Figure(go.Scatter(x=["Wk1","Wk2","Wk3","Wk4"],y=M["forecast"],mode="lines+markers",line=dict(color=T["teal"],width=3),marker=dict(size=10),fill="tozeroy",fillcolor=f"{T['teal']}18"))
    fig.add_hline(y=5000,line_dash="dash",line_color=T["red"],annotation_text="€5K safety")
    fig.update_layout(height=250,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(gridcolor="#E2E6EC",tickprefix="€"),margin=dict(l=20,r=20,t=10,b=30))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ════ REVENUE ════
with tabs[2]:
    st.markdown("##### Revenue vs Expenses")
    if len(M["rev_hist"])>1:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=M["labels"],y=[v/1000 for v in M["rev_hist"]],mode="lines+markers",name="Revenue",line=dict(color=T["green"],width=3),marker=dict(size=8),fill="tozeroy",fillcolor="rgba(76,167,113,0.1)"))
        fig.add_trace(go.Scatter(x=M["labels"],y=[v/1000 for v in M["exp_hist"]],mode="lines+markers",name="Expenses",line=dict(color=T["red"],width=3),marker=dict(size=8)))
        fig.update_layout(height=400,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="center",x=0.5),yaxis=dict(gridcolor="#E2E6EC",tickprefix="€",ticksuffix="K"),margin=dict(l=20,r=20,t=20,b=40))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

# ════ ALERTS ════
with tabs[3]:
    st.markdown("##### All Alerts")
    ct=0
    if M["exp_chg"]>10: st.error(f"**Critical:** Costs up {M['exp_chg']:.0f}%");ct+=1
    if M["runway"]<6: st.error(f"**Critical:** Runway {M['runway']} months");ct+=1
    if M["runway"]<12: st.warning("**Warning:** Runway below target");ct+=1
    if M["margin"]<bench["avg_margin"]: st.warning(f"**Warning:** Margin {M['margin']:.1f}% below avg");ct+=1
    if M["rev_chg"]>5: st.info(f"**Positive:** Revenue +{M['rev_chg']:.1f}%");ct+=1
    if ct==0: st.success("All metrics on target ✓")

# ════ CONTEXT ════
with tabs[4]:
    st.markdown("##### Business Context")
    st.markdown("##### 🏦 Economic Data")
    try:
        import requests
        r = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?lastNObservations=1&format=jsondata",timeout=8,headers={"Accept":"application/json"})
        if r.status_code==200:
            obs=r.json()["dataSets"][0]["series"]["0:0:0:0:0:0:0"]["observations"]
            rate=round(float(list(obs.values())[0][0]),2)
            st.metric("ECB Interest Rate",f"{rate}%")
        else:
            st.metric("ECB Rate","Unavailable")
    except:
        st.metric("ECB Rate","Unavailable")

    try:
        r2 = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.IE.N.000000.4.ANR?lastNObservations=1&format=jsondata",timeout=8,headers={"Accept":"application/json"})
        if r2.status_code==200:
            obs2=r2.json()["dataSets"][0]["series"]["0:0:0:0:0:0"]["observations"]
            infl=round(float(list(obs2.values())[0][0]),1)
            st.metric("Irish Inflation",f"{infl}%")
            if infl>3: st.warning(f"Inflation at {infl}% may push up costs.")
        else:
            st.metric("Irish Inflation","Unavailable")
    except:
        st.metric("Irish Inflation","Unavailable")

    st.divider()
    st.markdown("##### 📊 Industry Benchmarks")
    b1,b2,b3=st.columns(3)
    with b1: st.metric("Avg Margin",f"{bench['avg_margin']}%",f"Yours: {M['margin']:.1f}%")
    with b2: st.metric("Avg Staff %",f"{bench['avg_staff_pct']}%",f"Yours: {M['staff_pct']}%")
    with b3: st.metric("Avg Rent %",f"{bench['avg_rent_pct']}%",f"Yours: {M['rent_pct']}%")

# ════ COMPARE ════
with tabs[5]:
    st.markdown("##### Period Comparison")
    if len(M["labels"])>=2:
        c1,c2=st.columns(2)
        with c1: p1=st.selectbox("Period 1",M["labels"],index=max(0,len(M["labels"])-2))
        with c2: p2=st.selectbox("Period 2",M["labels"],index=len(M["labels"])-1)
        i1=M["labels"].index(p1);i2=M["labels"].index(p2)
        r1=M["rev_hist"][i1];r2=M["rev_hist"][i2];e1=M["exp_hist"][i1];e2=M["exp_hist"][i2]
        st.divider()
        m1,m2,m3=st.columns(3)
        with m1: st.metric("Revenue",f"€{r2:,.0f}",f"{((r2-r1)/r1*100):+.1f}%" if r1>0 else "N/A")
        with m2: st.metric("Expenses",f"€{e2:,.0f}",f"{((e2-e1)/e1*100):+.1f}%" if e1>0 else "N/A",delta_color="inverse")
        with m3: st.metric("Profit",f"€{r2-e2:,.0f}",f"{(((r2-e2)-(r1-e1))/abs(r1-e1)*100):+.1f}%" if (r1-e1)!=0 else "N/A")
        fig=go.Figure()
        fig.add_trace(go.Bar(name=p1,x=["Revenue","Expenses","Profit"],y=[r1/1000,e1/1000,(r1-e1)/1000],marker_color=T["muted"]))
        fig.add_trace(go.Bar(name=p2,x=["Revenue","Expenses","Profit"],y=[r2/1000,e2/1000,(r2-e2)/1000],marker_color=T["teal"]))
        fig.update_layout(height=300,barmode="group",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",yaxis=dict(gridcolor="#E2E6EC",tickprefix="€",ticksuffix="K"),margin=dict(l=20,r=20,t=20,b=40))
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("Need 2+ months for comparison.")

# ════ DATA ════
with tabs[6]:
    st.markdown("##### Your Data")
    if src=="demo": st.info("📋 Demo mode. Upload via sidebar.")
    else: st.success("✓ Live from Google Sheets.")
    if not fin.empty: st.markdown("**Monthly Financials**");st.dataframe(fin,use_container_width=True,hide_index=True)
    if not cf.empty: st.markdown("**Cash Flow**");st.dataframe(cf,use_container_width=True,hide_index=True)
    if info:
        st.markdown("**Business Profile**")
        for k,v in info.items(): st.markdown(f"- **{k}:** {v}")

# Footer
st.divider()
f1,f2=st.columns(2)
with f1: st.caption("**SME Pulse** · FunTech · Atlantic Technological University")
with f2: st.markdown('<p style="text-align:right;font-size:12px;color:#8896AB;">Callum Kidd · 2026</p>',unsafe_allow_html=True)
