from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['pdf', 'doc', 'docx', 'zip'])


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(hash: str, password: str) -> bool:
    return check_password_hash(hash, password)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload_file(file, user_id: str) -> str:
    uploads_root = current_app.config.get('UPLOAD_FOLDER')
    user_folder = os.path.join(uploads_root, user_id)
    os.makedirs(user_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    # store a relative path to the file under the uploads root
    rel_path = os.path.join(user_id, f"{int(__import__('time').time())}_{filename}")
    full_path = os.path.join(uploads_root, rel_path)
    file.save(full_path)
    # return relative path with forward slashes for URL (use in served URL: /uploads/<rel_path>)
    # Convert Windows backslashes to forward slashes for URLs
    return rel_path.replace('\\', '/')
