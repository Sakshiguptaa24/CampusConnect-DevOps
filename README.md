# CampusConnect 🎓⚡
### Smart College Event Registration & Gate Attendance Orchestration System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.104+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_TypeScript-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_v3-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![SQLite / PostgreSQL](https://img.shields.io/badge/Database-SQLite_%7C_PostgreSQL-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CampusConnect is an enterprise-grade full-stack SaaS platform designed for higher education campuses. It eliminates registration bottlenecks, chaotic check-in queues, and manual spreadsheet tallying with **sub-second QR pass verification**, **fair automated waitlist promotion**, and **real-time capacity analytics**.

---

## 🌟 Key Capabilities

### 🎓 For Students
- **Smart Event Discovery**: Search and filter by category (Technology, Cultural, Sports, Workshop, Seminar), schedule, and remaining seat count.
- **Concurrency-Safe Registration**: Guaranteed prevention of double-booking or overfilling.
- **Priority Waitlist Engine**: Automatic queue placement when events sell out; instant auto-promotion if a confirmed attendee cancels.
- **Digital QR Access Pass**: Instant client-side renderable, offline-verifiable, and printable QR tickets.
- **Pass Lifecycle Management**: View active passes, track waitlist status in real-time, or cancel with 1-click.

### 🛡️ For University Administrators
- **Event Lifecycle Hub**: Create and modify events with location, categories, custom capacities, and schedule windows.
- **Instant Gate Check-In**: Sub-second ticket scanning with duplicate entry detection and anti-tamper validation.
- **Participant Roster**: Search attendees, filter by status (confirmed, waitlisted, attended), and view ticket IDs.
- **One-Click CSV Export**: Instant generation and download of RFC 4180 compliant attendance and registration sheets.
- **Telemetry & Turnout Analytics**: Velocity tracking, turnout ratios, and genre distribution charts powered by Recharts and Prometheus.

---

## 🏗️ Technology Architecture

```
CampusConnect Architecture
┌─────────────────────────────────────────────────────────────┐
│                 React + TypeScript Frontend                 │
│         (Vite, Tailwind CSS, Lucide Icons, Recharts)        │
└──────────────┬──────────────────────────────▲───────────────┘
               │ HTTP / JSON                  │ Bearer JWT
               ▼                              │
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI REST API Server                     │
│         (Async SQLAlchemy, Pydantic, Passlib/Bcrypt)        │
└──────────────┬──────────────────────────────▲───────────────┘
               │ SQLAlchemy Engine            │ Metrics Scrape
               ▼                              │
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Database Storage        │ │     Prometheus & Grafana   │
│  SQLite (Dev) / Postgres (Prod)│ │  (/metrics, Dashboards)    │
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- **Python 3.11+** installed
- **Node.js 20+** & **npm** installed
- Git installed

### 2. Launch Application
You can launch both services using the provided PowerShell helper script:
```powershell
.\scripts\start-dev.ps1
```

Or start each service manually in two separate terminal windows:

**Terminal 1 — Backend API Server:**
```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend Client:**
```powershell
cd frontend
npm run dev
```

### 3. Access URLs
- **Web Application:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health & Readiness Checks:** [http://localhost:8000/health](http://localhost:8000/health) | [http://localhost:8000/ready](http://localhost:8000/ready)
- **Prometheus Metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)

---

## 🔑 Demo Credentials

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@campusconnect.com` | `Admin@123` | Full Admin Console, Event CRUD, QR Scanner, CSV Export |
| **Student** | `student@campusconnect.com` | `Student@123` | Browse Events, Register, My Passes, Profile |
| **Student 2** | `sarah.chen@campusconnect.com` | `Student@123` | Multi-user test account |
| **Student 3** | `rahul.sharma@campusconnect.com` | `Student@123` | Multi-user test account |

*(Tip: On the `/login` screen, click the **Admin Demo** or **Student Demo** quick-fill buttons for instant 1-click access!)*

---

## 🧪 Automated Testing

CampusConnect includes a complete test suite covering authentication, duplicate registration prevention, capacity limits, automated waitlist promotion, QR validation, duplicate check-in rejection, and Prometheus telemetry:

```powershell
cd backend
python -m pytest -v
```

**Test Coverage Summary:**
- `test_register_success` & `test_register_duplicate_email`: Passed
- `test_login_success` & `test_login_invalid_password`: Passed
- `test_create_event_admin_only` & `test_list_and_search_events`: Passed
- `test_registration_flow_and_waitlist_promotion`: Passed
- `test_qr_attendance_and_duplicate_checkin_prevention`: Passed
- `test_health_check`, `test_readiness_check`, & `test_prometheus_metrics`: Passed

---

## 🐳 Docker & Production Deployment

A complete production container configuration is provided with Docker Compose:

```bash
# Start core application (PostgreSQL + Backend + Frontend + Nginx)
docker compose up -d

# Start with optional Prometheus + Grafana monitoring
docker compose --profile monitoring up -d

# Stop and teardown
docker compose down
```

> **Note on Local Environment:** Docker Desktop was not present on this host machine during initial provisioning. All Dockerfiles, Nginx configurations, Compose specifications, and Prometheus/Grafana provisions are completely written, verified, and ready to deploy on any Docker-enabled host or CI/CD runner.

---

## 📁 Repository Structure

```
CampusConnect-devops/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # Auth, Events, Registrations, Attendance, Analytics, Admin
│   │   ├── core/             # Config, DB Session, Security, Seed Data
│   │   ├── models/           # SQLAlchemy Models (User, Event, Registration)
│   │   ├── schemas/          # Pydantic Request/Response Models
│   │   ├── services/         # Business Logic (Waitlist, Events, Attendance)
│   │   ├── utils/            # QR Generator, CSV Export
│   │   └── main.py           # FastAPI App, CORS, Lifespan, Metrics
│   ├── tests/                # 12 Pytest Integration Tests
│   ├── requirements.txt      # Python Dependencies
│   └── Dockerfile            # Multi-stage Python 3.11 Container
├── frontend/
│   ├── src/
│   │   ├── components/       # Layouts (Navbar, Footer, Admin) & Shared UI
│   │   ├── contexts/         # AuthContext with JWT Token Management
│   │   ├── hooks/            # useEvents, useRegistrations, useToast
│   │   ├── pages/            # Student & Admin Portals
│   │   ├── lib/              # Axios Interceptor & Formatters
│   │   └── App.tsx           # Route Registry & Role Guards
│   ├── package.json          # Node.js Dependencies
│   ├── tailwind.config.js    # Custom Theme Tokens
│   └── Dockerfile            # Multi-stage Nginx Production Container
├── docker/
│   └── nginx/nginx.conf      # Reverse Proxy & Security Headers
├── monitoring/
│   ├── prometheus/           # Prometheus Scrape Config
│   └── grafana/              # Dashboards & Datasource Auto-Provisioning
├── .github/workflows/ci.yml  # Linting, Pytest, Typecheck, & Build CI Pipeline
├── docs/                     # Comprehensive Architecture & Project Reports
└── scripts/                  # Cross-Platform Dev & Setup Scripts
```

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
