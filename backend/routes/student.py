from flask import Blueprint, request, jsonify, current_app, send_file
from ..db import db
from ..models import User, Profile, DailyUpload
from ..utils import allowed_file, save_upload_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os

student_bp = Blueprint('student', __name__)

@student_bp.route('/uploads', methods=['GET'])
@jwt_required()
def get_uploads():
    import os
    try:
        user_id = get_jwt_identity()
        uploads = DailyUpload.query.filter_by(user_id=user_id).order_by(DailyUpload.created_at.desc()).all()
        result = []
        uploads_root = current_app.config.get('UPLOAD_FOLDER')
        for u in uploads:
            file_url = u.file_url
            if not file_url.startswith('/uploads/'):
                try:
                    rel = os.path.relpath(file_url, uploads_root)
                    # Convert to forward slashes for URL
                    rel = rel.replace('\\', '/')
                    file_url = f"/uploads/{rel}"
                except Exception:
                    # leave as is if conversion fails
                    pass
            else:
                # Ensure forward slashes in stored URL paths
                file_url = file_url.replace('\\', '/')
            result.append({
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
            })
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to fetch uploads: {str(e)}'}), 500

@student_bp.route('/uploads', methods=['POST'])
@jwt_required()
def upload_file():
    # multipart/form-data
    user_id = get_jwt_identity()
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
        file = request.files['file']
        description = request.form.get('description')

        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        path = save_upload_file(file, user_id)

        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        upload = DailyUpload(
            user_id=user_id,
            file_name=file.filename,
            file_url=path,
            file_type=file.content_type or file.mimetype,
            file_size=file_size,
            description=description,
        )
        db.session.add(upload)
        db.session.commit()

        return jsonify({'success': True, 'message': 'File uploaded successfully', 'upload': {'id': upload.id}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Failed to upload file: {str(e)}'}), 500

@student_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    profile = user.profile
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'id': profile.id,
            'user_id': profile.user_id,
            'username': profile.username,
            'email': profile.email,
            'full_name': profile.full_name,
            'contact_number': profile.contact_number,
            'college_name': profile.college_name,
            'college_id': profile.college_id,
            'city': profile.city,
            'pincode': profile.pincode,
            'college_email': profile.college_email,
            'status': profile.status,
        })
    else:
        try:
            data = request.get_json() or {}
            if 'fullName' in data:
                profile.full_name = data.get('fullName')
            if 'contactNumber' in data:
                profile.contact_number = data.get('contactNumber')
            if 'collegeName' in data:
                profile.college_name = data.get('collegeName')
            if 'collegeId' in data:
                profile.college_id = data.get('collegeId')
            if 'collegeEmail' in data:
                profile.college_email = data.get('collegeEmail')
            profile.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Failed to update profile: {str(e)}'}), 500

@student_bp.route('/uploads/<upload_id>/download', methods=['GET'])
@jwt_required()
def download_upload(upload_id):
    import os
    upload = DailyUpload.query.get(upload_id)
    if not upload:
        return jsonify({'success': False, 'message': 'Upload not found'}), 404
    # stored file_url is a served URL like /uploads/<rel_path>
    rel = upload.file_url
    if rel.startswith('/uploads/'):
        rel = rel[len('/uploads/'):]
    # Convert forward slashes to OS-specific path separators
    rel = rel.replace('/', os.sep)
    uploads_root = current_app.config.get('UPLOAD_FOLDER')
    full_path = os.path.join(uploads_root, rel)
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'message': 'File not found on server'}), 404
    return send_file(full_path, as_attachment=True, download_name=upload.file_name)
