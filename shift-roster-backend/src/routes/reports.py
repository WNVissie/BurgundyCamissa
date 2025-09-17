from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import db, User, Skill, License, Role, AreaOfResponsibility, Designation, ShiftRoster, LeaveRequest, Shift, EmployeeLicense, employee_skills
from src.utils.decorators import manager_required
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/employee-search', methods=['GET'])
@jwt_required()
@manager_required
def employee_search_report():
    """
    Advanced employee search report.
    Filters by: skills, licenses, roles, areas, designations, and date range.
    Shows current shift status for each date in the range.
    """
    print("=== EMPLOYEE SEARCH ENDPOINT HIT ===")
    try:
        print("=== EMPLOYEE SEARCH REQUEST ===")
        print(f"Full request args: {dict(request.args)}")
        print(f"Raw request.args: {request.args}")
        
        # Get filter criteria from query params
        skill_ids = request.args.getlist('skill_ids', type=int)
        license_ids = request.args.getlist('license_ids', type=int)
        role_ids = request.args.getlist('role_ids', type=int)
        area_ids = request.args.getlist('area_ids', type=int)
        designation_ids = request.args.getlist('designation_ids', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        # Debug logging
        print(f"Filter params received:")
        print(f"  skill_ids: {skill_ids}")
        print(f"  license_ids: {license_ids}")
        print(f"  role_ids: {role_ids}")
        print(f"  area_ids: {area_ids}")
        print(f"  designation_ids: {designation_ids}")
        print(f"  start_date: {start_date_str}")
        print(f"  end_date: {end_date_str}")

        # Parse dates
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = date.today()

        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = start_date

        # Start with base query for all users
        query = User.query
        
        # Build filters step by step - only apply filters if values are provided
        filters_applied = []

        # Apply filters using EXISTS clauses - more reliable
        if skill_ids and len(skill_ids) > 0:
            print(f"Applying skill filter for skill_ids: {skill_ids}")
            # First, let's see what employees have these skills
            skill_employees = db.session.query(employee_skills.c.employee_id)\
                                .filter(employee_skills.c.skill_id.in_(skill_ids))\
                                .distinct().all()
            print(f"Found {len(skill_employees)} employees with these skills: {[e[0] for e in skill_employees]}")
            
            # Filter users who have any of the specified skills
            query = query.filter(
                User.id.in_(
                    db.session.query(employee_skills.c.employee_id)
                    .filter(employee_skills.c.skill_id.in_(skill_ids))
                )
            )
            filters_applied.append(f"skills: {skill_ids}")

        if license_ids and len(license_ids) > 0:
            # Filter users who have any of the specified licenses
            query = query.filter(
                User.id.in_(
                    db.session.query(EmployeeLicense.employee_id)
                    .filter(EmployeeLicense.license_id.in_(license_ids))
                )
            )
            filters_applied.append(f"licenses: {license_ids}")

        if role_ids and len(role_ids) > 0:
            query = query.filter(User.role_id.in_(role_ids))
            filters_applied.append(f"roles: {role_ids}")

        if area_ids and len(area_ids) > 0:
            query = query.filter(User.area_of_responsibility_id.in_(area_ids))
            filters_applied.append(f"areas: {area_ids}")

        if designation_ids and len(designation_ids) > 0:
            query = query.filter(User.designation_id.in_(designation_ids))
            filters_applied.append(f"designations: {designation_ids}")

        print(f"Filters applied: {filters_applied}")
        
        # Execute query with distinct to avoid duplicates
        employees = query.distinct().all()
        
        print(f"Found {len(employees)} employees matching criteria")
        for emp in employees:
            print(f"  - {emp.name} {emp.surname} (ID: {emp.id})")

        if not employees:
            print("No employees found matching criteria!")
            return jsonify({
                'results': [],
                'message': 'No employees found matching the specified criteria'
            }), 200

        # Generate list of dates
        current_date = start_date
        dates = []
        while current_date <= end_date:
            dates.append(current_date)
            current_date = datetime.combine(current_date, datetime.min.time()) + timedelta(days=1)
            current_date = current_date.date()

        results = []

        for current_date in dates:
            date_employees = []
            
            for employee in employees:
                # Determine status for this specific date
                status = 'Available'

                # Check for shift on this date
                on_shift = ShiftRoster.query.filter(
                    and_(
                        ShiftRoster.employee_id == employee.id,
                        ShiftRoster.date == current_date,
                        ShiftRoster.status.in_(['approved', 'accepted'])    
                    )
                ).first()
                if on_shift:
                    status = f"On Shift ({on_shift.shift.name})" if on_shift.shift else 'On Shift'

                # Check for leave (overrides shift status if both exist)
                on_leave = LeaveRequest.query.filter(
                    and_(
                        LeaveRequest.employee_id == employee.id,
                        LeaveRequest.start_date <= current_date,
                        LeaveRequest.end_date >= current_date,
                        LeaveRequest.status == 'approved'
                    )
                ).first()
                if on_leave:
                    status = f"On Leave ({on_leave.leave_type})"

                date_employees.append({
                    'employee_id': employee.id,
                    'name': employee.name,
                    'surname': employee.surname,
                    'role': employee.role_ref.name if employee.role_ref else 'No Role',
                    'area': employee.area_ref.name if employee.area_ref else 'No Area',
                    'skills': ', '.join([skill.name for skill in employee.skills]) if employee.skills else 'No Skills',
                    'status': status
                })

            results.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'employees': date_employees
            })

        return jsonify({'results': results}), 200

    except Exception as e:
        print(f"Error in employee search: {str(e)}")
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/shift-acceptance', methods=['GET'])
@jwt_required()
@manager_required
def shift_acceptance_report():
    """
    Report on employees who have accepted or not yet accepted their shifts.
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        query = ShiftRoster.query.filter(
            ShiftRoster.status.in_(['approved', 'accepted'])
        )

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(ShiftRoster.date >= start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(ShiftRoster.date <= end_date)

        roster_entries = query.order_by(ShiftRoster.date, ShiftRoster.employee_id).all()

        return jsonify([entry.to_dict() for entry in roster_entries]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/employee-history/<int:employee_id>', methods=['GET'])
@jwt_required()
@manager_required
def employee_history_report(employee_id):
    """
    Get booking history for a single employee.
    """
    try:
        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Get all shift roster entries for this employee, ordered by date
        history = ShiftRoster.query.filter_by(employee_id=employee_id).order_by(ShiftRoster.date.desc()).all()

        # Get a summary of shift types, roles, etc.
        shift_type_counts = db.session.query(Shift.name, func.count(ShiftRoster.id)).join(ShiftRoster).filter(ShiftRoster.employee_id == employee_id).group_by(Shift.name).all()

        # Note: Role, Area, Designation history is not tracked. We can only show current ones.

        return jsonify({
            'employee_details': employee.to_dict(),
            'shift_history': [entry.to_dict() for entry in history],
            'summary': {
                'total_shifts': len(history),
                'shift_type_summary': [{'type': name, 'count': count} for name, count in shift_type_counts],
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/leave-report', methods=['GET'])
@jwt_required()
@manager_required
def leave_report():
    """
    Comprehensive leave report with filtering and summary statistics.
    Filters by: employee, status, date range, leave type
    Returns: detailed leave records and summary statistics
    """
    try:
        # Get filter parameters
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        leave_type = request.args.get('leave_type')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Build base query
        query = LeaveRequest.query.join(User)
        
        # Apply filters
        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)
        
        if status:
            query = query.filter(LeaveRequest.status == status)
            
        if leave_type:
            query = query.filter(LeaveRequest.leave_type == leave_type)
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(
                and_(
                    LeaveRequest.start_date >= start_date,
                    LeaveRequest.end_date <= end_date
                )
            )
        
        # Get filtered leave requests
        leave_requests = query.order_by(LeaveRequest.start_date.desc()).all()
        
        # Calculate summary statistics
        total_requests = len(leave_requests)
        total_days = sum(leave.days for leave in leave_requests if leave.days)
        
        # Group by status
        status_breakdown = {}
        for leave in leave_requests:
            status_breakdown[leave.status] = status_breakdown.get(leave.status, 0) + 1
        
        # Group by leave type
        type_breakdown = {}
        type_days_breakdown = {}
        for leave in leave_requests:
            leave_type = leave.leave_type
            type_breakdown[leave_type] = type_breakdown.get(leave_type, 0) + 1
            type_days_breakdown[leave_type] = type_days_breakdown.get(leave_type, 0) + (leave.days or 0)
        
        # Group by employee (for employee summary)
        employee_breakdown = {}
        for leave in leave_requests:
            emp_name = f"{leave.employee.name} {leave.employee.surname}"
            if emp_name not in employee_breakdown:
                employee_breakdown[emp_name] = {
                    'total_requests': 0,
                    'total_days': 0,
                    'employee_id': leave.employee_id
                }
            employee_breakdown[emp_name]['total_requests'] += 1
            employee_breakdown[emp_name]['total_days'] += leave.days or 0
        
        # Prepare detailed records
        detailed_records = []
        for leave in leave_requests:
            record = {
                'id': leave.id,
                'employee_id': leave.employee_id,
                'employee_name': f"{leave.employee.name} {leave.employee.surname}",
                'employee_number': leave.employee.employee_id,
                'department': leave.employee.area_ref.name if leave.employee.area_ref else 'N/A',
                'designation': leave.employee.designation_ref.designation_name if leave.employee.designation_ref else 'N/A',
                'leave_type': leave.leave_type,
                'start_date': leave.start_date.isoformat(),
                'end_date': leave.end_date.isoformat(),
                'days': leave.days,
                'status': leave.status,
                'reason': leave.reason,
                'submitted_date': leave.submitted_date.isoformat() if leave.submitted_date else None,
                'approved_by': leave.approved_by_user.name + ' ' + leave.approved_by_user.surname if leave.approved_by_user else None,
                'approved_date': leave.approved_date.isoformat() if leave.approved_date else None,
                'has_attachment': bool(leave.attachment_filename),
                'attachment_filename': leave.attachment_filename
            }
            detailed_records.append(record)
        
        # Calculate average days per employee
        avg_days_per_employee = total_days / len(employee_breakdown) if employee_breakdown else 0
        
        return jsonify({
            'summary': {
                'total_requests': total_requests,
                'total_days': total_days,
                'avg_days_per_employee': round(avg_days_per_employee, 2),
                'status_breakdown': status_breakdown,
                'type_breakdown': type_breakdown,
                'type_days_breakdown': type_days_breakdown,
                'employee_breakdown': employee_breakdown,
                'date_range': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                }
            },
            'records': detailed_records
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/leave-export', methods=['GET'])
@jwt_required()
@manager_required
def export_leave_report():
    """
    Export leave report data for external use.
    Returns simplified data structure suitable for CSV/Excel export.
    """
    try:
        # Get the same filtered data as leave_report
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        leave_type = request.args.get('leave_type')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Build base query
        query = LeaveRequest.query.join(User)
        
        # Apply filters
        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)
        
        if status:
            query = query.filter(LeaveRequest.status == status)
            
        if leave_type:
            query = query.filter(LeaveRequest.leave_type == leave_type)
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(
                and_(
                    LeaveRequest.start_date >= start_date,
                    LeaveRequest.end_date <= end_date
                )
            )
        
        # Get filtered leave requests
        leave_requests = query.order_by(LeaveRequest.start_date.desc()).all()
        
        # Prepare export data with flattened structure
        export_data = []
        for leave in leave_requests:
            export_data.append({
                'Employee Number': leave.employee.employee_id,
                'Employee Name': f"{leave.employee.name} {leave.employee.surname}",
                'Department': leave.employee.area_ref.name if leave.employee.area_ref else 'N/A',
                'Designation': leave.employee.designation_ref.designation_name if leave.employee.designation_ref else 'N/A',
                'Leave Type': leave.leave_type,
                'Start Date': leave.start_date.isoformat(),
                'End Date': leave.end_date.isoformat(),
                'Days': leave.days,
                'Status': leave.status,
                'Reason': leave.reason,
                'Submitted Date': leave.submitted_date.isoformat() if leave.submitted_date else '',
                'Approved By': leave.approved_by_user.name + ' ' + leave.approved_by_user.surname if leave.approved_by_user else '',
                'Approved Date': leave.approved_date.isoformat() if leave.approved_date else '',
                'Has Attachment': 'Yes' if leave.attachment_filename else 'No'
            })
        
        return jsonify(export_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
