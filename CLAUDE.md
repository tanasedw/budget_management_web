# CLAUDE.md — Budget Management Web Project Context

This file is auto-read by Claude at the start of every conversation in this folder.
Do NOT delete this file.

---

## Who I Am

- Developer: tanasedw (tanasedbsn@gmail.com)
- Background: Familiar with Microsoft Fabric / OneLake / Lakehouse — new to Azure SQL Database
- Working on: Internal budget management web app for the budget department

---

## Project Summary

Internal OPEX budget system replacing manual SAP exports and Excel consolidation.
Users fill budget by division → approval workflow → dashboard vs actuals.

**GitHub:** https://github.com/tanasedw/budget_management_web.git
**Working folder:** `c:\04.budget_management_web\`

---

## Tech Stack (Final Decisions)

| Layer | Tool | Notes |
|-------|------|-------|
| Web UI | Streamlit (Python) | Local dev → deploy to Azure Container Apps |
| Transactional DB | Azure SQL Database | Budget input, approvals, user roles |
| Analytical DB | Fabric Lakehouse (OneLake) | SAP actuals, reporting, dashboards |
| Authentication | Azure Entra ID | Login + RLS by division |
| Email Notifications | Fabric Notebook + Microsoft Graph API | No Power Automate |
| Deployment | Azure Container Apps | Via Azure Cloud Shell (no local Docker/CLI) |
| Version Control | GitHub | https://github.com/tanasedw/budget_management_web.git |

---

## Key Architecture Decisions (Why)

1. **Azure SQL + Lakehouse (not Lakehouse only)**
   - Azure SQL for transactional writes (budget input, approval updates) — simple CRUD
   - Lakehouse for bulk analytical reads (SAP actuals, dashboards)
   - Lakehouse alone is bad for frequent small row updates

2. **No Power Automate**
   - Email notifications via Fabric Notebook + Microsoft Graph API instead
   - Triggered by Fabric REST API call from Streamlit when approval status changes

3. **No local Docker/Azure CLI**
   - Machine does not have admin rights to install
   - Use Azure Cloud Shell (portal.azure.com) for all deployment commands
   - Docker and az CLI are pre-installed in Cloud Shell

4. **ODBC Driver 17 (not 18)**
   - Driver 17 already installed on developer machine
   - Use `ODBC Driver 17 for SQL Server` in all connection strings

---

## Developer Machine — What Is Installed

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.14.0 | Installed |
| Git | 2.52.0 | Installed |
| VS Code | latest | Installed |
| ODBC Driver 17 for SQL Server | - | Installed |
| Azure CLI | - | NOT installed (use Cloud Shell) |
| Docker Desktop | - | NOT installed (use Cloud Shell) |

### Python Packages Installed
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

---

## Azure SQL Database

- Connection uses `ODBC Driver 17 for SQL Server`
- Credentials stored in `.env` file (never committed to GitHub)
- Developer was new to Azure SQL — familiar with Fabric Lakehouse

### Tables
| Table | Purpose |
|-------|---------|
| `user_division_map` | User email → division → role → approver mapping |
| `budget_submissions` | Monthly budget input per GL Account per cost center |
| `approval_status` | Current approval state per submission |
| `approval_log` | Full history of every approval action |

### Approval Status Flow
```
DRAFT → PENDING_VP → PENDING_BUDGET_STAFF → PENDING_MANAGER → APPROVED
                ↘ REJECTED_BY_VP
                                       ↘ REJECTED_BY_STAFF
                                                            ↘ REJECTED_BY_MANAGER
