# Budget Management Web Application

Internal OPEX budget management system for the budget department.
Users submit budget requests by division, managers approve through a workflow, and the budget team monitors actuals vs budget via dashboards.

---

> **Continuing this project with Claude?**
> Start your new conversation with:
> ```
> I'm continuing the budget management web project.
> Read CLAUDE.md and README.md for full context.
> ```

---

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Project Structure](#project-structure)
- [Database Setup](#database-setup)
- [Azure Cloud Setup](#azure-cloud-setup)
- [Deployment](#deployment)
- [Workflow](#workflow)
- [Features](#features)

---

## Project Overview

### Business Goals
1. Reduce manual repetitive work — pulling data from SAP and consolidating Excel files from users
2. Give department-level users self-service access to their own division's budget vs actuals
3. Help the budget team use data easily for dashboards and presentations

### Data Sources
| Source | Data Type | Frequency |
|--------|-----------|-----------|
| SAP (T-Code: FAGLL03H) | Actuals — G/L Line Items | Monthly |
| Excel Upload (SharePoint) | Board-approved Budget | Yearly |
| Web Form (this app) | User budget requests (OPEX) | Per budget cycle |

### Approval Workflow
```
User (fill budget)
    ↓
VP / AVP (of user's division)
    ↓
Nipapornt (Budget Staff)
    ↓
Warapornt (Budget Manager)
    ↓
Data flows to Fabric Lakehouse (Warehouse)
```

---

## Architecture

```
User Browser
    │
    ▼
Streamlit Web App  ←──── Azure Entra ID (Login + Role-Based Access)
    │
    ├── Azure SQL Database          ← Transactional data (fast read/write)
    │     ├── budget_submissions    ← User budget input
    │     ├── approval_status       ← Current approval state
    │     ├── approval_log          ← Full approval history
    │     └── user_division_map     ← User → Division → Role mapping (RLS)
    │
    ├── Fabric Lakehouse (OneLake)  ← Analytical data (reporting)
    │     ├── actuals_data          ← SAP monthly data
    │     ├── budget_master         ← Board-approved budget
    │     └── combined_data         ← Merged for dashboards
    │
    └── Fabric Notebook             ← Email notifications
          └── Microsoft Graph API   ← Send via Office 365
```

### Deployment Architecture
```
Developer Laptop (VS Code)
    │  write code & test locally
    │
    ├──► GitHub (budget_management_web)
    │         │  git push
    │         ▼
    │    Azure Cloud Shell
    │         │  git pull + docker build + az deploy
    │         ▼
    │    Azure Container Registry
    │         │  docker image stored
    │         ▼
    └──► Azure Container Apps  ←── Users access via browser URL
```

---

## Tech Stack

### Frontend / Web
| Tool | Purpose | Status |
|------|---------|--------|
| Streamlit 1.54+ | Web UI framework (Python-based) | Ready |
| Plotly | Charts and dashboards | Ready |
| Pandas | Data tables display | Ready |

### Backend / Database
| Tool | Purpose | Status |
|------|---------|--------|
| Azure SQL Database | Transactional data (budget input, approvals) | Need to create |
| Microsoft Fabric Lakehouse | Analytical data (SAP actuals, reporting) | Need to create |
| Microsoft Fabric OneLake | Raw file storage layer | Need to create |

### Authentication & Security
| Tool | Purpose | Status |
|------|---------|--------|
| Azure Entra ID (Azure AD) | Login, role-based access, RLS by division | Need to configure |
| MSAL (Python) | Azure AD auth in Streamlit | Installed |

### Notifications
| Tool | Purpose | Status |
|------|---------|--------|
| Fabric Notebook | Run notification script | Need to create |
| Microsoft Graph API | Send email via Office 365 | Need service principal |

### DevOps & Deployment
| Tool | Purpose | Status |
|------|---------|--------|
| GitHub | Version control & code storage | Ready |
| Azure Cloud Shell | Deploy commands (no local install needed) | Ready (browser) |
| Azure Container Apps | Host Streamlit app on cloud 24/7 | Need to create |
| Docker | Package app for cloud (used inside Cloud Shell) | Available in Cloud Shell |
| Azure CLI (az) | Deploy commands | Available in Cloud Shell |

---

## Prerequisites

### On Your Laptop (Developer Machine)

#### Already Installed
| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.14.0 | |
| Git | 2.52.0 | |
| VS Code | latest | |
| ODBC Driver 17 for SQL Server | - | Required for Azure SQL connection |

#### Python Packages — Already Installed
```
streamlit==1.54.0
pyodbc
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

Install all at once:
```bash
pip install streamlit pyodbc sqlalchemy pandas msal openpyxl python-dotenv requests plotly Pillow numpy pytest faker
```

#### Not Installed on Laptop (Use Cloud Shell Instead)
| Tool | Why Not on Laptop | Alternative |
|------|-------------------|-------------|
| Azure CLI | Requires admin permission | Azure Cloud Shell |
| Docker Desktop | Requires admin permission | Azure Cloud Shell |

> **Note:** Azure CLI and Docker are pre-installed in Azure Cloud Shell (portal.azure.com).
> No admin permission needed. Use Cloud Shell for all deployment tasks.

#### To Install Later (When Ready to Deploy — Ask IT or Use Cloud Shell)
| Tool | Purpose |
|------|---------|
| Azure CLI | For running `az` commands locally |
| Docker Desktop | For building containers locally |

---

### Cloud Services (Azure) — To Be Created

| Service | Purpose | When to Create |
|---------|---------|----------------|
| Azure SQL Database (Basic tier ~$5/mo) | Budget submissions & approvals | Before first coding test |
| Microsoft Fabric Workspace | Lakehouse + Notebooks | Before SAP data loading |
| Microsoft Fabric Lakehouse | Actuals & reporting data | Before SAP data loading |
| Azure Entra ID App Registration | Auth & RLS | Before login feature |
| Azure Container Registry | Store Docker images | Before deployment |
| Azure Container Apps | Host Streamlit on cloud | Before go-live |
| Azure Storage Account | Cloud Shell file storage | Auto-created with Cloud Shell |

---

## Local Development Setup

### Step 1 — Clone the Repository
```bash
git clone https://github.com/tanasedw/budget_management_web.git
cd budget_management_web
```

### Step 2 — Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### Step 3 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Create Environment Variables File
Create a `.env` file in the project root (never commit this file):
```
# Azure SQL Database
SQL_SERVER=your-server.database.windows.net
SQL_DATABASE=db-budget-management
SQL_USERNAME=sqladmin
SQL_PASSWORD=your-password

# Azure Entra ID (App Registration)
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# Microsoft Graph API (Email notifications)
GRAPH_SENDER_EMAIL=sender@company.com

# Fabric
FABRIC_WORKSPACE_ID=your-workspace-id
FABRIC_NOTEBOOK_ID=your-notification-notebook-id
```

### Step 5 — Run Locally
```bash
streamlit run app.py
```
Open browser: `http://localhost:8501`

---

## Project Structure

```
budget_management_web/
│
├── app.py                          ← Main Streamlit entry point
│
├── pages/
│   ├── 01_submit_budget.py         ← User: fill and submit budget form
│   ├── 02_approve_vp.py            ← VP/AVP: approve/reject submissions
│   ├── 03_approve_staff.py         ← Nipapornt (Budget Staff): review
│   ├── 04_approve_manager.py       ← Warapornt (Budget Manager): final approve
│   ├── 05_dashboard.py             ← Dashboard: budget vs actuals
│   └── 06_admin.py                 ← Admin: manage users, upload budget
│
├── components/
│   ├── auth.py                     ← Azure Entra ID login logic
│   ├── sidebar.py                  ← Shared sidebar with user info
│   └── charts.py                   ← Reusable Plotly chart functions
│
├── database/
│   ├── connection.py               ← Azure SQL connection helper
│   ├── budget_queries.py           ← Budget submission CRUD
│   ├── approval_queries.py         ← Approval workflow queries
│   └── user_queries.py             ← User role & division queries
│
├── services/
│   ├── notification.py             ← Trigger Fabric Notebook for email
│   ├── excel_handler.py            ← Excel upload & download logic
│   └── fabric_connector.py         ← Read from Fabric Lakehouse
│
├── sql/
│   ├── create_tables.sql           ← SQL to create all tables
│   └── seed_data.sql               ← Test data for development
│
├── tests/
│   ├── test_budget.py              ← Unit tests for budget logic
│   └── test_approval.py            ← Unit tests for approval workflow
│
├── .env                            ← Secrets (never commit — in .gitignore)
├── .env.example                    ← Template for .env (commit this)
├── .gitignore
├── requirements.txt
├── Dockerfile                      ← For cloud deployment
└── README.md
```

---

## Database Setup

### Azure SQL Database — Tables

Run these SQL scripts in Azure Data Studio or Azure Portal Query Editor:

```sql
-- 1. User role and division mapping (RLS)
CREATE TABLE user_division_map (
    id              INT IDENTITY PRIMARY KEY,
    user_email      NVARCHAR(255) NOT NULL,
    display_name    NVARCHAR(255),
    division        NVARCHAR(255),
    department      NVARCHAR(255),
    cost_center     NVARCHAR(50),
    role            NVARCHAR(50),       -- user, vp, avp, budget_staff, budget_manager
    approver_email  NVARCHAR(255),
    is_active       BIT DEFAULT 1,
    created_at      DATETIME DEFAULT GETDATE()
);

-- 2. Budget submissions (user input)
CREATE TABLE budget_submissions (
    submission_id   NVARCHAR(50) PRIMARY KEY,
    fiscal_year     INT NOT NULL,
    cost_center     NVARCHAR(50),
    division        NVARCHAR(255),
    department      NVARCHAR(255),
    gl_account      NVARCHAR(20),
    gl_description  NVARCHAR(255),
    group_exp       NVARCHAR(100),
    template_type   NVARCHAR(50),       -- main, oversea_trip, lease_rental, fuel, prof_legal
    submitted_by    NVARCHAR(255),
    submitted_at    DATETIME,
    jan_amt DECIMAL(18,2) DEFAULT 0,    feb_amt DECIMAL(18,2) DEFAULT 0,
    mar_amt DECIMAL(18,2) DEFAULT 0,    apr_amt DECIMAL(18,2) DEFAULT 0,
    may_amt DECIMAL(18,2) DEFAULT 0,    jun_amt DECIMAL(18,2) DEFAULT 0,
    jul_amt DECIMAL(18,2) DEFAULT 0,    aug_amt DECIMAL(18,2) DEFAULT 0,
    sep_amt DECIMAL(18,2) DEFAULT 0,    oct_amt DECIMAL(18,2) DEFAULT 0,
    nov_amt DECIMAL(18,2) DEFAULT 0,    dec_amt DECIMAL(18,2) DEFAULT 0,
    total_annual    AS (jan_amt+feb_amt+mar_amt+apr_amt+may_amt+jun_amt+
                        jul_amt+aug_amt+sep_amt+oct_amt+nov_amt+dec_amt),
    remark          NVARCHAR(500)
);

-- 3. Approval status (current state)
CREATE TABLE approval_status (
    submission_id   NVARCHAR(50) PRIMARY KEY,
    current_status  NVARCHAR(50) DEFAULT 'DRAFT',
    -- DRAFT → PENDING_VP → PENDING_BUDGET_STAFF → PENDING_MANAGER → APPROVED
    -- REJECTED_BY_VP / REJECTED_BY_STAFF / REJECTED_BY_MANAGER
    vp_email        NVARCHAR(255),
    updated_at      DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (submission_id) REFERENCES budget_submissions(submission_id)
);

-- 4. Approval log (full history)
CREATE TABLE approval_log (
    log_id          INT IDENTITY PRIMARY KEY,
    submission_id   NVARCHAR(50),
    action          NVARCHAR(50),       -- submit, vp_approve, vp_reject, etc.
    action_by       NVARCHAR(255),
    action_at       DATETIME DEFAULT GETDATE(),
    comment         NVARCHAR(500),
    from_status     NVARCHAR(50),
    to_status       NVARCHAR(50),
    FOREIGN KEY (submission_id) REFERENCES budget_submissions(submission_id)
);
```

### Fabric Lakehouse — Tables (Delta format)

| Table | Source | Load Method |
|-------|--------|-------------|
| `accruals_data` | SAP export (Excel) — FAGLL03H | Fabric Notebook — monthly |
| `budget_master` | Board-approved Excel upload | Fabric Notebook — yearly |
| `combined_data` | Merge accruals + budget | Fabric Notebook — after each load |

### ตารางข้อมูล Accruals — Schema (26 คอลัม)

ข้อมูล G/L Line Items ระดับ transaction จาก SAP T-Code FAGLL03H ใช้เป็น Actuals สำหรับ Dashboard

| # | Column Name | Data Type | ตัวอย่าง |
|---|-------------|-----------|---------|
| 1 | Company Code | VARCHAR | `1000` |
| 2 | G/L Account | VARCHAR | `5120300020` |
| 3 | G/L Account: Long Text | VARCHAR | `Oil Expenses` |
| 4 | Posting Date | DATE | `2026-03-19` |
| 5 | Ledger | VARCHAR | `0L` |
| 6 | Company Code Currency Key | VARCHAR | `THB` |
| 7 | Company Code Currency Value | DECIMAL | `4480.10` |
| 8 | Cost Center | VARCHAR | `TKTRUCK` |
| 9 | Cost Center: Long Text | VARCHAR | `TK-Truck` |
| 10 | Profit Center | VARCHAR | `1000` |
| 11 | Assignment | VARCHAR | `TKTRUCK` |
| 12 | Document Number | VARCHAR | `5300016837` |
| 13 | Document type | VARCHAR | `WA` |
| 14 | Transaction Code | VARCHAR | `MB1A` |
| 15 | Entry Date | DATE | `2026-03-22` |
| 16 | Order: Short Text | VARCHAR | `99-5424/T12` |
| 17 | Text | VARCHAR | `Mileage : 304760 KM` |
| 18 | Order | VARCHAR | `OXXTK008` |
| 19 | Quantity | DECIMAL | `140` |
| 20 | Unit of Measure | VARCHAR | `L` |
| 21 | Purchasing Document | VARCHAR | *(blank)* |
| 22 | Invoice Reference | VARCHAR | `5300016837` |
| 23 | G/L Account (dup) | VARCHAR | `5120300020` |
| 24 | Fiscal Year | INT | `2026` |
| 25 | Object Class | VARCHAR | `Overhead` |
| 26 | Debit/Credit ind | CHAR(1) | `S` |

---

## Azure Cloud Setup

### Step 1 — Create Azure SQL Database
1. Azure Portal → Search `SQL databases` → Create
2. Server: create new → `sql-budget-server-[name]`
3. Auth: SQL authentication (`sqladmin` + strong password)
4. Tier: Basic (~$5/mo) for dev, Standard S1 for production
5. Networking: Allow Azure services + Add your IP

### Step 2 — Create Fabric Workspace & Lakehouse
1. app.fabric.microsoft.com → New Workspace → `ws-budget-management`
2. Inside workspace → New Lakehouse → `lh_budget`
3. Create Notebook → `nb_send_notification`

### Step 3 — Register App in Azure Entra ID
1. Azure Portal → Entra ID → App registrations → New registration
2. Name: `budget-app`
3. Copy: Tenant ID, Client ID
4. Create Client Secret → copy value
5. Add API permissions: `User.Read`, `Mail.Send`

### Step 4 — Create Azure Container Registry (before deployment)
```bash
# Run in Azure Cloud Shell
az acr create --name budgetappregistry --resource-group rg-budget --sku Basic
```

### Step 5 — Create Azure Container Apps (before deployment)
```bash
# Run in Azure Cloud Shell
az containerapp env create --name budget-env --resource-group rg-budget --location southeastasia
```

---

## Deployment

### Every time you deploy (run in Azure Cloud Shell):

```bash
# 1. Pull latest code from GitHub
git clone https://github.com/tanasedw/budget_management_web.git
cd budget_management_web

# 2. Build Docker image
docker build -t budgetappregistry.azurecr.io/budget-app:latest .

# 3. Push to Azure Container Registry
az acr login --name budgetappregistry
docker push budgetappregistry.azurecr.io/budget-app:latest

# 4. Deploy to Azure Container Apps
az containerapp update \
  --name budget-streamlit-app \
  --resource-group rg-budget \
  --image budgetappregistry.azurecr.io/budget-app:latest
```

---

## Workflow

### Budget Submission Cycle (Yearly)

```
Budget dept opens cycle
        │
        ▼
Users log in → fill budget form (by GL Account, by month)
  - Template 1.1: Main budget per GL Account — shows Budget & Actuals by business line (สายงาน)
    - Header: สายงาน + หน่วยงาน
    - Columns: GL Code | GL Name | Budget prior year | Normalized prior year | YTD Actuals | Monthly Actuals (Jan-Dec) | Budget next year total | Monthly Budget Input (Jan-Dec) ← user fills
    - GL Groups: Communication, Electricity & Water, Entertainment, Lease & Rental, Office Expenses, Other Admin, Other Manpower, Personal, Prof & Legal Fee, Repair & Maintenance, Travelling
    - GL items linked to sub-templates show note "(กรอกข้อมูลที่ชีท ...)" and auto-pull total from sub-sheet
  - Template 1.2: Detail for Oversea Trip / Lease&Rental / Fuel / Prof&Legal Fee
        │
        ▼
Submit → status: PENDING_VP
  → Email sent to VP/AVP of division
        │
        ▼
VP/AVP reviews → Approve or Reject + comment
  Approve → status: PENDING_BUDGET_STAFF → Email to Nipapornt
  Reject  → status: REJECTED_BY_VP      → Email to User (revise & resubmit)
        │
        ▼
Nipapornt reviews → Approve or Reject
  Approve → status: PENDING_MANAGER → Email to Warapornt
  Reject  → status: REJECTED_BY_STAFF → Email to User + VP/AVP
        │
        ▼
Warapornt final approval
  Approve → status: APPROVED → data written to Fabric Lakehouse
  Reject  → status: REJECTED_BY_MANAGER → Email to all
        │
        ▼
Budget dept uploads board-approved budget (Excel batch upload — Template 2 "งบประมาณกำหนดเอง")
        │
        ▼
Template 1.1 data + Template 2 data → merged into combined data file ("ไฟล์รวม Data")
        │
        ▼
Dashboard available: Budget vs Actuals by division / GL Account / month
```

### Actuals Data Update (Monthly)

```
SAP team exports from FAGLL03H
  - Company Code: 1000
  - Layout: /FORTEMPLATE
  - GL Accounts: per approved list
  - Exclude: Doc type CO, specific cost centers, Assignment TFRS16
        │
        ▼
Upload Excel to Fabric Lakehouse
        │
        ▼
Run Fabric Notebook to process + load actuals_data table
        │
        ▼
Dashboard auto-refreshes with new actuals
```

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| Login | Azure Entra ID SSO | To build |
| RLS | Data scoped by division | To build |
| Budget Form | Fill monthly budget per GL Account | To build |
| Sub-templates | Oversea Trip, Lease&Rental, Fuel, Prof&Legal | To build |
| Excel Upload | Batch budget upload by budget dept | To build |
| Excel Download | Export budget data | To build |
| Approval Workflow | 4-level approval chain | To build |
| Email Notification | Trigger via Fabric Notebook + Graph API | To build |
| Dashboard | Budget vs Actuals by division/month | To build |
| Admin Panel | Manage users, roles, budget cycle dates | To build |

---

## GL Account Groups

The system tracks these expense groups from SAP:
- Bank Charge
- Communication Expense
- Electricity & Water
- Employee Benefits
- Entertainment
- Insurance Premium
- Lease & Rental
- Maintenance - License for Software
- Office Expenses
- Other Admin Expenses
- Oversea Trip
- Professional & Legal Fee
- Fuel (ค่าน้ำมันเชื้อเพลิง)

SAP Company Code: **1000** | Layout: **/FORTEMPLATE**

---

## Email Notification Conditions

| Trigger | Recipient |
|---------|-----------|
| User submits budget | VP/AVP of user's division |
| VP/AVP approves | Nipapornt (Budget Staff) |
| VP/AVP rejects | User (to revise) |
| Nipapornt approves | Warapornt (Budget Manager) |
| Nipapornt rejects | User + VP/AVP |
| Warapornt approves | User (final confirmation) |
| Warapornt rejects | User + VP/AVP + Nipapornt |
| Deadline reminder | All users who have not submitted |

---

## Key Contacts

| Role | Name | Function |
|------|------|----------|
| Budget Staff | Nipapornt | 3rd level approval |
| Budget Manager | Warapornt | Final approval |

---

## Notes

- Budget data closure date: set per annual budget cycle calendar
- Actuals: no closure date — can re-pull any previously loaded month
- All monetary values in **THB**
- Fiscal year: January – December
