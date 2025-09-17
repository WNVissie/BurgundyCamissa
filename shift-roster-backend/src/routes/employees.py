from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash
import secrets
import string
from src.models.models import db, User, Role, AreaOfResponsibility, Skill, License, EmployeeLicense
from src.utils.decorators import permission_required, get_current_user
from datetime import datetime

employees_bp = Blueprint('employees', __name__)

# Debug endpoint - remove this after testing
@employees_bp.route('/test', methods=['GET'])
def test_employees():
    """Test endpoint to debug employee data without auth"""
    try:
        employees = User.query.limit(5).all()
        return jsonify({
            'employees': [emp.to_dict() for emp in employees],
            'total': len(employees)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """Get all employees with optional filtering"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found. Please login again.'}), 401
        
        # Check permissions - Employees can get basic employee list for display,
        # but only Admin and Manager can use advanced filtering
        has_admin_permissions = current_user.role_ref and current_user.role_ref.name in ['Admin', 'Manager']
        
        # Get query parameters for filtering
        role_id = request.args.get('role_id', type=int)
        area_id = request.args.get('area_id', type=int)
        skill_id = request.args.get('skill_id', type=int)
        search = request.args.get('search', '')
        
        # If non-admin user tries to use filtering, deny access
        if not has_admin_permissions and (role_id or area_id or skill_id or search):
            return jsonify({'error': 'Insufficient permissions for filtered employee data'}), 403
        
        # Build query
        query = User.query
        
        # Only apply filters if user has admin permissions
        if has_admin_permissions:
            if role_id:
                query = query.filter(User.role_id == role_id)
            
            if area_id:
                query = query.filter(User.area_of_responsibility_id == area_id)
            
            if skill_id:
                query = query.join(User.skills).filter(Skill.id == skill_id)
            
            if search:
                search_filter = f'%{search}%'
                query = query.filter(
                    (User.name.ilike(search_filter)) |
                    (User.surname.ilike(search_filter)) |
                    (User.email.ilike(search_filter)) |
                    (User.employee_id.ilike(search_filter))
                )
        
        employees = query.all()
        
        # Determine if rates should be included based on user permissions
        include_rates = current_user.role_ref and current_user.role_ref.name == 'Admin'
        
        return jsonify({
            'employees': [emp.to_dict(include_rates=include_rates) for emp in employees],
            'total': len(employees)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('', methods=['POST'])
@permission_required('manage_employees')
def create_employee():
    """Create a new employee"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'name', 'surname', 'role_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.google_id == data.get('google_id')) | 
            (User.email == data['email']) |
            (User.username == data.get('username'))
        ).first()
        
        if existing_user:
            return jsonify({'error': 'User with this Google ID, email, or username already exists'}), 400
        
        # Validate role exists
        role = Role.query.get(data['role_id'])
        if not role:
            return jsonify({'error': 'Invalid role ID'}), 400
        
        # Validate area if provided
        if data.get('area_of_responsibility_id'):
            area = AreaOfResponsibility.query.get(data['area_of_responsibility_id'])
            if not area:
                return jsonify({'error': 'Invalid area of responsibility ID'}), 400
        
        # Create new employee
        employee = User(
            google_id=data.get('google_id'),
            email=data['email'],
            username=data.get('username'),
            name=data['name'],
            surname=data['surname'],
            employee_id=data.get('employee_id'),
            contact_no=data.get('contact_no'),
            alt_contact_name=data.get('alt_contact_name'),
            alt_contact_no=data.get('alt_contact_no'),
            designation_id=data.get('designation_id'),
            role_id=data['role_id'],
            area_of_responsibility_id=data.get('area_of_responsibility_id'),
            rate_type=data.get('rate_type'),
            rate_value=data.get('rate_value'),
            total_no_leave_days_annual=data.get('total_no_leave_days_annual'),
            total_no_leave_days_annual_float=data.get('total_no_leave_days_annual')  # Initialize remaining days to same as annual
        )
        
        # Hash password if provided
        if data.get('password'):
            employee.password_hash = generate_password_hash(data['password'])
        
        db.session.add(employee)
        db.session.commit()
        
        # Determine if rates should be included based on user permissions
        current_user = get_current_user()
        include_rates = current_user.role_ref and current_user.role_ref.name == 'Admin'
        
        return jsonify({
            'message': 'Employee created successfully',
            'employee': employee.to_dict(include_rates=include_rates)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Get specific employee details"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found. Please login again.'}), 401
        
        # Check permissions - users can view their own profile
        if current_user.role_ref.name not in ['Admin', 'Manager'] and current_user.id != employee_id:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Determine if rates should be included based on user permissions
        include_rates = current_user.role_ref and current_user.role_ref.name == 'Admin'
        
        return jsonify({'employee': employee.to_dict(include_rates=include_rates)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """Update employee details"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found. Please login again.'}), 401
        
        # Check permissions - users can update their own profile (limited fields)
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        
        # Admin can update all fields
        if current_user.role_ref.name == 'Admin':
            allowed_fields = ['email', 'username', 'password', 'name', 'surname', 'employee_id', 'contact_no', 'alt_contact_name', 'alt_contact_no', 'licenses', 'designation_id', 'role_id', 'area_of_responsibility_id', 'rate_type', 'rate_value', 'total_no_leave_days_annual']
        # Users can only update their own contact info
        elif current_user.id == employee_id:
            allowed_fields = ['contact_no']
        else:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Update allowed fields
        for field in allowed_fields:
            if field in data:
                if field == 'role_id':
                    if data[field]:
                        role = Role.query.get(data[field])
                        if not role:
                            return jsonify({'error': 'Invalid role ID'}), 400
                    employee.role_id = data[field]
                elif field == 'area_of_responsibility_id':
                    if data[field]:
                        area = AreaOfResponsibility.query.get(data[field])
                        if not area:
                            return jsonify({'error': 'Invalid area of responsibility ID'}), 400
                    employee.area_of_responsibility_id = data[field]
                elif field == 'designation_id':
                    employee.designation_id = data[field]
                elif field == 'total_no_leave_days_annual':
                    employee.total_no_leave_days_annual = data[field]
                    # When admin updates annual leave allocation, reset remaining days
                    # unless there are already approved leaves that need to be accounted for
                    if data[field] is not None:
                        from src.models.models import LeaveRequest
                        approved_leaves = LeaveRequest.query.filter_by(
                            employee_id=employee.id, 
                            status='approved'
                        ).all()
                        total_used_days = sum(float(leave.days) for leave in approved_leaves)
                        employee.total_no_leave_days_annual_float = float(data[field]) - total_used_days
                    else:
                        employee.total_no_leave_days_annual_float = None
                elif field == 'password':
                    # Only hash and update password if a new password is provided
                    if data[field] and data[field].strip():
                        employee.password_hash = generate_password_hash(data[field])
                else:
                    setattr(employee, field, data[field])
        
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Determine if rates should be included based on user permissions
        include_rates = current_user.role_ref and current_user.role_ref.name == 'Admin'
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee.to_dict(include_rates=include_rates)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@permission_required('manage_employees')
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check if employee has associated records
        if employee.shift_rosters or employee.timesheets:
            return jsonify({'error': 'Cannot delete employee with existing shift rosters or timesheets'}), 400
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'message': 'Employee deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/skills', methods=['POST'])
@permission_required('manage_employees')
def add_employee_skill(employee_id):
    """Add skill to employee"""
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        skill_id = data.get('skill_id')
        
        if not skill_id:
            return jsonify({'error': 'skill_id is required'}), 400
        
        skill = Skill.query.get(skill_id)
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        if skill in employee.skills:
            return jsonify({'error': 'Employee already has this skill'}), 400
        
        employee.skills.append(skill)
        db.session.commit()
        
        return jsonify({
            'message': 'Skill added to employee successfully',
            'employee': employee.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/skills/<int:skill_id>', methods=['DELETE'])
@permission_required('manage_employees')
def remove_employee_skill(employee_id, skill_id):
    """Remove skill from employee"""
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        skill = Skill.query.get(skill_id)
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        if skill not in employee.skills:
            return jsonify({'error': 'Employee does not have this skill'}), 400
        employee.skills.remove(skill)
        db.session.commit()
        return jsonify({
            'message': 'Skill removed from employee successfully',
            'employee': employee.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# License endpoints are now consolidated here.
# Listing all available license types is handled in licenses.py

@employees_bp.route('/<int:employee_id>/licenses', methods=['GET'])
@jwt_required()
def get_employee_licenses(employee_id):
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        return jsonify({'licenses': employee.to_dict().get('licenses_detailed', [])}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/licenses', methods=['POST'])
@permission_required('manage_employees')
def add_employee_license(employee_id):
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        data = request.get_json() or {}
        license_id = data.get('license_id')
        expiry_date_str = data.get('expiry_date')
        if not license_id:
            return jsonify({'error': 'license_id is required'}), 400
        lic = License.query.get(license_id)
        if not lic:
            return jsonify({'error': 'License not found'}), 404
        from datetime import datetime
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.fromisoformat(expiry_date_str).date()
            except Exception:
                return jsonify({'error': 'Invalid expiry_date format, expected ISO date'}), 400
        assoc = EmployeeLicense(employee_id=employee.id, license_id=license_id, expiry_date=expiry_date)
        db.session.add(assoc)
        db.session.commit()
        return jsonify({'message': 'License added to employee', 'employee': employee.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/licenses/<int:license_id>', methods=['PUT'])
@permission_required('manage_employees')
def update_employee_license(employee_id, license_id):
    try:
        assoc = EmployeeLicense.query.filter_by(employee_id=employee_id, license_id=license_id).first()
        if not assoc:
            return jsonify({'error': 'Employee license not found'}), 404
        data = request.get_json() or {}
        expiry_date_str = data.get('expiry_date')
        from datetime import datetime
        if expiry_date_str is not None:
            try:
                assoc.expiry_date = datetime.fromisoformat(expiry_date_str).date() if expiry_date_str else None
            except Exception:
                return jsonify({'error': 'Invalid expiry_date format, expected ISO date'}), 400
        db.session.commit()
        
        # Determine if rates should be included based on user permissions
        current_user = get_current_user()
        include_rates = current_user.role_ref and current_user.role_ref.name == 'Admin'
        
        return jsonify({'message': 'Employee license updated', 'employee': assoc.employee.to_dict(include_rates=include_rates)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/licenses/<int:license_id>', methods=['DELETE'])
@permission_required('manage_employees')
def remove_employee_license(employee_id, license_id):
    try:
        assoc = EmployeeLicense.query.filter_by(employee_id=employee_id, license_id=license_id).first()
        if not assoc:
            return jsonify({'error': 'Employee license not found'}), 404
        db.session.delete(assoc)
        db.session.commit()
        return jsonify({'message': 'License removed from employee'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def generate_temporary_password(length=12):
    """Generate a secure temporary password"""
    # Use a mix of letters, digits, and safe special characters
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    # Ensure at least one uppercase, one lowercase, one digit, and one special char
    if not any(c.isupper() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.islower() for c in password):
        password = password[:-1] + secrets.choice(string.ascii_lowercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + secrets.choice(string.digits)
    if not any(c in "!@#$%&*" for c in password):
        password = password[:-1] + secrets.choice("!@#$%&*")
    
    return password

@employees_bp.route('/<int:employee_id>/reset-password', methods=['POST'])
@permission_required('manage_employees')
def reset_employee_password(employee_id):
    """Reset an employee's password (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Only admin users can reset passwords'}), 403
        
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Generate a new temporary password
        new_password = generate_temporary_password()
        employee.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully',
            'temporary_password': new_password,
            'employee_name': f"{employee.name} {employee.surname}",
            'username': employee.username,
            'email': employee.email
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/generate-password', methods=['POST'])
@permission_required('manage_employees')
def generate_employee_password(employee_id):
    """Generate a new password for an employee (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Only admin users can generate passwords'}), 403
        
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Generate a new password but don't save it yet
        new_password = generate_temporary_password()
        
        return jsonify({
            'message': 'New password generated',
            'password': new_password,
            'employee_name': f"{employee.name} {employee.surname}",
            'note': 'Password has been generated but not saved. Use the update endpoint to save it.'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employees_bp.route('/<int:employee_id>/password-info', methods=['GET'])
@permission_required('manage_employees')
def get_employee_password_info(employee_id):
    """Get password status information for an employee (Admin only)"""
    try:
        current_user = get_current_user()
        if not current_user or current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Only admin users can view password information'}), 403
        
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({
            'employee_name': f"{employee.name} {employee.surname}",
            'username': employee.username,
            'email': employee.email,
            'has_password': bool(employee.password_hash),
            'has_google_auth': bool(employee.google_id),
            'login_methods': {
                'google_oauth': bool(employee.google_id),
                'username_password': bool(employee.password_hash and employee.username)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

