from flask import Blueprint, request, jsonify
from src.models.models import db, User

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/', methods=['POST'])
def create_employee():
    data = request.json
    employee = User(
        # ...other fields...
        total_no_leave_days_annual=data.get('total_no_leave_days_annual')
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify(employee.to_dict()), 201

@employee_bp.route('/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = User.query.get_or_404(id)
    data = request.json
    if 'total_no_leave_days_annual' in data:
        employee.total_no_leave_days_annual = float(data['total_no_leave_days_annual'])
        print("Assigned annual leave days:", employee.total_no_leave_days_annual)
    db.session.commit()
    return jsonify(employee.to_dict())