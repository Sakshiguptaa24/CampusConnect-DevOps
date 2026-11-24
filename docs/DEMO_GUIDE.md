# CampusConnect — Step-by-Step Demo Walkthrough

This guide walks through both student and administrator user journeys to showcase all implemented capabilities.

---

## 🏁 Step 1: Starting the Application

Ensure both services are running:
```powershell
.\scripts\start-dev.ps1
```
- Open your browser to: **[http://localhost:5173](http://localhost:5173)**

---

## 🎓 Journey 1: The Student Experience

### 1.1 Sign In as Student
1. Navigate to `/login`.
2. Click the blue **"🎓 Student Demo"** button to auto-fill:
   - **Email:** `student@campusconnect.com`
   - **Password:** `Student@123`
3. Click **"Sign In"**. You are redirected to your Student Dashboard.

### 1.2 Explore Campus Events
1. Click **"Discover Events"** in the top navigation bar (`/events`).
2. Type `"Hackathon"` or `"Summit"` in the search bar. Observe the live debounced filtering.
3. Click category chips: **Technology**, **Cultural**, **Sports**, **Workshop** to view filtered sets.
4. Note the visual capacity meters (e.g., green for seats available, amber for waitlist active).

### 1.3 Event Detail & Dynamic Waitlisting
1. Select **"Campus Hackathon 24H: HackTheFuture"** (`/events/2`).
   - Notice this event has reached capacity (2/2 seats filled).
   - The button automatically adapts to **"Join Priority Waitlist"**.
2. Click **"Join Priority Waitlist"**.
3. You are taken to the confirmation screen indicating:
   - `"Added to Priority Waitlist!"`
   - Real-time queue position display (`Waitlist #1`).

### 1.4 Viewing & Printing QR Ticket Passes
1. Click **"My Passes"** in the navigation header (`/my-registrations`).
2. Switch between tabs: **All Passes**, **Confirmed**, **Waitlisted**, **Attended**, **Cancelled**.
3. Under your confirmed pass (e.g. *AI & Cloud Tech Summit*), click **"View Pass"**.
4. You are presented with the high-resolution, print-ready ticket featuring:
   - Scannable QR code.
   - Event schedule & university venue.
   - Status badge ("VALID PASS").
   - Click **"Print Pass"** to trigger the browser's native print preview.

### 1.5 Testing Automated Waitlist Promotion
1. Under **"My Passes"**, find an event where you are confirmed.
2. Click **"Cancel"** and confirm cancellation in the dialog.
3. The seat is immediately released and the next person in line is promoted automatically!

---

## 🛡️ Journey 2: The Administrator Experience

### 2.1 Sign In as Administrator
1. Navigate to `/login`.
2. Click the purple **"🔑 Admin Demo"** button:
   - **Email:** `admin@campusconnect.com`
   - **Password:** `Admin@123`
3. Click **"Sign In"** -> Click **"Admin Portal"** (`/admin`).

### 2.2 Operations Dashboard & Analytics
1. View the 4 live KPI stats:
   - **Total Events**
   - **Total Registrations**
   - **Attendance Rate**
   - **Capacity Fill Rate**
2. Inspect the **Registration Velocity** area chart and **Category Breakdown** donut chart.

### 2.3 Creating a New Campus Event
1. Click **"Events Hub"** on the left sidebar (`/admin/events`).
2. Click **"Add New Event"**.
3. Enter:
   - **Title:** `Cloud Native & Kubernetes Boot Camp`
   - **Date:** Next month's date
   - **Time:** `10:00`
   - **Category:** `Technology`
   - **Capacity:** `50`
   - **Location:** `Tech Lab 4`
4. Click **"Create Event"**. The new event instantly appears in the roster and public discovery feed!

### 2.4 QR Gate Check-In & Anti-Fraud Terminal
1. Open **"Check-In & QR"** (`/admin/attendance`).
2. Paste a student's QR code token:
   - Example token from seeded student Alex: (You can copy this from any ticket pass URL `/ticket/<uuid>`).
3. Click **"Verify Pass"**:
   - **First Scan:** Green banner displays `"VERIFIED: ACCESS GRANTED"`. Ticket is marked as attended and added to the check-in stream.
   - **Second Scan with same code:** Red/amber banner displays `"DUPLICATE: ALREADY CHECKED IN"`. System prevents duplicate fraudulent gate entry!

### 2.5 Participant Management & CSV Export
1. Click **"Participants"** (`/admin/participants`).
2. Select any event from the top dropdown (e.g., *Annual Cultural Fest*).
3. Search for specific students by name or department.
4. Click **"Export CSV"**. The browser downloads an RFC 4180 compliant CSV file containing student names, emails, departments, registration status, and ticket tokens.

---

## 🔬 Journey 3: System Telemetry & Health Verification

1. Open **[http://localhost:8000/health](http://localhost:8000/health)** to verify application liveness.
2. Open **[http://localhost:8000/ready](http://localhost:8000/ready)** to verify active database connectivity.
3. Open **[http://localhost:8000/metrics](http://localhost:8000/metrics)** to view live Prometheus counters tracking request counts, error ratios, and average latency.
