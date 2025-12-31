"""Create DB tables and print status for debugging"""
from backend.app import create_app
import os
from backend.db import db

app = create_app()
print('APP DB URI', app.config.get('SQLALCHEMY_DATABASE_URI'))
print('Backend cwd:', os.getcwd())
pre = os.path.exists(os.path.join('backend', 'studenthub.db'))
print('Pre exists backend/studenthub.db:', pre)
with app.app_context():
    db.create_all()

# Run migration helper scripts to ensure local SQLite has expected columns
# (this is safe to run repeatedly; scripts check if columns exist first)
print('\nRunning DB helper scripts...')
import subprocess
import sys
try:
    subprocess.check_call([sys.executable, os.path.join('backend', 'scripts', 'add_course_fields.py')])
except subprocess.CalledProcessError:
    print('Warning: add_course_fields script failed. You may need to run it manually.')

post = os.path.exists(os.path.join('backend', 'studenthub.db'))
print('Post exists backend/studenthub.db:', post)
if post:
    print('size:', os.path.getsize(os.path.join('backend', 'studenthub.db')))
