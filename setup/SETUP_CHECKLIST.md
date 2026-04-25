# Budget Management Web — Setup Checklist

> Follow steps in order. Check off each item before moving to the next.
> All monetary values: THB | Fiscal Year: January–December

---

## Part A — Azure Portal (portal.azure.com)

---

### Step 1 — Entra ID App Registration
> **Purpose:** Enables user login (MSAL) and email sending (Microsoft Graph API)

- [ ] Go to **Azure Portal** → search `Azure Active Directory` → **App registrations**
- [ ] Click **New registration**
  - Name: `budget-mgmt-app`
  - Supported account types: `Accounts in this organizational directory only`
  - Redirect URI: `Web` → `http://localhost:8501`
  - Click **Register**
- [ ] On the app overview page — **copy and save**:
  - `Application (client) ID` → save as `ENTRA_CLIENT_ID`
  - `Directory (tenant) ID` → save as `ENTRA_TENANT_ID`
- [ ] Create client secret:
  - Left menu → **Certificates & secrets** → **New client secret**
  - Description: `budget-app-secret`, Expires: `24 months`
  - Click **Add** → **immediately copy the Value** (shown only once)
  - Save as `ENTRA_CLIENT_SECRET`
- [ ] Add API permissions:
  - Left menu → **API permissions** → **Add a permission** → **Microsoft Graph**
  - **Delegated permissions** → search and add:
    - `User.Read` (for reading login user profile)
    - `Mail.Send` (for email notifications)
  - Click **Grant admin consent for [your org]** → confirm Yes
- [ ] Add localhost redirect (for Streamlit local dev):
  - Left menu → **Authentication** → under Web → Redirect URIs
  - Confirm `http://localhost:8501` is listed
  - Enable: `Access tokens` + `ID tokens` checkboxes → Save

**Save to .env:**
```
ENTRA_CLIENT_ID=<paste Application client ID>
ENTRA_TENANT_ID=<paste Directory tenant ID>
ENTRA_CLIENT_SECRET=<paste client secret value>
```

---

### Step 2 — Azure SQL Server + Database
> **Purpose:** Transactional database for budget input, approvals, user roles

- [ ] Go to **Azure Portal** → **Create a resource** → search `SQL Database` → **Create**
- [ ] **Basics tab:**
  - Subscription: your subscription
  - Resource group: create new → `rg-budget-mgmt`
  - Database name: `budget_db`
  - Server: click **Create new**
    - Server name: `budget-mgmt-sql` (must be globally unique → becomes `budget-mgmt-sql.database.windows.net`)
    - Location: same region you'll use throughout (e.g., `Southeast Asia`)
    - Authentication: `SQL authentication`
    - Admin login: `budgetadmin`
    - Password: create strong password
    - Click **OK**
  - Compute + storage: click **Configure database** → select **Basic** (5 DTU, ~$5/mo for dev)
