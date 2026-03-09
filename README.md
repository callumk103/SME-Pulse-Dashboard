# SME Pulse — Business Health Dashboard

**A FunTech Project · Atlantic Technological University**

SME Pulse is a business health dashboard designed to help small and medium-sized business owners monitor financial performance, spot risks early, and make better decisions — without needing financial expertise.

## Features

- **Business Health Score** — single glanceable metric summarising overall business health
- **Cash Runway Indicator** — months of operating cash remaining with trend line
- **KPI Cards** — cash balance, revenue, expenses, and net profit with sparkline trends and forecasts
- **RAG Milestone Tracking** — red/amber/green status on key operational targets vs plan
- **Deviation Alerts** — flagged warnings when metrics deviate significantly from targets
- **Revenue Trends + Forecast** — visual bar charts with projected future months
- **Cost Breakdown** — donut chart showing expense allocation
- **Cash Flow Forecast** — upcoming inflows and outflows timeline
- **Owner/Board View Toggle** — customisable detail level for different audiences
- **Quick Actions** — export reports, share with accountant, set alert thresholds

## Tech Stack

- **Python** with **Streamlit** for the web application
- **Plotly** for interactive data visualisations
- **ATU Brand Guidelines** colour palette and typography

## Live Demo

Deployed on Streamlit Community Cloud:
> _Add your URL here after deployment_

## Setup & Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/sme-pulse-dashboard.git
cd sme-pulse-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **New app**
5. Select your repo, branch (`main`), and file (`app.py`)
6. Click **Deploy**

Your app will be live at `https://YOUR_APP.streamlit.app`

## Project Context

This dashboard was developed as part of the FunTech module at Atlantic Technological University. It addresses the challenge that SME owners face in understanding their business performance due to time constraints, limited financial knowledge, and disconnected data systems.

### Research Basis

- User persona: Liam — a stressed SME retail owner in Galway who needs quick, clear business insights
- Customer research interviews with SME stakeholders
- Design informed by OECD (2023) SME financial management research and McKinsey (2021) digital transformation insights

## Author

**Callum Kidd** — Project Manager
Atlantic Technological University · 2026
