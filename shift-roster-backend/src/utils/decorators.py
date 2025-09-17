from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import User, Role
import json

def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            try:
                user_id_int = int(current_user_id)
            except Exception:
                user_id_int = current_user_id
            user = User.query.get(user_id_int)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.role_ref:
                return jsonify({'error': 'User has no role assigned'}), 403
            
            if user.role_ref.name not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    """Decorator to check if user has specific permission"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            try:
                user_id_int = int(current_user_id)
            except Exception:
                user_id_int = current_user_id
            user = User.query.get(user_id_int)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.role_ref:
                return jsonify({'error': 'User has no role assigned'}), 403

            # Admins have access to all permissions
            if user.role_ref.name == 'Admin':
                return f(*args, **kwargs)
            
            raw = user.role_ref.permissions
            try:
                permissions = json.loads(raw) if isinstance(raw, str) else (raw or {})
            except Exception:
                permissions = {}
            
            if not permissions.get(permission, False):
                return jsonify({'error': f'Permission {permission} required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Helper function to get current user"""
    current_user_id = get_jwt_identity()
    try:
        user_id_int = int(current_user_id)
    except Exception:
        user_id_int = current_user_id
    return User.query.get(user_id_int)

# Convenience decorators used by some routes
def admin_required(f):
    return role_required('Admin')(f)

def manager_required(f):
    return role_required('Admin', 'Manager')(f)

