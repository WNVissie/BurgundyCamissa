from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import db, License, EmployeeLicense, User
from src.utils.decorators import permission_required, get_current_user, manager_required
from datetime import datetime

licenses_bp = Blueprint('licenses', __name__)

# --- License Type Management ---

@licenses_bp.route('/', methods=['GET'])
@jwt_required()
def get_licenses():
    """Get all license types."""
    try:
        licenses = License.query.order_by(License.name).all()
        return jsonify([l.to_dict() for l in licenses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@licenses_bp.route('/', methods=['POST'])
@jwt_required()
@permission_required('Admin')
def create_license():
    """Create a new license type."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'License name is required'}), 400

        new_license = License(name=data['name'], description=data.get('description', ''))
        db.session.add(new_license)
        db.session.commit()

        return jsonify(new_license.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@licenses_bp.route('/<int:license_id>', methods=['PUT'])
@jwt_required()
@permission_required('Admin')
def update_license(license_id):
    """Update an existing license type."""
    try:
        license = License.query.get(license_id)
        if not license:
            return jsonify({'error': 'License not found'}), 404

        data = request.get_json()
        if 'name' in data:
            license.name = data['name']
        if 'description' in data:
            license.description = data['description']

        db.session.commit()
        return jsonify(license.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@licenses_bp.route('/<int:license_id>', methods=['DELETE'])
@jwt_required()
@permission_required('Admin')
def delete_license(license_id):
    """Delete a license type."""
    try:
        license = License.query.get(license_id)
        if not license:
            return jsonify({'error': 'License not found'}), 404

        # Check if license is in use
        if EmployeeLicense.query.filter_by(license_id=license_id).first():
            return jsonify({'error': 'Cannot delete license as it is assigned to one or more employees'}), 400

        db.session.delete(license)
        db.session.commit()

        return jsonify({'message': 'License deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Employee license assignment is handled in employees.py
