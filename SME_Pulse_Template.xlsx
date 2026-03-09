"""
SME Pulse Backend v4 — Google Sheets + APIs + Industry-Aware Features
"""
import streamlit as st
import pandas as pd
import gspread
import requests

# ═══ GOOGLE SHEETS ═══
def get_gc():
    try: return gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
    except: return None

def get_sp(gc, name="SME Pulse Data"):
    try: return gc.open(name)
    except: return None

def ensure(sp):
    try:
        ex = [w.title for w in sp.worksheets()]
        for n, h in {
            "Monthly Financials": ["Month","Year","Revenue","Expenses","Staff Costs","Rent","Supplier Costs","Other Costs"],
            "Cash Flow": ["Date","Description","Type","Amount","Category","Status"],
            "Targets": ["Metric","Target Value","Unit","Direction"],
            "Business Info": ["Field","Value"],
        }.items():
            if n not in ex:
                w = sp.add_worksheet(title=n, rows=100, cols=20); w.append_row(h)
            else:
                w = sp.worksheet(n)
                if not w.get_all_values(): w.append_row(h)
    except: pass

def read_df(sp, tab):
    try:
        d = sp.worksheet(tab).get_all_records()
        return pd.DataFrame(d) if d else pd.DataFrame()
    except: return pd.DataFrame()

def read_info(sp):
    try:
        d = sp.worksheet("Business Info").get_all_records()
        return {str(r.get("Field","")): str(r.get("Value","")) for r in d if str(r.get("Field","")).strip()} if d else {}
    except: return {}

def write_df(sp, tab, df, headers):
    try:
        w = sp.worksheet(tab); w.clear(); w.append_row(headers)
        for _, r in df.iterrows(): w.append_row([str(r.get(h,"")) for h in headers])
        return True
    except: return False

def write_info(sp, d):
    try:
        w = sp.worksheet("Business Info"); w.clear(); w.append_row(["Field","Value"])
        for k,v in d.items(): w.append_row([str(k),str(v)])
        return True
    except: return False

def upload_excel(sp, f):
    res = {"success":[],"errors":[]}
    try:
        xls = pd.ExcelFile(f)
        for tab, h in {
            "Monthly Financials": ["Month","Year","Revenue","Expenses","Staff Costs","Rent","Supplier Costs","Other Costs"],
            "Cash Flow": ["Date","Description","Type","Amount","Category","Status"],
            "Targets": ["Metric","Target Value","Unit","Direction"],
        }.items():
            if tab in xls.sheet_names:
                df = pd.read_excel(xls, tab, header=3)
                df.columns = [str(c).split("(")[0].strip().replace("€","").strip() for c in df.columns]
                df = df.dropna(subset=[df.columns[0]])
                if write_df(sp, tab, df, h): res["success"].append(tab)
                else: res["errors"].append(tab)
        if "Business Info" in xls.sheet_names:
            df = pd.read_excel(xls, "Business Info", header=2)
            if len(df.columns)>=2:
                info = {str(r.iloc[0]).strip():str(r.iloc[1]).strip() for _,r in df.iterrows() if str(r.iloc[0]).strip() not in ("","nan")}
                if write_info(sp, info): res["success"].append("Business Info")
    except Exception as e: res["errors"].append(str(e))
    return res

def quick_entry(sp, month, year, rev, exp, staff, rent, sup, oth):
    try:
        sp.worksheet("Monthly Financials").append_row([month,int(year),float(rev),float(exp),float(staff),float(rent),float(sup),float(oth)])
        return True
    except: return False

# ═══ METRICS ═══
def cnum(s):
    return pd.to_numeric(s.astype(str).str.replace(",","").str.replace("€","").str.replace(" ",""), errors="coerce").fillna(0)