```

---

## Approval Workflow

4-level chain (no skipping):
```
User → VP/AVP (of user's division) → Nipapornt (Budget Staff) → Warapornt (Budget Manager)
```

| Person | Role | Email variable |
|--------|------|----------------|
| Nipapornt | Budget Staff (3rd level) | `NIPAPORNT_EMAIL` in .env |
| Warapornt | Budget Manager (final) | `WARAPORNT_EMAIL` in .env |

---

## Email Notification Triggers

| Event | Notify |
|-------|--------|
| User submits | VP/AVP of division |
| VP approves | Nipapornt |
| VP rejects | User |
| Nipapornt approves | Warapornt |
| Nipapornt rejects | User + VP/AVP |
| Warapornt approves | User (final confirmation) |
| Warapornt rejects | User + VP/AVP + Nipapornt |
| Deadline reminder | All users who have not submitted |

---

## Data Sources

| Data | Source | How | Frequency |
|------|--------|-----|-----------|
| Actuals | SAP T-Code FAGLL03H | Excel export → upload to Lakehouse | Monthly |
| Budget (board approved) | Excel upload | Budget dept uploads via web | Yearly |
| Budget (user input) | Web form (this app) | Cell by cell per GL Account | Per budget cycle |

### SAP Export Settings
- Company Code: 1000
- Layout: /FORTEMPLATE
- Exclude: Doc type=CO, Cost Centers: 10SC012000/CMRY01/CMKK01/CMPB01/MNLB00-04/(Blanks)
- Exclude: Assignment=TFRS16

### GL Account Groups (13 groups, ~135 accounts)
Bank Charge, Communication Expense, Electricity & Water, Employee Benefits,
Entertainment, Insurance Premium, Lease & Rental, Maintenance-License for Software,
Office Expenses, Other Admin Expenses, Oversea Trip, Professional & Legal Fee, Fuel

---

## Budget Input Templates

| Template | Type | Who Fills |
|----------|------|-----------|
| 1.1 Main | Budget per GL Account per month | Each dept user |
| 1.2 Oversea Trip | Detail breakdown | Dept user |
| 1.2 Lease & Rental | Detail breakdown | Dept user |
| 1.2 Fuel (ค่าน้ำมัน) | Detail breakdown | Dept user |
| 1.2 Professional & Legal Fee | Detail breakdown | Dept user |
| 2. Budget dept template | Batch upload | Budget dept only |

---

## Streamlit Pages Plan

| Page | File | Role |
|------|------|------|
| Home / Login | `app.py` | All |
| Submit Budget | `pages/01_submit_budget.py` | User |
| VP Approval | `pages/02_approve_vp.py` | VP/AVP |
| Staff Approval | `pages/03_approve_staff.py` | Nipapornt |
| Manager Approval | `pages/04_approve_manager.py` | Warapornt |
| Dashboard | `pages/05_dashboard.py` | All |
| Admin Panel | `pages/06_admin.py` | Budget dept |

---

## Deployment Flow

```
1. Write code → VS Code (local)
2. Test locally → streamlit run app.py (localhost:8501)
3. Push code → git push → GitHub
4. Deploy → Azure Cloud Shell (portal.azure.com)
   git pull → docker build → docker push → az containerapp update
5. Users access → Azure Container Apps URL (browser)
```

---

## Current Progress

- [x] Requirements gathered from requirement_detail.xlsx
- [x] Architecture decided (SQL + Lakehouse + Streamlit + Entra ID)
- [x] Tech stack finalized
- [x] Developer machine fully set up (all Python packages installed)
- [x] GitHub repo created and connected
- [x] README.md written (full project manual)
- [x] CLAUDE.md created (this file)
- [ ] Virtual environment (venv) created
- [ ] requirements.txt created
- [ ] Project folder structure created
- [ ] Azure SQL Database created
- [ ] Database tables created
- [ ] Fabric Lakehouse created
- [ ] Azure Entra ID configured
- [ ] Streamlit pages built
- [ ] Approval workflow built
- [ ] Email notifications built
- [ ] Dashboard built
- [ ] Deployed to Azure Container Apps

---

## Next Steps (pick up from here)

1. Create `venv` and `requirements.txt`
2. Create full project folder structure
3. Create Azure SQL Database (Azure Portal)
4. Create `db_connection.py` and run table creation SQL
5. Start building `app.py` and first Streamlit page

---

## Important Notes for Claude

- Always use `ODBC Driver 17 for SQL Server` (not 18) in connection strings
- Do NOT suggest installing Docker or Azure CLI locally — no admin rights
- For deployment always use Azure Cloud Shell approach
- Developer is familiar with Fabric/Lakehouse — can use that as analogy when explaining SQL concepts
- All monetary values in THB
- Fiscal year: January – December
- This is an internal company tool — security and RLS by division are non-negotiable
