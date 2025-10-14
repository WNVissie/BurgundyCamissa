from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.models import db, User, ShiftRoster, Shift, Role, AreaOfResponsibility, Skill, LeaveRequest, ActivityLog, Timesheet, Designation, HourlyRates
from src.utils.decorators import get_current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_metrics():
    """Get main dashboard metrics"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        today = date.today()
        
        # Total employees
        total_employees = User.query.count()
        
        # Employees on shift today (check both 'approved' and 'accepted' status)
        employees_on_shift = db.session.query(func.count(func.distinct(ShiftRoster.employee_id))).filter(
            and_(
                ShiftRoster.date == today,
                ShiftRoster.status.in_(['approved', 'accepted'])
            )
        ).scalar()
        
        # Employees on leave today
        employees_on_leave = db.session.query(func.count(func.distinct(LeaveRequest.employee_id))).filter(
            and_(
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today,
                LeaveRequest.status.in_(['approved', 'accepted', 'authorised'])
            )
        ).scalar()
        
        # Available employees (not on shift or leave)
        available_employees = max(0, total_employees - employees_on_shift - employees_on_leave)
        
        # Pending approvals (all pending shifts, not just today)
        pending_approvals = ShiftRoster.query.filter(
            ShiftRoster.status == 'pending'
        ).count()
        
        # Total scheduled hours today
        total_scheduled_hours = db.session.query(func.sum(ShiftRoster.hours)).filter(
            and_(
                ShiftRoster.date == today,
                ShiftRoster.status.in_(['approved', 'accepted'])
            )
        ).scalar() or 0

        # Get recent activities
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(30).all()
        
        # Debug logging
        print(f"Debug - Today: {today}")
        print(f"Debug - Total employees: {total_employees}")
        print(f"Debug - Employees on shift: {employees_on_shift}")
        print(f"Debug - Employees on leave: {employees_on_leave}")
        
        return jsonify({
            'metrics': {
                'total_employees': total_employees,
                'employees_on_shift': employees_on_shift,
                'employees_on_leave': employees_on_leave,
                'available_employees': available_employees,
                'pending_approvals': pending_approvals,
                'total_scheduled_hours': float(total_scheduled_hours)
            },
            'recent_activity': [activity.to_dict() for activity in recent_activities]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/skill-distribution', methods=['GET'])
@jwt_required()
def get_skill_distribution():
    """Get the distribution of skills across all employees"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403

        # Query to count employees for each skill
        skill_counts = db.session.query(
            Skill.name,
            func.count(User.id).label('employee_count')
        ).join(User.skills).group_by(Skill.id, Skill.name).all()

        result = []
        for skill_name, count in skill_counts:
            result.append({
                'skill': skill_name,
                'employees': count
            })

        return jsonify({'data': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/weekly-approval-trends', methods=['GET'])
@jwt_required()
def get_weekly_approval_trends():
    """Get weekly shift approval trends for the last 12 weeks"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403

        today = date.today()
        # Go back to the beginning of the week (Monday) for the start date
        start_of_period = today - timedelta(days=today.weekday()) - timedelta(weeks=11)

        # Query weekly trends
        # Use correct function for week grouping depending on DB
        db_url = str(db.engine.url)
        if 'postgresql' in db_url:
            week_func = func.to_char(ShiftRoster.date, 'IYYY-IW')
        else:
            week_func = func.strftime('%Y-%W', ShiftRoster.date)
        weekly_data = db.session.query(
            week_func.label('week'),
            ShiftRoster.status,
            func.count(ShiftRoster.id).label('count')
        ).filter(
            ShiftRoster.date >= start_of_period
        ).group_by('week', ShiftRoster.status).order_by('week').all()

        # Process data into a structured format
        trends = {}
        for week_str, status, count in weekly_data:
            if week_str not in trends:
                trends[week_str] = {'week': week_str, 'approved': 0, 'pending': 0, 'rejected': 0}
            # Treat both 'approved' and 'accepted' as 'approved' for the chart
            if status in ['approved', 'accepted']:
                trends[week_str]['approved'] += count
            elif status in trends[week_str]:
                trends[week_str][status] = count

        # Sort by week and convert to list
        sorted_trends = sorted(trends.values(), key=lambda x: x['week'])

        return jsonify({'data': sorted_trends}), 200

    except Exception as e:
        import traceback
        print("Error in get_weekly_approval_trends:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/employees-by-shift', methods=['GET'])
@jwt_required()
def get_employees_by_shift():
    """Get employee count by shift type"""
    try:
        current_user = get_current_user()
        
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = (today - timedelta(days=today.weekday())).isoformat()
            end_date = (today + timedelta(days=6-today.weekday())).isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Query employee count by shift
        shift_counts = db.session.query(
            Shift.name,
            Shift.color,
            func.count(func.distinct(ShiftRoster.employee_id)).label('employee_count')
        ).join(ShiftRoster).filter(
            and_(
                ShiftRoster.date >= start_date_obj,
                ShiftRoster.date <= end_date_obj,
                ShiftRoster.status == 'approved'
            )
        ).group_by(Shift.id, Shift.name, Shift.color).all()
        
        result = []
        for shift_name, color, count in shift_counts:
            result.append({
                'shift_name': shift_name,
                'color': color,
                'employee_count': count
            })
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/employees-by-role', methods=['GET'])
@jwt_required()
def get_employees_by_role():
    """Get employee count by role"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Query employee count by role
        role_counts = db.session.query(
            Role.name,
            func.count(User.id).label('employee_count')
        ).join(User).group_by(Role.id, Role.name).all()
        
        result = []
        for role_name, count in role_counts:
            result.append({
                'role_name': role_name,
                'employee_count': count
            })
        
        return jsonify({'data': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/employees-by-area', methods=['GET'])
@jwt_required()
def get_employees_by_area():
    """Get employee and shift count by area of responsibility"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Subquery for employee counts per area
        emp_counts_sub = db.session.query(
            User.area_of_responsibility_id,
            func.count(User.id).label('employee_count')
        ).group_by(User.area_of_responsibility_id).subquery()

        # Subquery for shift counts per area
        shift_counts_sub = db.session.query(
            User.area_of_responsibility_id,
            func.count(ShiftRoster.id).label('shift_count')
        ).join(ShiftRoster, User.id == ShiftRoster.employee_id)\
         .group_by(User.area_of_responsibility_id).subquery()

        # Main query joining areas with subqueries
        results = db.session.query(
            AreaOfResponsibility.name,
            func.coalesce(emp_counts_sub.c.employee_count, 0),
            func.coalesce(shift_counts_sub.c.shift_count, 0)
        ).outerjoin(emp_counts_sub, AreaOfResponsibility.id == emp_counts_sub.c.area_of_responsibility_id)\
         .outerjoin(shift_counts_sub, AreaOfResponsibility.id == shift_counts_sub.c.area_of_responsibility_id)\
         .group_by(
            AreaOfResponsibility.name,
            emp_counts_sub.c.employee_count,
            shift_counts_sub.c.shift_count
         ).all()

        result_data = []
        for name, emp_count, shift_count in results:
            result_data.append({
                'name': name,
                'employees': emp_count,
                'shifts': shift_count
            })
        
        return jsonify({'data': result_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/leave-summary', methods=['GET'])
@jwt_required()
def get_leave_summary():
    """Get leave summary by type"""
    try:
        current_user = get_current_user()
        
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(month=1, day=1).isoformat()  # Start of year
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Query leave summary by type
        leave_summary = db.session.query(
            LeaveRequest.leave_type,
            func.count(LeaveRequest.id).label('request_count'),
            func.sum(LeaveRequest.days).label('total_days')
        ).filter(
            and_(
                LeaveRequest.start_date >= start_date_obj,
                LeaveRequest.end_date <= end_date_obj,
                LeaveRequest.status.in_(['approved', 'accepted', 'authorised'])
            )
        ).group_by(LeaveRequest.leave_type).all()
        
        result = []
        for leave_type, request_count, total_days in leave_summary:
            result.append({
                'leave_type': leave_type,
                'request_count': request_count,
                'total_days': total_days or 0
            })
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/skill-search', methods=['GET'])
@jwt_required()
def skill_search():
    """Search employees by skill or role"""
    try:
        current_user = get_current_user()
        
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        skill_name = request.args.get('skill')
        role_name = request.args.get('role')
        
        if not skill_name and not role_name:
            return jsonify({'error': 'Either skill or role parameter is required'}), 400
        
        query = User.query
        
        if skill_name:
            query = query.join(User.skills).filter(Skill.name.ilike(f'%{skill_name}%'))
        
        if role_name:
            query = query.join(Role).filter(Role.name.ilike(f'%{role_name}%'))
        
        employees = query.all()
        
        # Get current shift status for each employee
        today = date.today()
        result = []
        
        for employee in employees:
            # Check if employee has a shift today
            today_roster = ShiftRoster.query.filter(
                and_(
                    ShiftRoster.employee_id == employee.id,
                    ShiftRoster.date == today,
                    ShiftRoster.status == 'approved'
                )
            ).first()
            
            shift_status = 'available'
            if today_roster:
                shift_status = 'on_shift'
            
            # Check if on leave
            on_leave = LeaveRequest.query.filter(
                and_(
                    LeaveRequest.employee_id == employee.id,
                    LeaveRequest.start_date <= today,
                    LeaveRequest.end_date >= today,
                    LeaveRequest.status.in_(['approved', 'accepted', 'authorised'])
                )
            ).first()
            
            if on_leave:
                shift_status = f'on_{on_leave.leave_type}_leave'
            
            employee_data = employee.to_dict()
            employee_data['shift_status'] = shift_status
            employee_data['today_shift'] = today_roster.to_dict() if today_roster else None
            
            result.append(employee_data)
        
        return jsonify({
            'search_criteria': {
                'skill': skill_name,
                'role': role_name
            },
            'employees': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/shift-coverage', methods=['GET'])
@jwt_required()
def get_shift_coverage():
    """Get shift coverage analysis"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = (today - timedelta(days=today.weekday())).isoformat()
            end_date = (today + timedelta(days=6-today.weekday())).isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get planned (pending+approved) and actual (approved and date <= today) counts per shift type
        today = date.today()
        shift_types = db.session.query(Shift.id, Shift.name, Shift.color).all()
        utilization = []
        for shift_id, shift_name, color in shift_types:
            planned = db.session.query(func.count(ShiftRoster.id)).filter(
                ShiftRoster.shift_id == shift_id,
                ShiftRoster.date >= start_date_obj,
                ShiftRoster.date <= end_date_obj,
                ShiftRoster.status.in_(['pending', 'approved'])
            ).scalar() or 0
            actual = db.session.query(func.count(ShiftRoster.id)).filter(
                ShiftRoster.shift_id == shift_id,
                ShiftRoster.date >= start_date_obj,
                ShiftRoster.date <= end_date_obj,
                ShiftRoster.status == 'approved',
                ShiftRoster.date <= today
            ).scalar() or 0
            utilization.append({
                'shift_name': shift_name,
                'color': color,
                'planned': planned,
                'actual': actual,
                'utilization': int((actual / planned) * 100) if planned > 0 else 0
            })
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'utilization': utilization
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/employee-availability', methods=['GET'])
@jwt_required()
def get_employee_availability():
    """Get employee availability breakdown with separate counts for regular leave and sick leave"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name not in ['Admin', 'Manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get date range from request or default to current week
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = (today - timedelta(days=today.weekday())).isoformat()
            end_date = (today + timedelta(days=6-today.weekday())).isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Debug logging
        print(f"Employee Availability Debug:")
        print(f"Date range: {start_date_obj} to {end_date_obj}")
        print(f"Today: {date.today()}")
        
        # Total employees
        total_employees = User.query.count()
        
        # Employees on shift (approved/accepted status)
        employees_on_shift = db.session.query(func.count(func.distinct(ShiftRoster.employee_id))).filter(
            and_(
                ShiftRoster.date >= start_date_obj,
                ShiftRoster.date <= end_date_obj,
                ShiftRoster.status.in_(['approved', 'accepted'])
            )
        ).scalar() or 0
        
        # Employees on regular leave (all leave types except sick, with authorised status)
        # Count employees who have any authorized leave that overlaps with the date range
        employees_on_leave = db.session.query(func.count(func.distinct(LeaveRequest.employee_id))).filter(
            and_(
                LeaveRequest.start_date <= end_date_obj,
                LeaveRequest.end_date >= start_date_obj,
                LeaveRequest.status == 'authorised',
                LeaveRequest.leave_type != 'sick'
            )
        ).scalar() or 0
        
        # Debug leave queries
        print(f"Leave query conditions:")
        print(f"- start_date <= {end_date_obj}")
        print(f"- end_date >= {start_date_obj}")
        print(f"- status = 'authorised'")
        print(f"- leave_type != 'sick'")
        print(f"Regular leave count: {employees_on_leave}")
        
        # Employees on sick leave (sick leave type with authorised status)
        employees_on_sick_leave = db.session.query(func.count(func.distinct(LeaveRequest.employee_id))).filter(
            and_(
                LeaveRequest.start_date <= end_date_obj,
                LeaveRequest.end_date >= start_date_obj,
                LeaveRequest.status == 'authorised',
                LeaveRequest.leave_type == 'sick'
            )
        ).scalar() or 0
        
        print(f"Sick leave count: {employees_on_sick_leave}")
        
        # Available employees (not on shift, regular leave, or sick leave)
        available_employees = max(0, total_employees - employees_on_shift - employees_on_leave - employees_on_sick_leave)
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'availability': {
                'total_employees': total_employees,
                'available': available_employees,
                'on_shift': employees_on_shift,
                'on_leave': employees_on_leave,
                'on_sick_leave': employees_on_sick_leave
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== COST ANALYTICS ENDPOINTS (ADMIN ONLY) =====

@analytics_bp.route('/costs/overview', methods=['GET'])
@jwt_required()
def get_cost_overview():
    """Get cost overview metrics - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()  # Start of month
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Calculate total costs from approved timesheets using HourlyRates table
        cost_data = db.session.query(
            User.id,
            User.name,
            User.surname,
            HourlyRates.rate_per_hr,
            func.sum(Timesheet.hours_worked).label('total_hours')
        ).join(Timesheet, User.id == Timesheet.employee_id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved'
            )
        ).group_by(User.id, User.name, User.surname, HourlyRates.rate_per_hr).all()
        
        total_cost = 0
        total_hours = 0
        employee_count = 0
        
        print(f"=========================================")
        print(f"COST OVERVIEW DEBUG - {datetime.now()}")
        print(f"Date range: {start_date_obj} to {end_date_obj}")
        print(f"Found {len(cost_data)} employees with hourly rate data")
        print(f"=========================================")
        
        for employee_id, name, surname, hourly_rate, hours in cost_data:
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                print(f"Processing: {name} {surname}")
                print(f"  Hourly Rate: R{rate}/hr")
                print(f"  Hours: {hours}")
                
                # Calculate cost directly (no conversion needed - already hourly)
                cost = hours * rate
                
                print(f"  CALCULATION: {hours} hours × R{rate}/hour = R{cost:.2f}")
                print(f"  ---")
                
                total_cost += cost
                total_hours += hours
                employee_count += 1
        
        # Get total employees with rates
        total_employees_with_rates = User.query.filter(User.rate_value.isnot(None)).count()
        
        print(f"=========================================")
        print(f"FINAL TOTALS:")
        print(f"Total Cost: R{total_cost:.2f}")
        print(f"Total Hours: {total_hours}")
        print(f"Employee Count: {employee_count}")
        print(f"Avg per Employee: R{(total_cost / employee_count) if employee_count > 0 else 0:.2f}")
        print(f"Cost per Hour: R{(total_cost / total_hours) if total_hours > 0 else 0:.2f}")
        print(f"=========================================")
        
        # Calculate averages
        avg_cost_per_employee = total_cost / employee_count if employee_count > 0 else 0
        avg_cost_per_hour = total_cost / total_hours if total_hours > 0 else 0
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'overview': {
                'total_cost': round(total_cost, 2),
                'total_hours': round(total_hours, 2),
                'employee_count': employee_count,
                'total_employees_with_rates': total_employees_with_rates,
                'avg_cost_per_employee': round(avg_cost_per_employee, 2),
                'avg_cost_per_hour': round(avg_cost_per_hour, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/costs/by-area', methods=['GET'])
@jwt_required()
def get_costs_by_area():
    """Get cost breakdown by area of responsibility - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get cost data by area using HourlyRates table
        area_costs = db.session.query(
            AreaOfResponsibility.name.label('area_name'),
            AreaOfResponsibility.color,
            HourlyRates.rate_per_hr,
            func.sum(Timesheet.hours_worked).label('total_hours'),
            func.count(func.distinct(User.id)).label('employee_count')
        ).join(User, AreaOfResponsibility.id == User.area_of_responsibility_id)\
         .join(Timesheet, User.id == Timesheet.employee_id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved'
            )
        ).group_by(
            AreaOfResponsibility.name,
            AreaOfResponsibility.color,
            HourlyRates.rate_per_hr
        ).all()
        
        # Process data by area
        area_summary = {}
        for area_name, color, hourly_rate, hours, emp_count in area_costs:
            if area_name not in area_summary:
                area_summary[area_name] = {
                    'area_name': area_name,
                    'color': color,
                    'total_cost': 0,
                    'total_hours': 0,
                    'employee_count': 0
                }
            
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (already hourly rate)
                cost = hours * rate
                
                area_summary[area_name]['total_cost'] += cost
                area_summary[area_name]['total_hours'] += hours
                area_summary[area_name]['employee_count'] = emp_count
        
        # Round costs and add efficiency metrics
        result = []
        for area_data in area_summary.values():
            area_data['total_cost'] = round(area_data['total_cost'], 2)
            area_data['total_hours'] = round(area_data['total_hours'], 2)
            area_data['cost_per_hour'] = round(
                area_data['total_cost'] / area_data['total_hours'] if area_data['total_hours'] > 0 else 0, 2
            )
            area_data['cost_per_employee'] = round(
                area_data['total_cost'] / area_data['employee_count'] if area_data['employee_count'] > 0 else 0, 2
            )
            result.append(area_data)
        
        # Sort by total cost descending
        result.sort(key=lambda x: x['total_cost'], reverse=True)
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/costs/by-designation', methods=['GET'])
@jwt_required()
def get_costs_by_designation():
    """Get cost breakdown by designation - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get cost data by designation using HourlyRates table
        designation_costs = db.session.query(
            Designation.designation_name,
            HourlyRates.rate_per_hr,
            func.sum(Timesheet.hours_worked).label('total_hours'),
            func.count(func.distinct(User.id)).label('employee_count')
        ).join(User, Designation.designation_id == User.designation_id)\
         .join(Timesheet, User.id == Timesheet.employee_id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved'
            )
        ).group_by(
            Designation.designation_name,
            HourlyRates.rate_per_hr
        ).all()
        
        # Process data by designation
        designation_summary = {}
        for designation_name, hourly_rate, hours, emp_count in designation_costs:
            if designation_name not in designation_summary:
                designation_summary[designation_name] = {
                    'designation_name': designation_name,
                    'total_cost': 0,
                    'total_hours': 0,
                    'employee_count': 0
                }
            
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (no conversion needed - already hourly)
                cost = hours * rate
                
                designation_summary[designation_name]['total_cost'] += cost
                designation_summary[designation_name]['total_hours'] += hours
                designation_summary[designation_name]['employee_count'] = emp_count
        
        # Round costs and add efficiency metrics
        result = []
        for designation_data in designation_summary.values():
            designation_data['total_cost'] = round(designation_data['total_cost'], 2)
            designation_data['total_hours'] = round(designation_data['total_hours'], 2)
            designation_data['cost_per_hour'] = round(
                designation_data['total_cost'] / designation_data['total_hours'] if designation_data['total_hours'] > 0 else 0, 2
            )
            designation_data['cost_per_employee'] = round(
                designation_data['total_cost'] / designation_data['employee_count'] if designation_data['employee_count'] > 0 else 0, 2
            )
            result.append(designation_data)
        
        # Sort by total cost descending
        result.sort(key=lambda x: x['total_cost'], reverse=True)
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/costs/by-employee', methods=['GET'])
@jwt_required()
def get_costs_by_employee():
    """Get cost breakdown by employee - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get top limit (default 10)
        limit = int(request.args.get('limit', 10))
        
        # Get cost data by employee using HourlyRates table
        employee_costs = db.session.query(
            User.id,
            User.name,
            User.surname,
            User.employee_id,
            HourlyRates.rate_per_hr,
            AreaOfResponsibility.name.label('area_name'),
            Designation.designation_name,
            func.sum(Timesheet.hours_worked).label('total_hours'),
            func.count(func.distinct(Timesheet.date)).label('shift_count')
        ).join(Timesheet, User.id == Timesheet.employee_id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).outerjoin(AreaOfResponsibility, User.area_of_responsibility_id == AreaOfResponsibility.id)\
         .outerjoin(Designation, User.designation_id == Designation.designation_id)\
         .filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status.in_(['approved', 'accepted'])
            )
        ).group_by(
            User.id, User.name, User.surname, User.employee_id,
            HourlyRates.rate_per_hr,
            AreaOfResponsibility.name, Designation.designation_name
        ).all()
        
        # Calculate costs and create result
        result = []
        for (emp_id, name, surname, employee_id, hourly_rate, 
             area_name, designation_name, hours, shift_count) in employee_costs:
            
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (no conversion needed - already hourly)
                total_cost = hours * rate
                
                result.append({
                    'employee_id': employee_id,
                    'name': f"{name} {surname}",
                    'area': area_name or 'Unassigned',
                    'designation': designation_name or 'Unassigned',
                    'rate_type': 'hourly',
                    'rate_value': float(hourly_rate),
                    'total_hours': round(hours, 2),
                    'shift_count': shift_count,
                    'total_cost': round(total_cost, 2),
                    'cost_per_hour': round(total_cost / hours if hours > 0 else 0, 2),
                    'avg_hours_per_shift': round(hours / shift_count if shift_count > 0 else 0, 2)
                })
        
        # Sort by total cost descending and limit results
        result.sort(key=lambda x: x['total_cost'], reverse=True)
        if limit > 0:
            result = result[:limit]
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'limit': limit,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/costs/daily-trends', methods=['GET'])
@jwt_required()
def get_daily_cost_trends():
    """Get daily cost trends - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = (today - timedelta(days=30)).isoformat()  # Last 30 days
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get daily cost data using HourlyRates table
        daily_data = db.session.query(
            Timesheet.date,
            HourlyRates.rate_per_hr,
            func.sum(Timesheet.hours_worked).label('total_hours')
        ).join(User, Timesheet.employee_id == User.id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved'
            )
        ).group_by(Timesheet.date, HourlyRates.rate_per_hr).all()
        
        # Process daily costs
        daily_costs = {}
        for date_obj, hourly_rate, hours in daily_data:
            date_str = date_obj.isoformat()
            
            if date_str not in daily_costs:
                daily_costs[date_str] = 0
            
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (no conversion needed - already hourly)
                cost = hours * rate
                
                daily_costs[date_str] += cost
        
        # Create result with all dates in range (including zero-cost days)
        result = []
        current_date = start_date_obj
        while current_date <= end_date_obj:
            date_str = current_date.isoformat()
            result.append({
                'date': date_str,
                'total_cost': round(daily_costs.get(date_str, 0), 2)
            })
            current_date += timedelta(days=1)
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/costs/efficiency', methods=['GET'])
@jwt_required()
def get_cost_efficiency():
    """Get cost efficiency metrics - Admin only"""
    try:
        current_user = get_current_user()
        if current_user.role_ref.name != 'Admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Get planned vs actual hours and costs using HourlyRates table
        planned_data = db.session.query(
            HourlyRates.rate_per_hr,
            func.sum(ShiftRoster.hours).label('planned_hours')
        ).join(User, ShiftRoster.employee_id == User.id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                ShiftRoster.date >= start_date_obj,
                ShiftRoster.date <= end_date_obj,
                ShiftRoster.status.in_(['pending', 'approved', 'accepted'])
            )
        ).group_by(HourlyRates.rate_per_hr).all()
        
        actual_data = db.session.query(
            HourlyRates.rate_per_hr,
            func.sum(Timesheet.hours_worked).label('actual_hours')
        ).join(User, Timesheet.employee_id == User.id)\
         .join(HourlyRates, and_(
             User.id == HourlyRates.employee_id,
             HourlyRates.effective_date <= end_date_obj,
             or_(HourlyRates.end_date.is_(None), HourlyRates.end_date > start_date_obj)
         )).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved'
            )
        ).group_by(HourlyRates.rate_per_hr).all()
        
        # Calculate planned costs
        total_planned_cost = 0
        total_planned_hours = 0
        for hourly_rate, hours in planned_data:
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (no conversion needed - already hourly)
                cost = hours * rate
                
                total_planned_cost += cost
                total_planned_hours += hours
        
        # Calculate actual costs
        total_actual_cost = 0
        total_actual_hours = 0
        for hourly_rate, hours in actual_data:
            if hourly_rate and hours:
                hours = float(hours)
                rate = float(hourly_rate)
                
                # Calculate cost directly (no conversion needed - already hourly)
                cost = hours * rate
                
                total_actual_cost += cost
                total_actual_hours += hours
        
        # Calculate efficiency metrics
        cost_variance = total_actual_cost - total_planned_cost
        cost_variance_percent = (cost_variance / total_planned_cost * 100) if total_planned_cost > 0 else 0
        
        hours_variance = total_actual_hours - total_planned_hours
        hours_variance_percent = (hours_variance / total_planned_hours * 100) if total_planned_hours > 0 else 0
        
        hour_utilization = (total_actual_hours / total_planned_hours * 100) if total_planned_hours > 0 else 0
        
        return jsonify({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'efficiency': {
                'planned_cost': round(total_planned_cost, 2),
                'actual_cost': round(total_actual_cost, 2),
                'cost_variance': round(cost_variance, 2),
                'cost_variance_percent': round(cost_variance_percent, 2),
                'planned_hours': round(total_planned_hours, 2),
                'actual_hours': round(total_actual_hours, 2),
                'hours_variance': round(hours_variance, 2),
                'hours_variance_percent': round(hours_variance_percent, 2),
                'hour_utilization': round(hour_utilization, 2),
                'over_budget': cost_variance > 0,
                'under_utilized': hour_utilization < 90
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