def compute(fin, cf, tgt, info):
    if fin.empty: return sample()
    df = fin.copy()
    for c in ["Revenue","Expenses","Staff Costs","Rent","Supplier Costs","Other Costs","Year"]:
        if c in df.columns: df[c] = cnum(df[c])
    if "Month" in df.columns: df = df[df["Month"].astype(str).str.strip()!=""]
    if df.empty: return sample()

    mo = {m:i for i,m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"])}
    df["_s"] = df["Month"].map(mo).fillna(99)
    df = df.sort_values(["Year","_s"]).drop(columns=["_s"])

    L, P = df.iloc[-1], (df.iloc[-2] if len(df)>1 else df.iloc[-1])
    m = {}
    m["revenue"]=float(L.get("Revenue",0)); m["expenses"]=float(L.get("Expenses",0))
    m["profit"]=m["revenue"]-m["expenses"]
    m["margin"]=(m["profit"]/m["revenue"]*100) if m["revenue"]>0 else 0
    pr=float(P.get("Revenue",0)); m["rev_chg"]=((m["revenue"]-pr)/pr*100) if pr>0 else 0
    pe=float(P.get("Expenses",0)); m["exp_chg"]=((m["expenses"]-pe)/pe*100) if pe>0 else 0

    cs = info.get("Monthly Cash Balance (€)", info.get("Monthly Cash Balance","23450"))
    try: m["cash"]=float(str(cs).replace(",","").replace("€",""))
    except: m["cash"]=23450

    burn = (m["expenses"]-m["revenue"]) if m["expenses"]>m["revenue"] else m["expenses"]*0.1
    m["runway"]=round(m["cash"]/burn,1) if burn>0 else 99

    if m["expenses"]>0:
        m["staff_pct"]=round(float(L.get("Staff Costs",0))/m["expenses"]*100,1)
        m["rent_pct"]=round(float(L.get("Rent",0))/m["expenses"]*100,1)
        m["sup_pct"]=round(float(L.get("Supplier Costs",0))/m["expenses"]*100,1)
        m["oth_pct"]=round(100-m["staff_pct"]-m["rent_pct"]-m["sup_pct"],1)
    else: m["staff_pct"]=m["rent_pct"]=m["sup_pct"]=m["oth_pct"]=25

    m["rev_hist"]=df["Revenue"].tolist(); m["exp_hist"]=df["Expenses"].tolist()
    m["labels"]=df["Month"].tolist()
    m["latest"]=f"{L.get('Month','')} {int(L.get('Year',0))}"
    m["owner"]=info.get("Owner Name","Liam"); m["biz"]=info.get("Business Name","Your Business")
    m["industry"]=info.get("Industry","Retail"); m["location"]=info.get("Location","Galway")
    m["employees"]=info.get("Employees","15")

    # Cash forecast 4 weeks
    weekly_burn = m["expenses"]/4.33
    weekly_in = m["revenue"]/4.33
    m["forecast"]=[]; bal=m["cash"]
    for w in range(1,5):
        bal = bal - weekly_burn + weekly_in
        m["forecast"].append(round(bal))

    # Health score
    sc=50
    if m["margin"]>25: sc+=15
    elif m["margin"]>15: sc+=10
    if m["rev_chg"]>0: sc+=10
    if m["runway"]>12: sc+=15
    elif m["runway"]>6: sc+=8
    if m["exp_chg"]<5: sc+=10
    m["health"]=min(sc,100)

    # Cash flow summary
    if not cf.empty:
        cfc=cf.copy()
        if "Amount" in cfc.columns: cfc["Amount"]=cnum(cfc["Amount"])
        m["cf_in"]=float(cfc[cfc["Type"].astype(str).str.strip().str.lower()=="in"]["Amount"].sum())
        m["cf_out"]=float(cfc[cfc["Type"].astype(str).str.strip().str.lower()=="out"]["Amount"].sum())
    else: m["cf_in"]=m["cf_out"]=0

    return m

def sample():
    return {"revenue":45200,"expenses":31800,"profit":13400,"margin":29.6,"rev_chg":8.2,"exp_chg":12.0,
        "cash":23450,"runway":8.2,"staff_pct":42,"rent_pct":22,"sup_pct":24,"oth_pct":12,
        "rev_hist":[38000,42000,39000,48000,44000,45200],"exp_hist":[30000,33000,31500,36000,34000,31800],
        "labels":["Sep","Oct","Nov","Dec","Jan","Feb"],"latest":"February 2026","owner":"Liam",
        "biz":"Sample Business","industry":"Retail","location":"Galway","employees":"15","health":74,
        "cf_in":15100,"cf_out":15200,"forecast":[22100,20800,19500,18200]}

# ═══ INDUSTRY CONFIG ═══
# Which features show for which industries
INDUSTRY_FEATURES = {
    "Retail":               {"weather": True,  "trends": True,  "exchange": True,  "unit_econ": False, "network": False},
    "Hospitality":          {"weather": True,  "trends": True,  "exchange": False, "unit_econ": False, "network": False},
    "Fitness":              {"weather": True,  "trends": True,  "exchange": False, "unit_econ": False, "network": False},
    "Professional Services":{"weather": False, "trends": True,  "exchange": False, "unit_econ": True,  "network": False},
    "Technology":           {"weather": False, "trends": True,  "exchange": True,  "unit_econ": True,  "network": True},
}

BENCHMARKS = {
    "Retail":               {"avg_margin":22.0,"avg_staff_pct":38.0,"avg_rent_pct":18.0,"survival_5yr":62},
    "Hospitality":          {"avg_margin":15.0,"avg_staff_pct":45.0,"avg_rent_pct":20.0,"survival_5yr":55},
    "Fitness":              {"avg_margin":18.0,"avg_staff_pct":35.0,"avg_rent_pct":25.0,"survival_5yr":58},
    "Professional Services":{"avg_margin":32.0,"avg_staff_pct":50.0,"avg_rent_pct":12.0,"survival_5yr":72},
    "Technology":           {"avg_margin":28.0,"avg_staff_pct":55.0,"avg_rent_pct":8.0,"survival_5yr":68},
}

def get_features(industry):
    return INDUSTRY_FEATURES.get(industry, INDUSTRY_FEATURES["Retail"])

def get_bench(industry):
    return BENCHMARKS.get(industry, BENCHMARKS["Retail"])

# ═══ APIS ═══
@st.cache_data(ttl=3600)
def get_weather(location="Galway"):
    try:
        key = st.secrets.get("openweather_api_key", None)
        if not key: return None
        r = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={location},IE&appid={key}&units=metric&cnt=40", timeout=8)
        if r.status_code!=200: return None
        days={}
        for item in r.json().get("list",[]):
            dt=item["dt_txt"][:10]
            if dt not in days:
                days[dt]={"temp":round(item["main"]["temp"]),"desc":item["weather"][0]["description"].title(),"rain":item.get("rain",{}).get("3h",0)}
        return list(days.items())[:7]
    except: return None

@st.cache_data(ttl=86400)
def get_ecb_rate():
    try:
        r = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?lastNObservations=1&format=jsondata", timeout=8, headers={"Accept":"application/json"})
        if r.status_code!=200: return None
        obs=r.json()["dataSets"][0]["series"]["0:0:0:0:0:0:0"]["observations"]
        return round(float(list(obs.values())[0][0]),2)
    except: return None

@st.cache_data(ttl=86400)
def get_inflation():
    try:
        r = requests.get("https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.IE.N.000000.4.ANR?lastNObservations=1&format=jsondata", timeout=8, headers={"Accept":"application/json"})
        if r.status_code!=200: return None
        obs=r.json()["dataSets"][0]["series"]["0:0:0:0:0:0"]["observations"]
        return round(float(list(obs.values())[0][0]),1)
    except: return None

@st.cache_data(ttl=3600)
def get_exchange():
    try:
        key = st.secrets.get("exchange_api_key", None)
        if not key: return None
        r = requests.get(f"https://openexchangerates.org/api/latest.json?app_id={key}&base=USD", timeout=8)
        if r.status_code!=200: return None
        rates=r.json().get("rates",{}); eur=rates.get("EUR",1); gbp=rates.get("GBP",1)
        return {"EUR_GBP":round(gbp/eur,4),"EUR_USD":round(1/eur,4)}
    except: return None

@st.cache_data(ttl=86400)
def get_trends(keyword):
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl='en-IE', tz=0)
        pt.build_payload([keyword], cat=0, timeframe='today 12-m', geo='IE')
        df = pt.interest_over_time()
        if df.empty: return None
        return df[keyword].tolist()[-12:]
    except: return None
