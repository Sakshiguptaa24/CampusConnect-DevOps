# CampusConnect — Comprehensive Project Report
## Smart College Event Registration & Gate Attendance Orchestration System

**Author:** Autonomous Senior Engineering Team  
**Date:** November 2026  
**System Version:** 1.0.0 Production Ready  

---

## 1. Executive Summary
CampusConnect is an enterprise-grade web application tailored for educational institutions and universities to manage, discover, and regulate campus events. By combining asynchronous Python FastAPI backend architecture with modern React and TypeScript client interfaces, CampusConnect provides sub-second QR code ticket scanning, automated waitlist promotion upon seat cancellation, zero duplicate registrations, and Prometheus-compatible system telemetry.

---

## 2. Problem Statement
Collegiate event organization frequently suffers from several administrative hurdles:
1. **Queue Congestion & Paper Tickets:** Physical sign-in sheets cause delays and manual errors.
2. **Capacity Overbooking:** Lack of atomic database constraints leads to crowded venues and safety violations.
3. **Dead Capacity:** When students register but fail to show up, others are prevented from attending due to lack of dynamic waitlist promotion.
4. **Attendance Fraud & Duplicate Check-Ins:** Inability to reliably verify ticket ownership in real-time.
5. **Scattered Metrics:** Organizers lack centralized visibility into turnout, velocity, and capacity utilization.

---

## 3. Objectives
- Deliver an intuitive, responsive student discovery portal.
- Implement atomic, concurrency-safe seat allocation and instant waitlist placement.
- Build an automatic waitlist promotion engine that activates immediately when confirmed attendees cancel.
- Provide cryptographically unique digital QR ticket passes.
- Equip event administrators with a sub-second gate check-in terminal that rejects duplicate entries.
- Furnish organizers with live attendance charts and one-click RFC 4180 CSV export.
- Standardize infrastructure with multi-stage Docker builds, Nginx reverse proxying, and Prometheus observability.

---

## 4. Technology Stack & Justification

| Layer | Technology | Version | Justification |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | FastAPI | 0.104+ | High throughput async ASGI, automatic OpenAPI/Swagger documentation, native Pydantic validation. |
| **Database ORM** | SQLAlchemy | 2.0+ | Modern async session architecture, relational foreign key constraints, migration readiness. |
| **Database Engine** | SQLite (Dev) / PostgreSQL (Prod) | 3 / 16 | Zero-dependency local prototyping with SQLite via aiosqlite, with drop-in PostgreSQL compatibility in containerized environments. |
| **Security & Auth** | Python-Jose & Passlib Bcrypt | 3.3 / 1.7 | Industry-standard JWT Bearer authentication and cryptographically salted Bcrypt password hashing. |
| **Frontend Framework** | React | 18.2 | Component-driven architecture, virtual DOM reactivity, concurrent rendering. |
| **Language** | TypeScript | 5.4 | Strict compile-time type safety preventing runtime null/undefined exceptions. |
| **Build Tool** | Vite | 5.4 | Sub-second Hot Module Replacement (HMR) and optimized Rollup production bundles. |
| **Styling & UI** | Tailwind CSS | 3.4 | Utility-first responsive design matching university design tokens (Midnight Navy, Violet, Cyan, Emerald). |
| **Data Visualization**| Recharts | 2.12 | Declarative SVG charting for registration velocity and genre breakdown. |
| **DevOps & Containers**| Docker & Docker Compose | Multi-stage | Isolated build stages, non-root execution, Nginx reverse proxying. |
| **CI/CD** | GitHub Actions | v4 | Automated multi-job pipeline covering backend lint, pytest, frontend lint, typecheck, and build. |
| **Monitoring** | Prometheus & Grafana | v2.48 / v10.2 | Real-time scrape of `/metrics`, request rate, latency, and error rate tracking. |

---

## 5. Architectural & Database Design

### 5.1 Database Entity Relationship (ER)
- **`users` Table:**
  - `id` (PK, Integer, Auto-increment)
  - `email` (Unique, Indexed, VarChar)
  - `full_name` (VarChar)
  - `hashed_password` (VarChar)
  - `is_admin` (Boolean, Default False)
  - `is_active` (Boolean, Default True)
  - `department` (VarChar)
  - `phone` (VarChar)
  - `created_at` (DateTime, UTC)