- [ ] **Networking tab:**
  - Connectivity: `Public endpoint`
  - Firewall rules: `Yes` to "Allow Azure services and resources"
  - Click **Add current client IP** (adds your machine's IP)
- [ ] Click **Review + Create** → **Create** (takes ~2 min)
- [ ] After creation — go to the SQL Server resource → **Connection strings** → copy **ODBC** string

**Save to .env:**
```
DB_SERVER=budget-mgmt-sql.database.windows.net
DB_NAME=budget_db
DB_USER=budgetadmin
DB_PASSWORD=<your password>
```

> **Note:** Use `ODBC Driver 17 for SQL Server` — already installed on dev machine.

---

### Step 3 — Azure Container Registry (ACR)
> **Purpose:** Stores Docker images for deployment to Container Apps

- [ ] Go to **Azure Portal** → **Create a resource** → search `Container Registry` → **Create**
  - Resource group: `rg-budget-mgmt`
  - Registry name: `budgetmgmtacr` (globally unique, letters/numbers only)
  - Location: same region as Step 2
  - SKU: `Basic`
  - Click **Review + Create** → **Create**
- [ ] After creation — go to resource → **Access keys**
  - Enable **Admin user** toggle → copy:
    - Login server (e.g., `budgetmgmtacr.azurecr.io`)
    - Username
    - Password

**Save to notes:**
```
ACR_LOGIN_SERVER=budgetmgmtacr.azurecr.io
ACR_USERNAME=budgetmgmtacr
ACR_PASSWORD=<copy from Access keys>
```

---

### Step 4 — Container Apps Environment
> **Purpose:** Runtime environment for the Streamlit app (Azure Container Apps)

- [ ] Go to **Azure Portal** → **Create a resource** → search `Container Apps Environment` → **Create**
  - Resource group: `rg-budget-mgmt`
  - Environment name: `budget-mgmt-env`
  - Region: same as above
  - **Monitoring tab:** Create new Log Analytics workspace → name: `budget-mgmt-logs`
  - Click **Review + Create** → **Create** (takes ~3 min)

**Save to notes:**
```
CONTAINER_ENV_NAME=budget-mgmt-env
RESOURCE_GROUP=rg-budget-mgmt
```

---

## Part B — Microsoft Fabric (app.fabric.microsoft.com)

---

### Step 5 — Fabric Workspace
> **Purpose:** Container for all Fabric assets (Lakehouse, Notebooks)

- [ ] Go to **app.fabric.microsoft.com**
- [ ] Left sidebar → **Workspaces** → **New workspace**
  - Name: `budget-mgmt`
  - License: use your org's Fabric capacity (or Trial if available)
  - Click **Apply**
- [ ] Open the workspace → look at browser URL → copy the workspace ID
  - URL format: `https://app.fabric.microsoft.com/groups/<WORKSPACE_ID>/...`

**Save to .env:**
```
FABRIC_WORKSPACE_ID=<paste workspace ID from URL>
```

---

### Step 6 — Fabric Lakehouse
> **Purpose:** Stores SAP actuals (G/L line items from FAGLL03H) for dashboards

- [ ] Inside `budget-mgmt` workspace → **New** → **Lakehouse**
  - Name: `budget_actuals`
  - Click **Create**
- [ ] After creation → look at browser URL → copy the lakehouse ID
  - URL format: `.../lakehouses/<LAKEHOUSE_ID>`
- [ ] Note the SQL analytics endpoint (shown in Lakehouse settings) — used for read-only queries

**Save to .env:**
```
FABRIC_LAKEHOUSE_ID=<paste lakehouse ID from URL>
```

---

### Step 7 — Fabric Notebook (placeholder)
> **Purpose:** Will handle SAP actuals upload (Replace-by-Month) and email notifications

- [ ] Inside `budget-mgmt` workspace → **New** → **Notebook**
  - Name: `nb_upload_actuals`
  - Add a comment cell: `# SAP Actuals Upload — Replace by Month logic — TODO`
  - Click **Save**
- [ ] Copy notebook ID from URL:
  - URL format: `.../notebooks/<NOTEBOOK_ID>`
- [ ] Repeat — create second notebook:
  - Name: `nb_send_email`
  - Add comment: `# Email notification via Microsoft Graph API — TODO`
  - Copy notebook ID

**Save to .env:**
```
FABRIC_NOTEBOOK_ACTUALS_ID=<nb_upload_actuals ID>
FABRIC_NOTEBOOK_EMAIL_ID=<nb_send_email ID>
```

---

## Part C — Local Machine

---

### Step 8 — Create Python Virtual Environment

Open VS Code terminal in `c:\04.budget_management_web\`:

```bash
python -m venv venv
venv\Scripts\activate
```

Confirm activated — terminal prompt should show `(venv)`.

- [ ] venv created
- [ ] venv activated

---

### Step 9 — Create requirements.txt

- [ ] Create file `c:\04.budget_management_web\requirements.txt` with content:

```
streamlit==1.54.0
pyodbc==5.3.0
sqlalchemy==2.0.49
pandas==2.3.3
msal==1.36.0
openpyxl==3.1.5
python-dotenv
requests==2.32.4
plotly==6.7.0
Pillow==12.1.1
numpy==2.4.2
pytest==9.0.2
faker
```

- [ ] Run install:
```bash
pip install -r requirements.txt
```

---

### Step 10 — Create .env File

- [ ] Create file `c:\04.budget_management_web\.env` — **NEVER commit this file to GitHub**
- [ ] Confirm `.env` is in `.gitignore` (should already be there)
- [ ] Fill in all values collected from Steps 1–7:

```env
# Azure SQL Database
DB_SERVER=budget-mgmt-sql.database.windows.net
DB_NAME=budget_db
DB_USER=budgetadmin
DB_PASSWORD=

# Azure Entra ID (MSAL login + Microsoft Graph)
ENTRA_CLIENT_ID=
ENTRA_TENANT_ID=
ENTRA_CLIENT_SECRET=

# Approval workflow — fixed recipients
NIPAPORNT_EMAIL=
WARAPORNT_EMAIL=

# Microsoft Fabric
FABRIC_WORKSPACE_ID=
FABRIC_LAKEHOUSE_ID=
FABRIC_NOTEBOOK_ACTUALS_ID=
FABRIC_NOTEBOOK_EMAIL_ID=
```

---

### Step 11 — Create Project Folder Structure

Run in terminal (venv activated):

```bash
mkdir pages utils db
type nul > app.py
type nul > pages\01_submit_budget.py
type nul > pages\02_approve_vp.py
type nul > pages\03_approve_staff.py
type nul > pages\04_approve_manager.py
type nul > pages\05_dashboard.py
type nul > pages\06_admin.py
type nul > utils\auth.py
type nul > utils\email.py
type nul > db\connection.py
type nul > db\schema.sql
```

Expected structure:
```
c:\04.budget_management_web\
├── app.py
├── pages/
│   ├── 01_submit_budget.py
│   ├── 02_approve_vp.py
│   ├── 03_approve_staff.py
│   ├── 04_approve_manager.py
│   ├── 05_dashboard.py
│   └── 06_admin.py
├── utils/
│   ├── auth.py
│   └── email.py
├── db/
│   ├── connection.py
│   └── schema.sql
├── setup/                    ← you are here
├── venv/
├── .env                      ← never commit
├── .gitignore
├── requirements.txt
├── CLAUDE.md
└── README.md
```

- [ ] All folders created
- [ ] All placeholder files created

---

### Step 12 — Create SQL Tables (schema.sql)

- [ ] Write `db/schema.sql` — 4 tables:
  - `user_division_map`
  - `budget_submissions`
  - `approval_status`
  - `approval_log`

> Ask Claude to generate this file — it knows the full schema from CLAUDE.md.

- [ ] Run SQL in Azure Portal:
  - Go to SQL Database `budget_db` → left menu → **Query editor**
  - Login with `budgetadmin` + password
  - Paste content of `schema.sql` → **Run**
  - Confirm tables created: `SELECT name FROM sys.tables`

---

### Step 13 — Verify Local Dev Works

- [ ] Run Streamlit:
```bash
streamlit run app.py
```
- [ ] Browser opens at `http://localhost:8501` — no errors
- [ ] Test DB connection (add 3 lines to `db/connection.py`, run python to confirm connect)

---

## Summary

| Step | What | Where | Est. Time |
|------|------|-------|-----------|
| 1 | Entra ID App Registration | Azure Portal | 15 min |
| 2 | Azure SQL Server + DB | Azure Portal | 10 min |
| 3 | Container Registry | Azure Portal | 5 min |
| 4 | Container Apps Environment | Azure Portal | 5 min |
| 5 | Fabric Workspace | Fabric Portal | 5 min |
| 6 | Fabric Lakehouse | Fabric Portal | 5 min |
| 7 | Fabric Notebooks (x2) | Fabric Portal | 5 min |
| 8 | Python venv | Local terminal | 5 min |
| 9 | requirements.txt + pip install | Local | 5 min |
| 10 | .env file | Local | 10 min |
| 11 | Folder structure | Local terminal | 5 min |
| 12 | SQL tables (schema.sql) | Azure Portal | 20 min |
| 13 | Verify local dev | Local | 5 min |
| **Total** | | | **~1.5 hrs** |

---

> **After Step 13 is complete — start coding `app.py`**
