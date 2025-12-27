from .db import db
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='student')  # student or admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete')
    uploads = db.relationship('DailyUpload', backref='user', cascade='all, delete')

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String, unique=True, nullable=True)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String, nullable=True)
    college_name = db.Column(db.String, nullable=True)
    college_id = db.Column(db.String, nullable=True)  # Keep for backward compatibility
    city = db.Column(db.String, nullable=True)
    pincode = db.Column(db.String, nullable=True)
    college_email = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='pending')
    avatar_url = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyUpload(db.Model):
    __tablename__ = 'daily_uploads'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String, nullable=False)
    file_type = db.Column(db.String, nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String, nullable=True)
    status = db.Column(db.String, default='pending')
    admin_feedback = db.Column(db.String, nullable=True)
    reviewed_by = db.Column(db.String, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
