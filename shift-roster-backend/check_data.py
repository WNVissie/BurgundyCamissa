#!/usr/bin/env python3

import sys
sys.path.append('src')

from src.models.models import db, User, ShiftRoster, LeaveRequest, Shift
from src.config import Config
from flask import Flask
from datetime import date, datetime

# Create Flask app and configure database
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    today = date.today()
    print(f"Today's date: {today}")
    print()
    
    # Check total users
    total_users = User.query.count()
    print(f"Total users: {total_users}")
    
    # Check shift rosters
    total_shifts = ShiftRoster.query.count()
    print(f"Total shift rosters: {total_shifts}")
    
    # Check shifts for today
    todays_shifts = ShiftRoster.query.filter(ShiftRoster.date == today).all()
    print(f"Shifts for today ({today}): {len(todays_shifts)}")
    
    # Check approved shifts for today
    approved_today = ShiftRoster.query.filter(
        ShiftRoster.date == today,
        ShiftRoster.status == 'approved'
    ).all()
    print(f"Approved shifts for today: {len(approved_today)}")
    
    # Check all shift dates
    print("\nAll shift dates in database:")
    shift_dates = db.session.query(ShiftRoster.date, ShiftRoster.status).distinct().order_by(ShiftRoster.date).all()
    for date_obj, status in shift_dates[:10]:  # Show first 10
        print(f"  {date_obj} - {status}")
    
    print(f"\nTotal unique shift dates: {len(shift_dates)}")
    
    # Check leave requests
    total_leave = LeaveRequest.query.count()
    print(f"\nTotal leave requests: {total_leave}")
    
    # Check leave for today
    leave_today = LeaveRequest.query.filter(
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today,
        LeaveRequest.status == 'approved'
    ).all()
    print(f"Approved leave covering today: {len(leave_today)}")
    
    # Check shifts table
    shifts = Shift.query.all()
    print(f"\nAvailable shift types: {len(shifts)}")
    for shift in shifts:
        print(f"  {shift.name}")
