"""
SME Pulse — Google Sheets Backend
"""
import streamlit as st
import pandas as pd
import gspread


def get_gspread_client():
    try:
        creds = st.secrets["gcp_service_account"]
        return gspread.service_account_from_dict(dict(creds))
    except Exception:
        return None


def get_spreadsheet(gc, name="SME Pulse Data"):
    try:
        return gc.open(name)
    except Exception:
        return None


def ensure_sheets(sp):
    try:
        existing = [ws.title for ws in sp.worksheets()]
        sheets = {
            "Monthly Financials": ["Month", "Year", "Revenue", "Expenses", "Staff Costs", "Rent", "Supplier Costs", "Other Costs"],
            "Cash Flow": ["Date", "Description", "Type", "Amount", "Category", "Status"],
            "Targets": ["Metric", "Target Value", "Unit", "Direction"],
            "Business Info": ["Field", "Value"],
        }
        for name, headers in sheets.items():
            if name not in existing:
                ws = sp.add_worksheet(title=name, rows=100, cols=20)
                ws.append_row(headers)
            else:
                ws = sp.worksheet(name)
                if not ws.get_all_values():
                    ws.append_row(headers)
    except Exception:
        pass


def read_df(sp, tab):
    try:
        ws = sp.worksheet(tab)
        data = ws.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def read_info(sp):
    try:
        ws = sp.worksheet("Business Info")
        data = ws.get_all_records()
        if not data:
            return {}
        return {str(r.get("Field", "")): str(r.get("Value", "")) for r in data if str(r.get("Field", "")).strip()}
    except Exception:
        return {}


def write_df(sp, tab, df, headers):
    try:
        ws = sp.worksheet(tab)
        ws.clear()
        ws.append_row(headers)
        for _, row in df.iterrows():
            ws.append_row([str(row.get(h, "")) for h in headers])
        return True
    except Exception:
        return False


def write_info(sp, info_dict):
    try:
        ws = sp.worksheet("Business Info")
        ws.clear()
        ws.append_row(["Field", "Value"])
        for k, v in info_dict.items():
            ws.append_row([str(k), str(v)])
        return True
    except Exception:
        return False


def upload_excel(sp, uploaded_file):
    results = {"success": [], "errors": []}
    try:
        xls = pd.ExcelFile(uploaded_file)

        if "Monthly Financials" in xls.sheet_names:
            df = pd.read_excel(xls, "Monthly Financials", header=3)
            df.columns = [str(c).split("(")[0].strip().replace("€", "").strip() for c in df.columns]
            df = df.dropna(subset=[df.columns[0]])
            h = ["Month", "Year", "Revenue", "Expenses", "Staff Costs", "Rent", "Supplier Costs", "Other Costs"]
            if write_df(sp, "Monthly Financials", df, h):
                results["success"].append("Monthly Financials")

        if "Cash Flow" in xls.sheet_names:
            df = pd.read_excel(xls, "Cash Flow", header=3)
            df.columns = [str(c).split("(")[0].strip().replace("€", "").strip() for c in df.columns]
            df = df.dropna(subset=[df.columns[0]])
            h = ["Date", "Description", "Type", "Amount", "Category", "Status"]
            if write_df(sp, "Cash Flow", df, h):
                results["success"].append("Cash Flow")

        if "Targets" in xls.sheet_names:
            df = pd.read_excel(xls, "Targets", header=3)
            df.columns = [str(c).split("(")[0].strip().replace("€", "").strip() for c in df.columns]
            df = df.dropna(subset=[df.columns[0]])
            h = ["Metric", "Target Value", "Unit", "Direction"]
            if write_df(sp, "Targets", df, h):
                results["success"].append("Targets")

        if "Business Info" in xls.sheet_names:
            df = pd.read_excel(xls, "Business Info", header=2)
            if len(df.columns) >= 2:
                info = {str(r.iloc[0]).strip(): str(r.iloc[1]).strip() for _, r in df.iterrows() if str(r.iloc[0]).strip() not in ("", "nan")}
                if write_info(sp, info):
                    results["success"].append("Business Info")
    except Exception as e:
        results["errors"].append(str(e))
    return results


