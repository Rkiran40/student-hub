import sys, os
# Ensure repo root is on sys.path when running script directly
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
from backend.app import create_app
from backend.db import db
from backend.models import Profile

app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
client = app.test_client()

resp = client.post('/auth/signup', json={'email':'course@example.com','password':'password','full_name':'Course User','course_name':'CS','course_mode':'online','course_duration':'long'})
print('signup status', resp.status_code, resp.get_json())

with app.app_context():
    p = Profile.query.filter_by(email='course@example.com').first()
    print('before update status:', p.status)
    p.status = 'active'
    db.session.commit()
    p2 = Profile.query.filter_by(email='course@example.com').first()
    print('after update status:', p2.status)

login = client.post('/auth/login', json={'email':'course@example.com','password':'password'})
print('login status', login.status_code, login.get_json())
