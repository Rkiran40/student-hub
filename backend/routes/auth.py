from flask import Blueprint, request, jsonify, current_app
from ..db import db
from ..models import User, Profile
from ..utils import hash_password, verify_password
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    contact_number = data.get('contact_number')
    college_name = data.get('college_name')
    college_id = data.get('college_id')
    city = data.get('city')
    pincode = data.get('pincode')
    college_email = data.get('college_email')

    if not email or not password or not full_name:
        return jsonify({'success': False, 'message': 'email, password, and full_name are required'}), 400

    try:
        user = User(email=email, password_hash=hash_password(password))
        db.session.add(user)
        db.session.flush()  # Get user.id without committing

        profile = Profile(
            user_id=user.id, 
            username=None, 
            full_name=full_name, 
            email=email, 
            contact_number=contact_number, 
            college_name=college_name, 
            college_id=college_id,
            city=city,
            pincode=pincode,
            college_email=college_email
        )
        db.session.add(profile)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Signup successful', 'user': {'id': user.id, 'email': user.email}})
    except IntegrityError as e:
        db.session.rollback()
        if 'email' in str(e.orig).lower() or 'unique' in str(e.orig).lower():
            return jsonify({'success': False, 'message': 'Email already exists'}), 409
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Signup failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username or email) or not password:
            return jsonify({'success': False, 'message': 'username (or email) and password required'}), 400

        # Support login by username (Profile.username) or by email (User.email)
        user = None
        profile = None
        if email:
            user = User.query.filter_by(email=email).first()
            profile = user.profile if user else None
        else:
            profile = Profile.query.filter_by(username=username).first()
            user = User.query.get(profile.user_id) if profile else None

        # Verify user and password
        if not user or not verify_password(user.password_hash, password):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

        # For admin users, skip status check (admins are always active)
        # For students, check if account is active
        if user.role != 'admin':
            if not profile or profile.status != 'active':
                if profile and profile.status == 'pending':
                    return jsonify({'success': False, 'message': 'Your account is pending approval. Please wait for admin verification.'}), 403
                elif profile and profile.status == 'suspended':
                    return jsonify({'success': False, 'message': 'Your account has been suspended. Please contact support.'}), 403

        access = create_access_token(identity=user.id)
        refresh = create_refresh_token(identity=user.id)

        return jsonify({
            'success': True,
            'access_token': access,
            'refresh_token': refresh,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': profile.username if profile else None,
                'role': user.role or 'student'
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Login error: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    profile = user.profile
    return jsonify({'success': True, 'user': {'id': user.id, 'email': user.email, 'role': user.role, 'profile': {
        'id': profile.id if profile else None,
        'username': profile.username if profile else None,
        'full_name': profile.full_name if profile else None,
        'status': profile.status if profile else 'pending'
    }}})

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access = create_access_token(identity=user_id)
    return jsonify({'success': True, 'access_token': access})

@auth_bp.route('/forgot-username', methods=['POST'])
def forgot_username():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'success': True, 'message': 'If an account exists, your username will be sent to your email.'})
    profile = Profile.query.filter_by(email=email).first()
    # For now, just pretend to send email
    return jsonify({'success': True, 'message': 'If an account exists, your username will be sent to your email.'})

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email')
    # In production you'd send an email with a secure token. Here, we return success.
    return jsonify({'success': True, 'message': 'Password reset email sent.'})

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    email = data.get('email')
    new_password = data.get('newPassword') or data.get('new_password') or data.get('password')
    if not email or not new_password:
        return jsonify({'success': False, 'message': 'email and new password are required'}), 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    user.password_hash = hash_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password reset successful.'})

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    data = request.get_json() or {}
    new_password = data.get('newPassword') or data.get('new_password') or data.get('password')
    if not new_password:
        return jsonify({'success': False, 'message': 'new password is required'}), 400
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    user.password_hash = hash_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully.'})
