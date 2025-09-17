#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.models import db, User, ShiftRoster, LeaveRequest
from src.main import create_app
from datetime import datetime, date
from sqlalchemy import func, and_

def debug_dashboard():
    app = create_app()
    with app.app_context():
        today = date.today()
        print(f"Debug Dashboard for {today}")
        print("=" * 50)
        
        # Total employees
        total_employees = User.query.count()
        print(f"Total employees: {total_employees}")
        
        # Check shift roster for today
        print(f"\nShift Roster for {today}:")
        shifts_today = ShiftRoster.query.filter(ShiftRoster.date == today).all()
        print(f"Total shifts: {len(shifts_today)}")
        
        for shift in shifts_today:
            employee = User.query.get(shift.employee_id)
            shift_info = f"Employee: {employee.name} {employee.surname}, Status: {shift.status}, Hours: {shift.hours}"
            print(f"  - {shift_info}")
        
        # Count approved shifts for today
        approved_shifts = ShiftRoster.query.filter(
            and_(
                ShiftRoster.date == today,
                ShiftRoster.status == 'approved'
            )
        ).count()
        print(f"Approved shifts today: {approved_shifts}")
        
        # Unique employees on shift today (approved)
        employees_on_shift = db.session.query(func.count(func.distinct(ShiftRoster.employee_id))).filter(
            and_(
                ShiftRoster.date == today,
                ShiftRoster.status == 'approved'
            )
        ).scalar()
        print(f"Unique employees on shift today: {employees_on_shift}")
        
        # Check leave requests for today
        print(f"\nLeave Requests overlapping {today}:")
        leave_today = LeaveRequest.query.filter(
            and_(
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today
            )
        ).all()
        
        print(f"Total leave requests: {len(leave_today)}")
        for leave in leave_today:
            employee = User.query.get(leave.employee_id)
            leave_info = f"Employee: {employee.name} {employee.surname}, Status: {leave.status}, From: {leave.start_date} To: {leave.end_date}"
            print(f"  - {leave_info}")
        
        # Count approved leave for today
        employees_on_leave = db.session.query(func.count(func.distinct(LeaveRequest.employee_id))).filter(
            and_(
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today,
                LeaveRequest.status == 'approved'
            )
        ).scalar()
        print(f"Unique employees on leave today: {employees_on_leave}")
        
        print(f"\nSummary:")
        print(f"  Total employees: {total_employees}")
        print(f"  On shift: {employees_on_shift}")
        print(f"  On leave: {employees_on_leave}")
        print(f"  Available: {total_employees - employees_on_shift - employees_on_leave}")

if __name__ == '__main__':
    debug_dashboard()
