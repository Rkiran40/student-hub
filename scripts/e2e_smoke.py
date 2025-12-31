"""A simple end-to-end smoke test that covers signup -> admin approve -> student login.
Usage:
  ADMIN_EMAIL=admin@local ADMIN_PASSWORD=adminpass python scripts/e2e_smoke.py
"""
import os
import requests
import time
import uuid

BACKEND = os.environ.get('BACKEND_URL', 'http://localhost:5001')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@local')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'adminpass')

print('Starting E2E smoke test against', BACKEND)

# 1) signup
email = f'smoke_{uuid.uuid4().hex[:8]}@example.com'
password = 'password123'
print('Signing up', email)
r = requests.post(f'{BACKEND}/auth/signup', json={'email': email, 'password': password, 'full_name': 'Smoke Tester'})
if r.status_code != 200:
    print('Signup failed:', r.status_code, r.text)
    raise SystemExit(2)
print('Signup response:', r.json())

# 2) admin login
print('Logging in as admin', ADMIN_EMAIL)
r = requests.post(f'{BACKEND}/auth/login', json={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD})
if r.status_code != 200:
    print('Admin login failed:', r.status_code, r.text)
    raise SystemExit(2)
admin_tokens = r.json()
access = admin_tokens['access_token']
headers = {'Authorization': f'Bearer {access}'}

# 3) find profile and approve
print('Fetching students list')
r = requests.get(f'{BACKEND}/admin/students', headers=headers)
if r.status_code != 200:
    print('Failed to fetch students:', r.status_code, r.text)
    raise SystemExit(2)
profiles = r.json()
profile = next((p for p in profiles if p.get('email') == email), None)
if not profile:
    print('Profile not found in students list; will wait a bit and retry')
    for i in range(5):
        time.sleep(1)
        r = requests.get(f'{BACKEND}/admin/students', headers=headers)
        profiles = r.json() if r.ok else []
        profile = next((p for p in profiles if p.get('email') == email), None)
        if profile:
            break

if not profile:
    print('Failed to find newly created profile after retries')
    raise SystemExit(2)

profile_id = profile['id']
username = f'user_{uuid.uuid4().hex[:6]}'
print('Approving user', profile_id, 'with username', username)
r = requests.post(f'{BACKEND}/admin/students/{profile_id}/approve', json={'username': username}, headers=headers)
if r.status_code != 200:
    print('Failed to approve student:', r.status_code, r.text)
    raise SystemExit(2)
print('Approve response:', r.json())

# 4) login as the new user
print('Attempting login as new user')
r = requests.post(f'{BACKEND}/auth/login', json={'username': username, 'password': password})
if r.status_code != 200:
    print('User login failed:', r.status_code, r.text)
    raise SystemExit(2)
print('User login success:', r.json())
print('E2E smoke test passed!')
