import urllib.request
import urllib.error
import json
import sys

BASE = 'http://127.0.0.1:8000'

def request(method, path, data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req_body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(f'{BASE}{path}', data=req_body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read()
            content_type = resp.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return resp.status, json.loads(content.decode('utf-8'))
            return resp.status, content.decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, err_body

print("========================================")
print("CAMPUSCONNECT RELEASE AUDIT VERIFICATION")
print("========================================")

# 1. Student Login
status, data = request('POST', '/api/auth/login', {'email': 'student@campusconnect.com', 'password': 'Student@123'})
assert status == 200, f'Student login failed: {status} {data}'
student_token = data['access_token']
role = 'admin' if data['user']['is_admin'] else 'student'
print(f"[PASS] 1. Student Login: {data['user']['email']} | role: {role}")

# 2. Admin Login
status, data = request('POST', '/api/auth/login', {'email': 'admin@campusconnect.com', 'password': 'Admin@123'})
assert status == 200, f'Admin login failed: {status} {data}'
admin_token = data['access_token']
role = 'admin' if data['user']['is_admin'] else 'student'
print(f"[PASS] 2. Admin Login: {data['user']['email']} | role: {role}")

# 3. Event Browsing
status, data = request('GET', '/api/events')
assert status == 200, f'Event browsing failed: {status}'
assert len(data['events']) > 0, 'No events returned'
print(f"[PASS] 3. Event Browsing: {data['total']} events available (First: \"{data['events'][0]['title']}\")")

# 4. Admin Event Creation (Capacity = 1 to test waitlist promotion)
new_event = {
    'title': 'Autonomous Release Verification Workshop',
    'description': 'Testing complete lifecycle under release audit',
    'date': '2026-12-01',
    'time': '10:00 AM',
    'end_time': '12:00 PM',
    'location': 'Auditorium Hall B',
    'category': 'technology',
    'capacity': 1,
    'image_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800'
}
status, event = request('POST', '/api/events', new_event, token=admin_token)
assert status == 201, f'Admin event creation failed: {status} {event}'
event_id = event['id']
print(f"[PASS] 4. Admin Event Creation: ID {event_id}, Title: \"{event['title']}\", Capacity: {event['capacity']}")

# 5. Student 1 Registration (Capacity 1/1 -> Confirmed)
status, reg1 = request('POST', '/api/registrations', {'event_id': event_id}, token=student_token)
assert status == 201, f'Student 1 registration failed: {status} {reg1}'
assert reg1['status'] == 'confirmed', f"Expected confirmed, got {reg1['status']}"
print(f"[PASS] 5. Event Registration: Reg ID {reg1['id']}, Status: {reg1['status']}")

# 6. QR Ticket Generation
status, qr_res = request('GET', f"/api/registrations/{reg1['id']}/qr", token=student_token)
assert status == 200, f'QR ticket generation failed: {status} {qr_res}'
assert 'qr_image' in qr_res and qr_res['qr_image'].startswith('data:image/png;base64,'), 'Invalid QR image'
qr_code_1 = qr_res['qr_code']
print(f"[PASS] 6. QR Ticket Generation: QR token {qr_code_1[:16]}... with image data URI ({len(qr_res['qr_image'])} bytes)")

# 7. Student 2 Registration (Capacity 1/1 full -> Waitlisted)
request('POST', '/api/auth/register', {
    'email': 'waitlist_tester@campusconnect.com',
    'password': 'Password@123',
    'full_name': 'Waitlist Tester',
    'phone': '555-0199',
    'department': 'Computer Science'
})
status, lgn = request('POST', '/api/auth/login', {'email': 'waitlist_tester@campusconnect.com', 'password': 'Password@123'})
assert status == 200, f'Student 2 login failed: {status} {lgn}'
student2_token = lgn['access_token']

status, reg2 = request('POST', '/api/registrations', {'event_id': event_id}, token=student2_token)
assert status == 201, f'Student 2 registration failed: {status} {reg2}'
assert reg2['status'] == 'waitlisted', f"Expected waitlisted, got {reg2['status']}"
print(f"[PASS] 7. Automatic Waitlist: Reg ID {reg2['id']}, Status: {reg2['status']}")

# 8. Registration Cancellation (Student 1 cancels)
status, cancel_res = request('DELETE', f'/api/registrations/{event_id}', token=student_token)
assert status == 200, f'Cancellation failed: {status} {cancel_res}'
assert cancel_res['status'] == 'cancelled', f"Expected cancelled, got {cancel_res['status']}"
print(f"[PASS] 8. Registration Cancellation: Reg ID {reg1['id']} cancelled successfully")

# 9. Waitlist Promotion Verification (Student 2 should be promoted)
status, my_regs = request('GET', '/api/registrations/my', token=student2_token)
assert status == 200, f'Get my registrations failed: {status} {my_regs}'
reg2_updated = next(r for r in my_regs if r['event_id'] == event_id)
assert reg2_updated['status'] == 'confirmed', f"Expected promoted to confirmed, got {reg2_updated['status']}"
print(f"[PASS] 9. Automatic Waitlist Promotion: Reg ID {reg2['id']} promoted to status: {reg2_updated['status']}")

# 10. Attendance Verification (Admin scans promoted Student 2 QR ticket)
status, qr2_res = request('GET', f"/api/registrations/{reg2['id']}/qr", token=student2_token)
qr_code_2 = qr2_res['qr_code']
status, attend_res = request('POST', '/api/attendance/verify', {'qr_code': qr_code_2}, token=admin_token)
assert status == 200, f'Attendance check-in failed: {status} {attend_res}'
assert attend_res['valid'] is True, f'Expected valid check-in, got {attend_res}'
assert attend_res['status'] == 'attended', f"Expected attended, got {attend_res['status']}"
print(f"[PASS] 10. Attendance Verification: Checked in {attend_res['student']['name']} for \"{attend_res['event']['title']}\"")

# 11. Duplicate Check-In Prevention (Rescan same ticket)
status, dup_res = request('POST', '/api/attendance/verify', {'qr_code': qr_code_2}, token=admin_token)
assert status == 400, f'Duplicate check-in should return 400, got {status} {dup_res}'
assert 'already marked' in str(dup_res), f'Expected already marked error, got {dup_res}'
print(f"[PASS] 11. Duplicate Check-in Prevention: Rejected with HTTP 400: \"{dup_res['detail']}\"")

# 12. CSV Export
status, csv_data = request('GET', f'/api/admin/events/{event_id}/export-csv', token=admin_token)
assert status == 200, f'CSV export failed: {status} {csv_data}'
assert 'Registration ID' in csv_data and 'Waitlist Tester' in csv_data, f'CSV data incomplete: {csv_data[:200]}'
print(f"[PASS] 12. CSV Export: Successfully generated CSV ({len(csv_data)} bytes)")
print("--- CSV Header & Sample Row ---")
for line in csv_data.strip().split('\n')[:3]:
    print('   ', line)

print("========================================")
print("ALL 12 PRODUCTION-READINESS TESTS PASSED!")
print("========================================")
