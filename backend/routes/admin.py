from flask import Blueprint, request, jsonify, current_app
from ..db import db
from ..models import Profile, DailyUpload, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint('admin', __name__)

def admin_only(fn):
    # simple decorator to check role
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/students', methods=['GET'])
@jwt_required()
@admin_only
def get_students():
    try:
        profiles = Profile.query.order_by(Profile.created_at.desc()).all()
        result = [
            {
                'id': p.id,
                'user_id': p.user_id,
                'username': p.username,
                'email': p.email,
                'full_name': p.full_name,
                'contact_number': p.contact_number,
                'college_name': p.college_name,
                'college_id': p.college_id,
                'city': p.city,
                'pincode': p.pincode,
                'college_email': p.college_email,
                'status': p.status,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in profiles
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to fetch students: {str(e)}'}), 500

@admin_bp.route('/students/<profile_id>/approve', methods=['POST'])
@jwt_required()
@admin_only
def approve_student(profile_id):
    data = request.get_json() or {}
    username = data.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'username is required'}), 400
    
    # Check if username already exists
    existing_profile = Profile.query.filter_by(username=username).first()
    if existing_profile and existing_profile.id != profile_id:
        return jsonify({'success': False, 'message': f'Username "{username}" is already taken'}), 400
    
    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
    
    try:
        profile.username = username
        profile.status = 'active'
        db.session.commit()
        return jsonify({'success': True, 'message': f'Student approved with username: {username}'})
    except IntegrityError as e:
        db.session.rollback()
        if 'username' in str(e.orig).lower() or 'unique' in str(e.orig).lower():
            return jsonify({'success': False, 'message': f'Username "{username}" is already taken. Please choose a different username.'}), 400
        return jsonify({'success': False, 'message': 'Database constraint violation. Please try again.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to approve student: {str(e)}'}), 500

@admin_bp.route('/students/<profile_id>/suspend', methods=['POST'])
@jwt_required()
@admin_only
def suspend_student(profile_id):
    try:
        profile = Profile.query.get(profile_id)
        if not profile:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        profile.status = 'suspended'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Student suspended successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to suspend student: {str(e)}'}), 500

@admin_bp.route('/students/<profile_id>/activate', methods=['POST'])
@jwt_required()
@admin_only
def activate_student(profile_id):
    try:
        profile = Profile.query.get(profile_id)
        if not profile:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
        profile.status = 'active'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Student activated successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to activate student: {str(e)}'}), 500

@admin_bp.route('/uploads', methods=['GET'])
@jwt_required()
@admin_only
def get_uploads():
    import os
    try:
        uploads = DailyUpload.query.order_by(DailyUpload.created_at.desc()).all()
        # fetch profile names
        result = []
        uploads_root = current_app.config.get('UPLOAD_FOLDER')
        for u in uploads:
            profile = Profile.query.filter_by(user_id=u.user_id).first()
            file_url = u.file_url
            if not file_url.startswith('/uploads/'):
                try:
                    rel = os.path.relpath(file_url, uploads_root)
                    # Convert to forward slashes for URL
                    rel = rel.replace('\\', '/')
                    file_url = f"/uploads/{rel}"
                except Exception:
                    pass
            else:
                # Ensure forward slashes in stored URL paths
                file_url = file_url.replace('\\', '/')
            result.append({
                **{
                    'id': u.id,
                    'user_id': u.user_id,
                    'file_name': u.file_name,
                    'file_url': file_url,
                    'file_type': u.file_type,
                    'file_size': u.file_size,
                    'upload_date': u.upload_date.isoformat() if u.upload_date else None,
                    'description': u.description,
                    'status': u.status,
                    'admin_feedback': u.admin_feedback,
                    'reviewed_by': u.reviewed_by,
                    'reviewed_at': u.reviewed_at.isoformat() if u.reviewed_at else None,
                    'created_at': u.created_at.isoformat() if u.created_at else None,
                },
                'student_name': profile.full_name if profile else 'Unknown'
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to fetch uploads: {str(e)}'}), 500

@admin_bp.route('/uploads/<upload_id>/status', methods=['POST'])
@jwt_required()
@admin_only
def update_upload_status(upload_id):
    try:
        data = request.get_json() or {}
        status = data.get('status')
        feedback = data.get('feedback')
        if status not in ('reviewed', 'approved', 'rejected'):
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        upload = DailyUpload.query.get(upload_id)
        if not upload:
            return jsonify({'success': False, 'message': 'Upload not found'}), 404
        upload.status = status
        upload.admin_feedback = feedback
        upload.reviewed_by = get_jwt_identity()
        upload.reviewed_at = __import__('datetime').datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': f'Upload marked as {status}.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to update upload status: {str(e)}'}), 500
