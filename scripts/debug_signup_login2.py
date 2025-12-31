import sys, os
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from backend.app import create_app
from backend.db import db
from backend.models import Profile

app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})

with app.app_context():
    db.drop_all()
    db.create_all()

client = app.test_client()

email = 'course@example.com'
payload = {
    'email': email,
    'password': 'password',
    'full_name': 'Course User',
    'course_name': 'Computer Science',
    'course_mode': 'online',
    'course_duration': 'long'
}

resp = client.post('/auth/signup', json=payload)
print('signup', resp.status_code, resp.get_json())

with app.app_context():
    profile = Profile.query.filter_by(email=email).first()
    print('profile before:', profile.status)
    profile.status = 'active'
    db.session.commit()
    profile2 = Profile.query.filter_by(email=email).first()
    print('profile after:', profile2.status)

login_resp = client.post('/auth/login', json={'email': email, 'password': 'password'})
print('login', login_resp.status_code, login_resp.get_json())
