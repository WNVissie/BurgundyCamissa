from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import Designation

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
