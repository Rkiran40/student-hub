import os, sys
if __name__ == '__main__' and __package__ is None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, repo_root)
    __package__ = 'backend'

from flask import Flask, jsonify
from flask_cors import CORS
from backend.config import Config
from backend.db import db
from backend.auth import jwt


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    # ✅ FIXED CORS (allows Railway + tokens + other devices)
    CORS(
        app,
        supports_credentials=True,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # create db tables
        db.create_all()

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Serve uploaded files
    @app.route('/uploads/<path:relpath>')
    def serve_upload(relpath):
        from flask import send_from_directory
        uploads_root = app.config.get('UPLOAD_FOLDER')
        relpath_os = relpath.replace('/', os.sep)
        full = os.path.join(uploads_root, relpath_os)

        if not os.path.exists(full):
            return jsonify({'success': False, 'message': 'File not found'}), 404

        return send_from_directory(uploads_root, relpath_os)

    @app.get('/debug/db')
    def debug_db():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        info = {'SQLALCHEMY_DATABASE_URI': uri}

        if uri and uri.startswith('sqlite'):
            rel = uri.split('sqlite:///')[-1]
            info['resolved_path'] = os.path.abspath(rel)
            info['exists'] = os.path.exists(info['resolved_path'])

            try:
                import sqlite3
                conn = sqlite3.connect(info['resolved_path'])
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                info['tables'] = [r[0] for r in cur.fetchall()]
                conn.close()
            except Exception as e:
                info['tables_error'] = str(e)

        return jsonify(info)

    @app.get('/')
    def health():
        return jsonify({"status": "ok"})

    return app


# ✅ RAILWAY-SAFE RUN
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    create_app().run(host='0.0.0.0', port=port, debug=False)
