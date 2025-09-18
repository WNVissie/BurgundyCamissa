from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, Role, AreaOfResponsibility, Skill, Shift, License, HourlyRates, User
from src.utils.decorators import permission_required, role_required, get_current_user
from datetime import time, date, datetime
import json

admin_bp = Blueprint('admin', __name__)

# Roles Management
@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    """Get all roles"""
    try:
        roles = Role.query.all()
        return jsonify({
            'roles': [role.to_dict() for role in roles],
            'total': len(roles)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles', methods=['POST'])
@permission_required('manage_roles')
def create_role(): 
    """Create a new role"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'Role name is required'}), 400
        
        # Check if role already exists
        existing_role = Role.query.filter_by(name=data['name']).first()
        if existing_role:
            return jsonify({'error': 'Role with this name already exists'}), 400
        
        role = Role(
            name=data['name'],
            permissions=json.dumps(data.get('permissions', {}))
        )
        
        db.session.add(role)
        db.session.commit()
        
        return jsonify({
            'message': 'Role created successfully',
            'role': role.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
@permission_required('manage_roles')
def update_role(role_id):
    """Update a role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if another role has this name
            existing_role = Role.query.filter(Role.name == data['name'], Role.id != role_id).first()
            if existing_role:
                return jsonify({'error': 'Role with this name already exists'}), 400
            role.name = data['name']
        
        if 'permissions' in data:
            role.permissions = json.dumps(data['permissions'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Role updated successfully',
            'role': role.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@permission_required('manage_roles')
def delete_role(role_id):
    """Delete a role"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        
        # Check if role is in use
        if role.users:
            return jsonify({'error': 'Cannot delete role that is assigned to users'}), 400
        
        db.session.delete(role)
        db.session.commit()
        
        return jsonify({'message': 'Role deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Areas of Responsibility Management
@admin_bp.route('/areas', methods=['GET'])
@jwt_required()
def get_areas():
    """Get all areas of responsibility"""
    try:
        areas = AreaOfResponsibility.query.all()
        return jsonify({
            'areas': [area.to_dict() for area in areas],
            'total': len(areas)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/areas', methods=['POST'])
@permission_required('manage_areas')
def create_area():
    """Create a new area of responsibility"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'Area name is required'}), 400
        
        # Check if area already exists
        existing_area = AreaOfResponsibility.query.filter_by(name=data['name']).first()
        if existing_area:
            return jsonify({'error': 'Area with this name already exists'}), 400
        
        area = AreaOfResponsibility(
            name=data['name'],
            description=data.get('description', ''),
            color=data.get('color', '#808080')
        )
        
        db.session.add(area)
        db.session.commit()
        
        return jsonify({
            'message': 'Area created successfully',
            'area': area.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/areas/<int:area_id>', methods=['PUT'])
@permission_required('manage_areas')
def update_area(area_id):
    """Update an area of responsibility"""
    try:
        area = AreaOfResponsibility.query.get(area_id)
        if not area:
            return jsonify({'error': 'Area not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if another area has this name
            existing_area = AreaOfResponsibility.query.filter(
                AreaOfResponsibility.name == data['name'], 
                AreaOfResponsibility.id != area_id
            ).first()
            if existing_area:
                return jsonify({'error': 'Area with this name already exists'}), 400
            area.name = data['name']
        
        if 'description' in data:
            area.description = data['description']

        if 'color' in data:
            area.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Area updated successfully',
            'area': area.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/areas/<int:area_id>', methods=['DELETE'])
@permission_required('manage_areas')
def delete_area(area_id):
    """Delete an area of responsibility"""
    try:
        area = AreaOfResponsibility.query.get(area_id)
        if not area:
            return jsonify({'error': 'Area not found'}), 404
        
        # Check if area is in use
        if area.users:
            return jsonify({'error': 'Cannot delete area that is assigned to users'}), 400
        
        db.session.delete(area)
        db.session.commit()
        
        return jsonify({'message': 'Area deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Skills Management
@admin_bp.route('/skills', methods=['GET'])
@jwt_required()
def get_skills():
    """Get all skills"""
    try:
        skills = Skill.query.all()
        return jsonify({
            'skills': [skill.to_dict() for skill in skills],
            'total': len(skills)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/skills', methods=['POST'])
@permission_required('manage_skills')
def create_skill():
    """Create a new skill"""
    try:
        data = request.get_json()
        
        if 'name' not in data:
            return jsonify({'error': 'Skill name is required'}), 400
        
        # Check if skill already exists
        existing_skill = Skill.query.filter_by(name=data['name']).first()
        if existing_skill:
            return jsonify({'error': 'Skill with this name already exists'}), 400
        
        skill = Skill(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'message': 'Skill created successfully',
            'skill': skill.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/skills/<int:skill_id>', methods=['PUT'])
@permission_required('manage_skills')
def update_skill(skill_id):
    """Update a skill"""
    try:
        skill = Skill.query.get(skill_id)
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if another skill has this name
            existing_skill = Skill.query.filter(
                Skill.name == data['name'], 
                Skill.id != skill_id
            ).first()
            if existing_skill:
                return jsonify({'error': 'Skill with this name already exists'}), 400
            skill.name = data['name']
        
        if 'description' in data:
            skill.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Skill updated successfully',
            'skill': skill.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
@permission_required('manage_skills')
def delete_skill(skill_id):
    """Delete a skill"""
    try:
        skill = Skill.query.get(skill_id)
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
        
        # Check if skill is in use
        if skill.employees:
            return jsonify({'error': 'Cannot delete skill that is assigned to employees'}), 400
        
        db.session.delete(skill)
        db.session.commit()
        
        return jsonify({'message': 'Skill deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Shifts Management
@admin_bp.route('/shifts', methods=['GET'])
@jwt_required()
def get_shifts():
    """Get all shift types"""
    try:
        shifts = Shift.query.all()
        return jsonify({
            'shifts': [shift.to_dict() for shift in shifts],
            'total': len(shifts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/shifts', methods=['POST'])
@permission_required('manage_shifts')
def create_shift():
    """Create a new shift type"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'start_time', 'end_time', 'hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if shift already exists
        existing_shift = Shift.query.filter_by(name=data['name']).first()
        if existing_shift:
            return jsonify({'error': 'Shift with this name already exists'}), 400
        
        # Parse time strings
        try:
            start_time = time.fromisoformat(data['start_time'])
            end_time = time.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({'error': 'Invalid time format. Use HH:MM'}), 400
        
        shift = Shift(
            name=data['name'],
            start_time=start_time,
            end_time=end_time,
            hours=data['hours'],
            description=data.get('description', ''),
            color=data.get('color', '#3498db')
        )
        
        db.session.add(shift)
        db.session.commit()
        
        return jsonify({
            'message': 'Shift created successfully',
            'shift': shift.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/shifts/<int:shift_id>', methods=['PUT'])
@permission_required('manage_shifts')
def update_shift(shift_id):
    """Update a shift type"""
    try:
        shift = Shift.query.get(shift_id)
        if not shift:
            return jsonify({'error': 'Shift not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            # Check if another shift has this name
            existing_shift = Shift.query.filter(
                Shift.name == data['name'], 
                Shift.id != shift_id
            ).first()
            if existing_shift:
                return jsonify({'error': 'Shift with this name already exists'}), 400
            shift.name = data['name']
        
        if 'start_time' in data:
            try:
                shift.start_time = time.fromisoformat(data['start_time'])
            except ValueError:
                return jsonify({'error': 'Invalid start_time format. Use HH:MM'}), 400
        
        if 'end_time' in data:
            try:
                shift.end_time = time.fromisoformat(data['end_time'])
            except ValueError:
                return jsonify({'error': 'Invalid end_time format. Use HH:MM'}), 400
        
        if 'hours' in data:
            shift.hours = data['hours']
        
        if 'description' in data:
            shift.description = data['description']
        
        if 'color' in data:
            shift.color = data['color']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shift updated successfully',
            'shift': shift.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/shifts/<int:shift_id>', methods=['DELETE'])
@permission_required('manage_shifts')
def delete_shift(shift_id):
    """Delete a shift type"""
    try:
        shift = Shift.query.get(shift_id)
        if not shift:
            return jsonify({'error': 'Shift not found'}), 404
        
        # Check if shift is in use
        if shift.shift_rosters:
            return jsonify({'error': 'Cannot delete shift that is used in rosters'}), 400
        
        db.session.delete(shift)
        db.session.commit()
        
        return jsonify({'message': 'Shift deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Licenses Management
# Get all licenses
@admin_bp.route('/licenses', methods=['GET'])
@jwt_required()
def get_licenses():
    """Get all licenses"""
    try:
        licenses = License.query.all()
        return jsonify({
            'licenses': [license.to_dict() for license in licenses],
            'total': len(licenses)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new license
@admin_bp.route('/licenses', methods=['POST'])
@permission_required('manage_licenses')
def create_license():
    """Create a new license"""
    try:
        data = request.get_json()
        if 'name' not in data:
            return jsonify({'error': 'License name is required'}), 400
        existing_license = License.query.filter_by(name=data['name']).first()
        if existing_license:
            return jsonify({'error': 'License with this name already exists'}), 400
        license = License(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(license)
        db.session.commit()
        return jsonify({
            'message': 'License created successfully',
            'license': license.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Hourly Rates Management
@admin_bp.route('/hourly-rates', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_hourly_rates():
    """Get all hourly rates with employee information"""
    try:
        print(f"========== ADMIN HOURLY RATES DEBUG ==========")
        print(f"Fetching hourly rates at {datetime.now()}")
        
        # First, get ALL rates to debug
        all_rates = db.session.query(HourlyRates, User).join(
            User, HourlyRates.employee_id == User.id
        ).order_by(User.name, User.surname).all()
        
        print(f"Total rates in database: {len(all_rates)}")
        
        # Now filter for current rates (no end_date or end_date in the future)
        rates = db.session.query(HourlyRates, User).join(
            User, HourlyRates.employee_id == User.id
        ).filter(
            db.or_(
                HourlyRates.end_date.is_(None),
                HourlyRates.end_date > date.today()
            )
        ).order_by(User.name, User.surname).all()
        
        print(f"Current rates after filtering: {len(rates)}")
        print(f"Today's date for comparison: {date.today()}")
        
        # Debug: Show all rates with their end dates
        for rate, employee in all_rates:
            print(f"  Rate ID {rate.rate_id}: {employee.name} {employee.surname} - "
                  f"Rate: R{rate.rate_per_hr} - End Date: {rate.end_date}")
        
        print(f"===============================================")
        
        rates_data = []
        for rate, employee in rates:
            rates_data.append({
                'rate_id': rate.rate_id,
                'employee_id': rate.employee_id,
                'employee_name': f"{employee.name} {employee.surname}",
                'employee_code': employee.employee_id,
                'rate_per_hr': float(rate.rate_per_hr),
                'currency': rate.currency,
                'effective_date': rate.effective_date.isoformat(),
                'end_date': rate.end_date.isoformat() if rate.end_date else None,
                'created_at': rate.created_at.isoformat()
            })
        
        return jsonify({
            'rates': rates_data,
            'total': len(rates_data)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/hourly-rates', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_hourly_rate():
    """Create a new hourly rate"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Validate required fields
        required_fields = ['employee_id', 'rate_per_hr']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate employee exists
        employee = User.query.get(data['employee_id'])
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Validate rate is positive
        if float(data['rate_per_hr']) <= 0:
            return jsonify({'error': 'Rate must be greater than 0'}), 400
        
        # Check if there's already an active rate for this employee
        existing_rate = HourlyRates.query.filter(
            HourlyRates.employee_id == data['employee_id'],
            db.or_(
                HourlyRates.end_date.is_(None),
                HourlyRates.end_date > date.today()
            )
        ).first()
        
        if existing_rate:
            # End the current rate
            existing_rate.end_date = date.today()
        
        # Parse effective date or use today
        effective_date = date.today()
        if 'effective_date' in data and data['effective_date']:
            try:
                effective_date = date.fromisoformat(data['effective_date'])
            except ValueError:
                return jsonify({'error': 'Invalid effective_date format. Use YYYY-MM-DD'}), 400
        
        # Create new rate
        new_rate = HourlyRates(
            employee_id=data['employee_id'],
            rate_per_hr=data['rate_per_hr'],
            currency=data.get('currency', 'ZAR'),
            effective_date=effective_date,
            created_by=current_user.id
        )
        
        db.session.add(new_rate)
        db.session.commit()
        
        return jsonify({
            'message': 'Hourly rate created successfully',
            'rate': {
                'rate_id': new_rate.rate_id,
                'employee_id': new_rate.employee_id,
                'employee_name': f"{employee.name} {employee.surname}",
                'rate_per_hr': float(new_rate.rate_per_hr),
                'currency': new_rate.currency,
                'effective_date': new_rate.effective_date.isoformat(),
                'end_date': new_rate.end_date.isoformat() if new_rate.end_date else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/hourly-rates/<int:rate_id>', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_hourly_rate(rate_id):
    """Update an hourly rate"""
    try:
        rate = HourlyRates.query.get(rate_id)
        if not rate:
            return jsonify({'error': 'Hourly rate not found'}), 404
        
        data = request.get_json()
        
        # Validate employee if changed
        if 'employee_id' in data:
            employee = User.query.get(data['employee_id'])
            if not employee:
                return jsonify({'error': 'Employee not found'}), 404
            rate.employee_id = data['employee_id']
        
        if 'rate_per_hr' in data:
            if float(data['rate_per_hr']) <= 0:
                return jsonify({'error': 'Rate must be greater than 0'}), 400
            rate.rate_per_hr = data['rate_per_hr']
        
        if 'currency' in data:
            rate.currency = data['currency']
        
        if 'effective_date' in data:
            try:
                rate.effective_date = date.fromisoformat(data['effective_date'])
            except ValueError:
                return jsonify({'error': 'Invalid effective_date format. Use YYYY-MM-DD'}), 400
        
        if 'end_date' in data:
            if data['end_date']:
                try:
                    rate.end_date = date.fromisoformat(data['end_date'])
                except ValueError:
                    return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400
            else:
                rate.end_date = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Hourly rate updated successfully',
            'rate': {
                'rate_id': rate.rate_id,
                'employee_id': rate.employee_id,
                'employee_name': f"{rate.employee.name} {rate.employee.surname}",
                'rate_per_hr': float(rate.rate_per_hr),
                'currency': rate.currency,
                'effective_date': rate.effective_date.isoformat(),
                'end_date': rate.end_date.isoformat() if rate.end_date else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/hourly-rates/<int:rate_id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin')
def delete_hourly_rate(rate_id):
    """Delete an hourly rate"""
    try:
        rate = HourlyRates.query.get(rate_id)
        if not rate:
            return jsonify({'error': 'Hourly rate not found'}), 404
        
        # Instead of deleting, we can end-date the rate
        rate.end_date = date.today()
        db.session.commit()
        
        return jsonify({'message': 'Hourly rate ended successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/hourly-rates/employees', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_employees_for_rates():
    """Get all employees for rate assignment dropdown"""
    try:
        print(f"========== ADMIN EMPLOYEES DEBUG ==========")
        print(f"Fetching employees at {datetime.now()}")
        
        employees = User.query.order_by(User.name, User.surname).all()
        print(f"Total employees: {len(employees)}")
        
        employee_list = []
        for employee in employees:
            # Check if employee has current rate
            has_current_rate = HourlyRates.query.filter(
                HourlyRates.employee_id == employee.id,
                db.or_(
                    HourlyRates.end_date.is_(None),
                    HourlyRates.end_date > date.today()
                )
            ).first() is not None
            
            print(f"  Employee {employee.id}: {employee.name} {employee.surname} - Has current rate: {has_current_rate}")
            
            employee_list.append({
                'id': employee.id,
                'name': f"{employee.name} {employee.surname}",
                'employee_id': employee.employee_id,
                'has_current_rate': has_current_rate
            })
        
        return jsonify({
            'employees': employee_list,
            'total': len(employee_list)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

