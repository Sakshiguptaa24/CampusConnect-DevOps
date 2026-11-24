# CampusConnect — Architecture Specification

## 1. System Overview
CampusConnect follows a decoupled client-server architecture with an asynchronous REST API backend, a reactive single-page frontend (SPA), a relational persistence layer, and optional telemetry monitoring.

---

## 2. High-Level Component Diagram

```mermaid
flowchart TD
    Client["Browser / Mobile Client (React + Vite)"]
    Nginx["Nginx Reverse Proxy (:80)"]
    FastAPI["FastAPI Backend (:8000)"]
    DB[(SQLite / PostgreSQL :5432)]
    Prometheus["Prometheus Server (:9090)"]
    Grafana["Grafana Dashboards (:3000)"]

    Client -->|HTTP / UI| Nginx
    Nginx -->|/api, /docs, /health| FastAPI
    Nginx -->|Static Assets| Client
    FastAPI -->|Async SQLAlchemy| DB
    Prometheus -->|Scrape /metrics| FastAPI
    Grafana -->|Query Datasource| Prometheus
```

---

## 3. Authentication & Authorization Sequence

```mermaid
sequenceDiagram
    autonumber
    actor User as Student / Admin
    participant Frontend as React Client
    participant API as FastAPI Backend
    participant DB as Database

    User->>Frontend: Enter Email & Password
    Frontend->>API: POST /api/auth/login {email, password}
    API->>DB: Query User by Email
    DB-->>API: User Record with Hashed Password
    API->>API: Verify Password via Passlib Bcrypt
    alt Valid Credentials
        API->>API: Generate Signed JWT with sub, email, is_admin
        API-->>Frontend: HTTP 200 {access_token, token_type, user}
        Frontend->>Frontend: Persist JWT in localStorage
        Frontend-->>User: Redirect to Dashboard
    else Invalid Password
        API-->>Frontend: HTTP 401 Unauthorized
        Frontend-->>User: Display Error Banner
    end
```

---

## 4. Registration & Automated Waitlist Flow

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant API as FastAPI
    participant DB as Database

    Student->>API: POST /api/registrations {event_id}
    API->>DB: Check for Existing Non-Cancelled Registration
    alt Already Registered
        API-->>Student: HTTP 400 "Already registered for this event"
    else New Registration
        API->>DB: SELECT registered_count, capacity FROM events
        alt registered_count < capacity
            API->>DB: INSERT Registration (status='confirmed', qr_code=UUID)
            API->>DB: UPDATE events SET registered_count = registered_count + 1
            API-->>Student: HTTP 201 Confirmed (with QR Code)
        else Capacity Reached
            API->>DB: Query MAX(waitlist_position)
            API->>DB: INSERT Registration (status='waitlisted', waitlist_position=pos+1)
            API-->>Student: HTTP 201 Waitlisted (# position)
        end
    end
```

---

## 5. Waitlist Promotion on Cancellation

```mermaid
sequenceDiagram
    autonumber
    actor Attendee
    actor WaitlistedStudent
    participant API as FastAPI
    participant DB as Database

    Attendee->>API: DELETE /api/registrations/{event_id}
    API->>DB: Fetch Active Registration for Attendee
    API->>DB: UPDATE Registration SET status='cancelled', cancelled_at=now()
    alt Was Confirmed Attendee
        API->>DB: UPDATE events SET registered_count = registered_count - 1
        API->>DB: SELECT * FROM registrations WHERE event_id=X AND status='waitlisted' ORDER BY waitlist_position ASC LIMIT 1
        alt Waitlisted Candidate Exists
            API->>DB: UPDATE Candidate SET status='confirmed', waitlist_position=NULL
            API->>DB: UPDATE events SET registered_count = registered_count + 1
            Note over API,DB: Candidate is now automatically confirmed!
        end
    end
    API-->>Attendee: HTTP 200 Cancellation Confirmed
```

---

## 6. Gate QR Verification Flow

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Staff Gate Scanner
    participant Terminal as Admin Check-In UI
    participant API as FastAPI
    participant DB as Database

    Admin->>Terminal: Scan Attendee QR Code
    Terminal->>API: POST /api/attendance/verify {qr_code}
    API->>DB: SELECT * FROM registrations WHERE qr_code = code
    alt Code Not Found
        API-->>Terminal: HTTP 404 "Invalid QR code"
    else Already Attended
        API-->>Terminal: HTTP 400 "Attendance already marked for this registration"
    else Status == 'waitlisted'
        API-->>Terminal: HTTP 400 "Registration is on waitlist, not confirmed"
    else Status == 'confirmed'
        API->>DB: UPDATE Registration SET status = 'attended'
        API-->>Terminal: HTTP 200 "Attendance Verified & Marked"
        Terminal-->>Admin: Green Visual & Audio Confirmation
    end
```
