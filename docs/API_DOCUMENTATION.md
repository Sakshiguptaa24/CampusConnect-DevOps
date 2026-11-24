# CampusConnect — REST API Documentation

**Base URL:** `http://localhost:8000/api`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**ReDoc Reference:** `http://localhost:8000/redoc`  
**Authentication Scheme:** `Bearer <JWT_TOKEN>` via HTTP `Authorization` Header  

---

## 1. System Endpoints

### `GET /health`
Liveness probe checking basic service uptime.
- **Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-11-24T12:00:00Z",
  "service": "CampusConnect API",
  "version": "1.0.0",
  "uptime_seconds": 124.5
}
```

### `GET /ready`
Readiness probe verifying active database connectivity.
- **Response (200 OK):**
```json
{
  "status": "ready",
  "timestamp": "2026-11-24T12:00:00Z",
  "checks": {
    "database": "ok",
    "application": "ok"
  }
}
```

### `GET /metrics`
Prometheus metrics format containing request counts, latencies, and error codes.
- **Response (200 OK):** `text/plain; version=0.0.4`

---

## 2. Authentication (`/api/auth`)

### `POST /api/auth/register`
Creates a new student user.
- **Body:**
```json
{
  "email": "student@campusconnect.com",
  "password": "Student@123",
  "full_name": "Alex Johnson",
  "department": "Computer Science",
  "phone": "+1 555-0101"
}
```
- **Response (201 Created):**
```json
{
  "id": 2,
  "email": "student@campusconnect.com",
  "full_name": "Alex Johnson",
  "is_admin": false,
  "is_active": true,
  "department": "Computer Science",
  "phone": "+1 555-0101",
  "created_at": "2026-11-24T12:00:00Z"
}
```

### `POST /api/auth/login`
Authenticates credentials and issues signed JWT bearer token.
- **Body:**
```json
{
  "email": "student@campusconnect.com",
  "password": "Student@123"
}
```
- **Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "student@campusconnect.com",
    "full_name": "Alex Johnson",
    "is_admin": false
  }
}
```

### `GET /api/auth/me`
Retrieves current authenticated user's profile.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** User object.

### `PUT /api/auth/me`
Updates profile information (full name, department, phone).
- **Headers:** `Authorization: Bearer <token>`
- **Body:** `{ "full_name": "Alex J.", "department": "IT", "phone": "+1 555-0199" }`

---

## 3. Events (`/api/events`)

### `GET /api/events`
Public event catalog with search, filter, and pagination.
- **Query Params:**
  - `page`: default `1`
  - `page_size`: default `10`
  - `search`: title or keyword search
  - `category`: Technology, Cultural, Sports, Workshop, Seminar
- **Response (200 OK):**
```json
{
  "events": [
    {
      "id": 1,
      "title": "AI & Cloud Tech Summit 2026",
      "description": "Explore cutting-edge advancements...",
      "date": "2026-11-29",
      "time": "09:30",
      "end_time": "17:00",
      "location": "Main Auditorium",
      "category": "Technology",
      "capacity": 50,
      "registered_count": 3,
      "image_url": "https://...",
      "is_active": true
    }
  ],
  "total": 8,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### `GET /api/events/{event_id}`
Retrieves single event details by ID.
- **Response (200 OK):** Event object.

### `POST /api/events` *(Admin Only)*
Creates a new event.
- **Headers:** `Authorization: Bearer <admin_token>`
- **Body:** Event creation payload.
- **Response (201 Created):** Created Event object.

### `PUT /api/events/{event_id}` *(Admin Only)*
Modifies an existing event.

### `DELETE /api/events/{event_id}` *(Admin Only)*
Deletes an event and its registrations.

---

## 4. Registrations & Waitlist (`/api/registrations`)

### `POST /api/registrations`
Registers authenticated user for an event (or enters waitlist if full).
- **Headers:** `Authorization: Bearer <token>`
- **Body:** `{ "event_id": 1 }`
- **Response (201 Created):**
```json
{
  "id": 10,
  "user_id": 2,
  "event_id": 1,
  "status": "confirmed",
  "qr_code": "4f11617f-217a-4227-9ac2-a9cd2fad9f25",
  "registered_at": "2026-11-24T12:00:00Z",
  "waitlist_position": null
}
```

### `DELETE /api/registrations/{event_id}`
Cancels an existing registration and triggers automated waitlist promotion.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** Cancelled Registration object.

### `GET /api/registrations/my`
Retrieves all event registrations for current student.
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):** List of registration objects with event title, date, time, and QR token.

### `GET /api/registrations/events/{event_id}/participants` *(Admin Only)*
Retrieves all participants for an event with user details.

---

## 5. Gate Attendance & Verification (`/api/attendance`)

### `POST /api/attendance/verify` *(Admin Only)*
Verifies QR ticket and records attendance.
- **Headers:** `Authorization: Bearer <admin_token>`
- **Body:** `{ "qr_code": "4f11617f-217a-4227-9ac2-a9cd2fad9f25" }`
- **Response (200 OK):**
```json
{
  "registration_id": 10,
  "status": "attended",
  "event_id": 1
}
```
- **Error Responses:**
  - `400 Bad Request`: "Attendance already marked for this registration"
  - `400 Bad Request`: "Registration is on waitlist, not confirmed"
  - `404 Not Found`: "Invalid QR code"

### `GET /api/attendance/verify/{qr_code}`
Public lookup of ticket validity by QR code string.

### `GET /api/attendance/stats/{event_id}` *(Admin Only)*
Returns attendance counts and show-up percentage for an event.

---

## 6. Admin & Reporting (`/api/admin`)

### `GET /api/admin/events/{event_id}/export-csv` *(Admin Only)*
Exports RFC 4180 compliant CSV of all registrations for an event.
- **Headers:** `Authorization: Bearer <admin_token>`
- **Response (200 OK):** `text/csv` attachment.

### `GET /api/analytics/dashboard` *(Admin Only)*
Aggregated university dashboard metrics (total events, registrations, turnout rate, utilization).

### `GET /api/analytics/trends` *(Admin Only)*
Registration volume velocity over time.

### `GET /api/analytics/categories` *(Admin Only)*
Event distribution breakdown by category.
