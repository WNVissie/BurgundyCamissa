import os
import sys
from dotenv import load_dotenv
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from src.models.models import db
from src.routes.user import user_bp
from src.config import config
import logging

logging.basicConfig(level=logging.DEBUG)

def create_app():
    # Load env vars from .env if present (dev convenience)
    load_dotenv()
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    app.config.from_object(config['development'])
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # JWT error handlers to normalize responses
    @jwt.unauthorized_loader
    def handle_unauthorized(err_str):
        return {"error": "Unauthorized", "message": err_str}, 401

    @jwt.invalid_token_loader
    def handle_invalid_token(err_str):
        return {"error": "Invalid token", "message": err_str}, 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return {"error": "Token expired", "message": "Please refresh your session."}, 401

    @jwt.needs_fresh_token_loader
    def handle_needs_fresh(jwt_header, jwt_payload):
        return {"error": "Fresh token required", "message": "Please login again."}, 401

    @jwt.revoked_token_loader
    def handle_revoked(jwt_header, jwt_payload):
        return {"error": "Token revoked", "message": "Please login again."}, 401
    
    # Normalize JWT errors to 401 so the frontend can refresh or logout gracefully
    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        from flask import jsonify
        return jsonify({'error': f'Invalid token: {reason}'}), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        from flask import jsonify
        return jsonify({'error': f'Unauthorized: {reason}'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({'error': 'Token has expired'}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({'error': 'Token has been revoked'}), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({'error': 'Fresh token required'}), 401
    
    # Configure CORS to be specific to API routes, preventing conflicts with static file serving.
    # Allow frontend origin for development and production
    # Get CORS origins from environment variable or use defaults
    cors_origins = os.getenv('CORS_ORIGINS', 'https://burgundycamissa.netlify.app,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175,http://127.0.0.1:5176,http://127.0.0.1:5177').split(',')
    
    CORS(app, 
         supports_credentials=True,
         origins=cors_origins,
         allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Credentials'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         expose_headers=['Authorization'])
    
    # Register blueprints
    # Note: user_bp is obsolete and has been removed to avoid conflicts.
    # Employee management is handled by the employees_bp.
    
    # Import and register new blueprints
    from src.routes.auth import auth_bp
    from src.routes.employees import employees_bp
    from src.routes.roster import roster_bp
    from src.routes.admin import admin_bp
    from src.routes.analytics import analytics_bp
    from src.routes.export import export_bp
    from src.routes.timesheets import timesheets_bp
    from src.routes.licenses import licenses_bp
    from src.routes.leave import leave_bp
    from src.routes.reports import reports_bp
    from src.routes.designations import designations_bp
    from src.routes.community import community_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(employees_bp, url_prefix='/api/employees')
    app.register_blueprint(roster_bp, url_prefix='/api/roster')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(export_bp, url_prefix='/api/export')
    app.register_blueprint(designations_bp, url_prefix='/api/designations')
    app.register_blueprint(community_bp, url_prefix='/api/community')
    app.register_blueprint(timesheets_bp, url_prefix='/api/timesheets')
    app.register_blueprint(licenses_bp, url_prefix='/api/licenses')
    app.register_blueprint(leave_bp, url_prefix='/api/leave')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')

    # Create database tables and apply lightweight migrations
    with app.app_context():
        db.create_all()
        # Lightweight migration for new columns/tables
        # Skip migration checks for PostgreSQL as db.create_all() handles schema
        try:
            from sqlalchemy import text, inspect
            from sqlalchemy.exc import OperationalError
            
            # Check if we're using PostgreSQL or SQLite
            db_url = str(db.engine.url)
            is_postgres = 'postgresql' in db_url
            
            if not is_postgres:
                # SQLite-specific migration code
                with db.engine.connect() as conn:
                    cols = conn.execute(text("PRAGMA table_info(users)")).fetchall()
                    col_names = {c[1] for c in cols}
                    alter_stmts = []
                    if 'alt_contact_name' not in col_names:
                        alter_stmts.append("ALTER TABLE users ADD COLUMN alt_contact_name VARCHAR(100)")
                    if 'alt_contact_no' not in col_names:
                        alter_stmts.append("ALTER TABLE users ADD COLUMN alt_contact_no VARCHAR(20)")
                    
                    for stmt in alter_stmts:
                        try:
                            conn.execute(text(stmt))
                        except OperationalError:
                            pass

                    # Ensure licenses table exists
                    conn.execute(text("CREATE TABLE IF NOT EXISTS licenses (id INTEGER PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, description TEXT, created_at DATETIME)"))
                    # Ensure employee_licenses table exists
                    conn.execute(text("CREATE TABLE IF NOT EXISTS employee_licenses (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, license_id INTEGER NOT NULL, expiry_date DATE, created_at DATETIME, FOREIGN KEY(employee_id) REFERENCES users(id), FOREIGN KEY(license_id) REFERENCES licenses(id))"))
            else:
                # For PostgreSQL, db.create_all() handles everything
                # Just ensure tables exist
                print("PostgreSQL detected - using db.create_all() for schema management")
        except Exception as e:
            # Best-effort; ignore if migration check fails
            print(f"Migration check skipped: {e}")
            pass
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # Don't intercept API routes - let blueprints handle them
        if path.startswith('api/'):
            # This should not happen as blueprints should handle API routes
            # Return 404 to indicate API endpoint not found
            return {"error": "API endpoint not found"}, 404
            
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    @app.route('/ping')
    def ping():
        return 'pong'
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print("Exception occurred:", e)
        traceback.print_exc()
        return {"error": str(e)}, 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