def clean_num(series):
    return pd.to_numeric(series.astype(str).str.replace(",", "").str.replace("€", "").str.replace(" ", ""), errors="coerce").fillna(0)


def compute_metrics(fin_df, cf_df, tgt_df, info):
    if fin_df.empty:
        return sample_metrics()

    df = fin_df.copy()
    for c in ["Revenue", "Expenses", "Staff Costs", "Rent", "Supplier Costs", "Other Costs", "Year"]:
        if c in df.columns:
            df[c] = clean_num(df[c])
    if "Month" in df.columns:
        df = df[df["Month"].astype(str).str.strip() != ""]

    if df.empty:
        return sample_metrics()

    mo = {m: i for i, m in enumerate(["January","February","March","April","May","June","July","August","September","October","November","December"])}
    df["_s"] = df["Month"].map(mo).fillna(99)
    df = df.sort_values(["Year", "_s"]).drop(columns=["_s"])

    lat = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else lat
    m = {}

    m["revenue"] = float(lat.get("Revenue", 0))
    m["expenses"] = float(lat.get("Expenses", 0))
    m["profit"] = m["revenue"] - m["expenses"]
    m["margin"] = (m["profit"] / m["revenue"] * 100) if m["revenue"] > 0 else 0

    pr = float(prev.get("Revenue", 0))
    m["revenue_change"] = ((m["revenue"] - pr) / pr * 100) if pr > 0 else 0
    pe = float(prev.get("Expenses", 0))
    m["expenses_change"] = ((m["expenses"] - pe) / pe * 100) if pe > 0 else 0

    cash_str = info.get("Monthly Cash Balance (€)", info.get("Monthly Cash Balance", "23450"))
    try:
        m["cash_balance"] = float(str(cash_str).replace(",", "").replace("€", ""))
    except:
        m["cash_balance"] = 23450

    burn = (m["expenses"] - m["revenue"]) if m["expenses"] > m["revenue"] else m["expenses"] * 0.1
    m["runway_months"] = round(m["cash_balance"] / burn, 1) if burn > 0 else 99

    if m["expenses"] > 0:
        m["staff_pct"] = round(float(lat.get("Staff Costs", 0)) / m["expenses"] * 100, 1)
        m["rent_pct"] = round(float(lat.get("Rent", 0)) / m["expenses"] * 100, 1)
        m["supplier_pct"] = round(float(lat.get("Supplier Costs", 0)) / m["expenses"] * 100, 1)
        m["other_pct"] = round(100 - m["staff_pct"] - m["rent_pct"] - m["supplier_pct"], 1)
    else:
        m["staff_pct"] = m["rent_pct"] = m["supplier_pct"] = m["other_pct"] = 25

    m["rev_hist"] = df["Revenue"].tolist()
    m["exp_hist"] = df["Expenses"].tolist()
    m["month_labels"] = df["Month"].tolist()
    m["latest_month"] = f"{lat.get('Month','')} {int(lat.get('Year',0))}"
    m["owner"] = info.get("Owner Name", "Liam")
    m["biz_name"] = info.get("Business Name", "Your Business")

    score = 50
    if m["margin"] > 25: score += 15
    elif m["margin"] > 15: score += 10
    if m["revenue_change"] > 0: score += 10
    if m["runway_months"] > 12: score += 15
    elif m["runway_months"] > 6: score += 8
    if m["expenses_change"] < 5: score += 10
    m["health_score"] = min(score, 100)

    return m


def sample_metrics():
    return {
        "revenue": 45200, "expenses": 31800, "profit": 13400, "margin": 29.6,
        "revenue_change": 8.2, "expenses_change": 12.0,
        "cash_balance": 23450, "runway_months": 8.2,
        "staff_pct": 42, "rent_pct": 22, "supplier_pct": 24, "other_pct": 12,
        "rev_hist": [38000, 42000, 39000, 48000, 44000, 45200],
        "exp_hist": [30000, 33000, 31500, 36000, 34000, 31800],
        "month_labels": ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"],
        "latest_month": "February 2026", "owner": "Liam", "biz_name": "Sample Business",
        "health_score": 74,
    }
