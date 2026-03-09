# ═══════════════════════════════════════════════════════════
# SME Pulse — Streamlit Secrets Configuration
# ═══════════════════════════════════════════════════════════
#
# HOW TO USE:
# 1. Copy this file's contents
# 2. Go to your Streamlit Cloud app → Settings → Secrets
# 3. Paste and replace the placeholder values with your real credentials
#
# To get these credentials:
# 1. Go to https://console.cloud.google.com
# 2. Create a new project (or use existing)
# 3. Enable "Google Sheets API" and "Google Drive API"
# 4. Go to Credentials → Create Credentials → Service Account
# 5. Give it a name, click Create
# 6. Click on the service account → Keys → Add Key → JSON
# 7. Download the JSON file — its contents go below
# 8. Create a Google Sheet called "SME Pulse Data"
# 9. Share that sheet with the service account email (the client_email below)
#
# ═══════════════════════════════════════════════════════════

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
