from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from google.auth.transport import requests
from google.oauth2 import id_token
from src.models.models import db, User, Role
from datetime import datetime
import json

auth_bp = Blueprint('auth', __name__)

# NOTE: Blueprint is registered with url_prefix='/api/auth' in main.py,
# so these routes should NOT include '/auth' again.
@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """Authenticate user with Google OAuth token"""
    try:
        data = request.get_json() or {}
        token = data.get('token')
        
        # For development, we'll skip actual Google verification
        # In production, uncomment the following lines:
        # try:
        #     idinfo = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])
        #     google_id = idinfo['sub']
        #     email = idinfo['email']
        #     name = idinfo.get('given_name', '')
        #     surname = idinfo.get('family_name', '')
        # except ValueError:
        #     return jsonify({'error': 'Invalid token'}), 401

        # Development fallback: accept mock credentials without a token
        email = data.get('email') or 'dev@example.com'
        google_id = data.get('google_id') or f"dev_{email.replace('@', '_').replace('.', '_')}"
        name = data.get('name') or 'Dev'
        surname = data.get('surname') or 'User'
        
        # Check if user exists by google_id first, then by email as fallback
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Update the google_id for existing user found by email
                user.google_id = google_id
                db.session.commit()
        
        if not user:
            # Determine role: Admin for specific email, otherwise Employee
            if email == 'wanda.nezar@gmail.com':
                role_name = 'Admin'
            else:
                role_name = 'Employee'

            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return jsonify({'error': f'Default role "{role_name}" not found'}), 500
            
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                surname=surname,
                role_id=role.id,
                contact_no=''  # Provide default empty string for required field
            )
            db.session.add(user)
            db.session.commit()
        
        # Create JWT tokens
        # Identity in JWT should be a string to satisfy PyJWT 'sub' claim requirements
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        try:
            user_id_int = int(current_user_id)
        except Exception:
            user_id_int = current_user_id

        user = User.query.get(user_id_int)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        new_token = create_access_token(identity=str(user.id))
        return jsonify({'access_token': new_token}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        try:
            user_id_int = int(current_user_id)
        except Exception:
            user_id_int = current_user_id
        user = User.query.get(user_id_int)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({'message': 'Successfully logged out'}), 200

