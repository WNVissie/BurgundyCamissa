from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from src.models.models import db, Timesheet, ShiftRoster, User
from src.utils.decorators import get_current_user

timesheets_bp = Blueprint('timesheets', __name__)

# GET endpoint to fetch timesheets
@timesheets_bp.route('', methods=['GET'])
@jwt_required()
def get_timesheets():
    """Fetch timesheets, optionally filtered by date range and/or employee, with employee name/surname."""
    current_user = get_current_user()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    employee_id = request.args.get('employee_id')

    query = db.session.query(Timesheet, User).join(User, Timesheet.employee_id == User.id)

    # If user is an employee, they can only see their own timesheets
    if current_user.role_ref.name == 'Employee':
        query = query.filter(Timesheet.employee_id == current_user.id)
    elif employee_id: # Admins/Managers can filter by employee
        query = query.filter(Timesheet.employee_id == int(employee_id))

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Timesheet.date >= start_dt)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD'}), 400
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Timesheet.date <= end_dt)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use YYYY-MM-DD'}), 400

    results = query.order_by(Timesheet.date.desc()).all()
    timesheets = []
    for ts, user in results:
        ts_dict = ts.to_dict()
        ts_dict['employee_name'] = user.name
        ts_dict['employee_surname'] = user.surname
        timesheets.append(ts_dict)
    return jsonify(timesheets), 200

@timesheets_bp.route('/generate', methods=['POST'])
def generate_timesheets():
    """Generate timesheets from roster entries within a date range.
    Request JSON: { start_date: 'YYYY-MM-DD', end_date: 'YYYY-MM-DD', employee_id?: int }
    Admin/Manager: for all or specific employee; Employee: only for self.
    Creates timesheets only when not existing for roster entries with approved or pending status.
    """
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        employee_id = data.get('employee_id')

        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Generate timesheets only from approved shifts
        query = ShiftRoster.query.filter_by(status='approved')

        if employee_id:
            query = query.filter(ShiftRoster.employee_id == int(employee_id))

        query = query.filter(ShiftRoster.date >= start_dt, ShiftRoster.date <= end_dt)

        rosters = query.all()
        created = 0
        for r in rosters:
            existing = Timesheet.query.filter_by(roster_id=r.id).first()
            if existing:
                continue
            ts = Timesheet(
                employee_id=r.employee_id,
                roster_id=r.id,
                date=r.date,
                hours_worked=r.hours,
                status='pending'
            )
            db.session.add(ts)
            created += 1

        db.session.commit()
        return jsonify({'message': f'Generated {created} timesheets', 'created': created}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@timesheets_bp.route('/<int:id>/approve', methods=['POST'])
@jwt_required()
def approve_timesheet(id):
    """Approve a timesheet by ID."""
    current_user = get_current_user()
    ts = Timesheet.query.get(id)
    if not ts:
        return jsonify({'error': 'Timesheet not found'}), 404
    ts.status = 'approved'
    ts.approved_by = current_user.id
    ts.approved_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Timesheet approved', 'timesheet': ts.to_dict()}), 200

@timesheets_bp.route('/<int:id>/accept', methods=['POST'])
@jwt_required()
def accept_timesheet(id):
    """Employee accepts a timesheet by ID."""
    ts = Timesheet.query.get(id)
    if not ts:
        return jsonify({'error': 'Timesheet not found'}), 404
    ts.status = 'accepted'
    db.session.commit()
    return jsonify({'message': 'Timesheet accepted', 'timesheet': ts.to_dict()}), 200

@timesheets_bp.route('/<int:id>/reject', methods=['POST'])
@jwt_required()
def reject_timesheet(id):
    """Reject a timesheet by ID."""
    current_user = get_current_user()
    data = request.get_json()
    ts = Timesheet.query.get(id)
    if not ts:
        return jsonify({'error': 'Timesheet not found'}), 404
    ts.status = 'rejected'
    ts.approved_by = current_user.id
    ts.approved_at = datetime.utcnow()
    if data and 'notes' in data:
        ts.notes = data['notes']
    db.session.commit()
    return jsonify({'message': 'Timesheet rejected', 'timesheet': ts.to_dict()}), 200
