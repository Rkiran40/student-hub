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

    CORS(app, supports_credentials=True)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        # ensure models are imported so SQLAlchemy metadata includes them before create_all()
        try:
            print('IMPORTING backend.models')
            from . import models  # noqa: F401 - import for side-effects (register models)
            print('IMPORTED backend.models')
            app.logger.info('Imported backend.models')
        except Exception as e:
            print('FAILED to import backend.models', e)
            app.logger.exception('Failed to import backend.models')
        # create db tables
        db.create_all()

    # register blueprints
    from .routes.auth import auth_bp
    from .routes.student import student_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Serve uploaded files from the configured UPLOAD_FOLDER at /uploads/<path:relpath>
    @app.route('/uploads/<path:relpath>')
    def serve_upload(relpath):
        import os
        from flask import send_from_directory, abort
        uploads_root = app.config.get('UPLOAD_FOLDER')
        # Normalize to a safe OS path for filesystem checks
        rel_parts = [p for p in relpath.replace('\\', '/').split('/') if p and p != '..']
        full = os.path.join(uploads_root, *rel_parts)
        if not os.path.isfile(full):
            # Don't leak filesystem details; return a simple 404 JSON
            return jsonify({'success': False, 'message': 'File not found'}), 404
        # For send_from_directory, use a POSIX-style relative path
        rel_for_send = '/'.join(rel_parts)
        try:
            return send_from_directory(uploads_root, rel_for_send)
        except Exception:
            # If send_from_directory fails for any reason, return generic 404
            return jsonify({'success': False, 'message': 'File not found'}), 404

    @app.get('/debug/db')
    def debug_db():
        import os
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


if __name__ == '__main__':
    # Allow overriding the port with the PORT env var (default to 5001 for local dev)
    port = int(os.environ.get('PORT', 5001))
    create_app().run(host='0.0.0.0', port=port, debug=True)