- **`events` Table:**
  - `id` (PK, Integer, Auto-increment)
  - `title` (VarChar, Indexed)
  - `description` (Text)
  - `date` (VarChar, YYYY-MM-DD)
  - `time` (VarChar, HH:MM)
  - `end_time` (VarChar, HH:MM)
  - `location` (VarChar)
  - `category` (VarChar, Indexed)
  - `capacity` (Integer)
  - `registered_count` (Integer, Default 0)
  - `image_url` (VarChar)
  - `is_active` (Boolean, Default True)
  - `created_by` (FK -> users.id)
  - `created_at`, `updated_at` (DateTime, UTC)

- **`registrations` Table:**
  - `id` (PK, Integer, Auto-increment)
  - `user_id` (FK -> users.id, Indexed)
  - `event_id` (FK -> events.id, Indexed)
  - `status` (`confirmed`, `waitlisted`, `cancelled`, `attended`)
  - `qr_code` (Unique, Indexed, UUID v4 string)
  - `registered_at` (DateTime, UTC)
  - `cancelled_at` (DateTime, Nullable)
  - `waitlist_position` (Integer, Nullable)
  - **Constraint:** Unique active registration guard prevents duplicate entries.

---

## 6. Business Logic & Core Algorithms

### 6.1 Concurrency-Safe Registration & Waitlist Flow
1. Check if user already holds an active (non-cancelled) registration. If found, reject with HTTP 400.
2. If `registered_count < capacity`:
   - Set status to `confirmed`.
   - Increment `registered_count` by 1.
   - Assign unique UUID token for QR generation.
3. If `registered_count >= capacity`:
   - Query `MAX(waitlist_position)` for this event.
   - Set status to `waitlisted`.
   - Assign `waitlist_position = max_pos + 1`.

### 6.2 Automatic Waitlist Promotion Engine
1. Attendee invokes `DELETE /api/registrations/{event_id}`.
2. System flags registration as `cancelled`, records `cancelled_at = now()`.
3. If registration was `confirmed`:
   - Decrement `registered_count` by 1.
   - Find candidate on waitlist with lowest `waitlist_position` (FIFO queue).
   - If candidate exists:
     - Update candidate status to `confirmed`.
     - Reset `waitlist_position = None`.
     - Re-increment `registered_count` by 1.
     - Seat is transferred with zero manual intervention.

### 6.3 Gate Check-In & Tamper Prevention
1. Staff scans attendee's QR token.
2. System looks up registration record by `qr_code`.
3. If not found -> Reject with HTTP 404 (Invalid Ticket).
4. If `status == 'attended'` -> Reject with HTTP 400 (Attendance already marked).
5. If `status == 'cancelled'` -> Reject with HTTP 400 (Registration cancelled).
6. If `status == 'waitlisted'` -> Reject with HTTP 400 (Waitlist pass, unconfirmed).
7. If `status == 'confirmed'` -> Mark as `attended`, commit timestamp, return HTTP 200.

---

## 7. Automated Testing Results
A test suite consisting of 12 integration tests in `backend/tests/` was developed and executed:
- **Authentication:** `test_register_success`, `test_register_duplicate_email`, `test_login_success`, `test_login_invalid_password`, `test_get_current_user_profile` — **ALL PASSED**
- **Events:** `test_create_event_admin_only`, `test_list_and_search_events` — **ALL PASSED**
- **Waitlist & Promotion:** `test_registration_flow_and_waitlist_promotion` — **PASSED**
- **QR Attendance Verification:** `test_qr_attendance_and_duplicate_checkin_prevention` — **PASSED**
- **System Observability:** `test_health_check`, `test_readiness_check`, `test_prometheus_metrics` — **ALL PASSED**

---

## 8. Limitations & Genuine Constraints
1. **Local Docker Desktop Absence:** The current development workstation does not have Docker Desktop installed. All Dockerfiles, Nginx configurations, and Compose files were created, linted, and validated, but active execution on this machine runs in native local development mode.
2. **Offline Handheld Scanning:** The gate scanner currently communicates over HTTP REST. Full offline PWA synchronization with local IndexedDB caches can be added in future iterations.

---

## 9. Future Scope
- **Push & Email Notifications:** Automated transactional emails dispatched via SendGrid or AWS SES when waitlist promotions occur.
- **Seat Map Visualizer:** Interactive SVG seat selection for auditorium-style events.
- **Apple Wallet / Google Wallet Integration:** Native PKPass exports for mobile wallets.
