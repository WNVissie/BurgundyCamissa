from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.models.models import Designation, db
from src.utils.decorators import permission_required

designations_bp = Blueprint('designations', __name__)

@designations_bp.route('', methods=['GET'])
@jwt_required()
def get_designations():
    """Get all designation types."""
    try:
        designations = Designation.query.order_by(Designation.designation_name).all()
        return jsonify([d.to_dict() for d in designations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@designations_bp.route('', methods=['POST'])
@permission_required('manage_employees')
def create_designation():
    """Create a new designation"""
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Designation name is required'}), 400
        
        # Check if designation already exists
        existing = Designation.query.filter_by(designation_name=data['name']).first()
        if existing:
            return jsonify({'error': 'Designation already exists'}), 400
        
        designation = Designation(
            designation_name=data['name']
        )
        
        db.session.add(designation)
        db.session.commit()
        
        return jsonify({
            'message': 'Designation created successfully',
            'designation': designation.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@designations_bp.route('/<int:designation_id>', methods=['PUT'])
@permission_required('manage_employees')
def update_designation(designation_id):
    """Update a designation"""
    try:
        designation = Designation.query.get(designation_id)
        if not designation:
            return jsonify({'error': 'Designation not found'}), 404
        
        data = request.get_json()
        
        if data.get('name'):
            # Check if new name conflicts with existing designation
            existing = Designation.query.filter(
                Designation.designation_name == data['name'],
                Designation.designation_id != designation_id
            ).first()
            if existing:
                return jsonify({'error': 'Designation name already exists'}), 400
            
            designation.designation_name = data['name']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Designation updated successfully',
            'designation': designation.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@designations_bp.route('/<int:designation_id>', methods=['DELETE'])
@permission_required('manage_employees')
def delete_designation(designation_id):
    """Delete a designation"""
    try:
        designation = Designation.query.get(designation_id)
        if not designation:
            return jsonify({'error': 'Designation not found'}), 404
        
        # Check if designation is in use
        if designation.users:
            return jsonify({'error': 'Cannot delete designation that is assigned to employees'}), 400
        
        db.session.delete(designation)
        db.session.commit()
        
        return jsonify({'message': 'Designation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
