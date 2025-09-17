import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.models import db, User, Timesheet
from src.main import app
from datetime import date, timedelta

with app.app_context():
    print("=== Users with Rate Data ===")
    users = User.query.filter(User.rate_value.isnot(None)).all()
    for user in users:
        print(f"{user.name} {user.surname}: {user.rate_type} - R{user.rate_value}")
    
    print(f"\nTotal users with rates: {len(users)}")
    
    if len(users) == 0:
        print("\n=== All Users (first 10) ===")
        all_users = User.query.limit(10).all()
        for user in all_users:
            rate_info = f"{user.rate_type} - R{user.rate_value}" if user.rate_value else "No rate"
            print(f"{user.name} {user.surname}: {rate_info}")
    
    print("\n=== Recent Timesheets (last 10) ===")
    timesheets = Timesheet.query.filter(Timesheet.status.in_(['approved', 'accepted'])).order_by(Timesheet.date.desc()).limit(10).all()
    print(f"Found {len(timesheets)} approved timesheets")
    for ts in timesheets:
        print(f"Employee {ts.employee.name} {ts.employee.surname}: {ts.hours_worked}h on {ts.date}")
        
    print("\n=== Checking specific users (Wanda & Denzil) ===")
    wanda = User.query.filter(User.name.ilike('%wanda%')).first()
    if wanda:
        print(f"Wanda: {wanda.rate_type} - R{wanda.rate_value}")
        wanda_timesheets = Timesheet.query.filter(Timesheet.employee_id == wanda.id).all()
        print(f"  Timesheets: {len(wanda_timesheets)}")
        for ts in wanda_timesheets[:3]:
            print(f"    {ts.date}: {ts.hours_worked}h ({ts.status})")
    
    denzil = User.query.filter(User.name.ilike('%denzil%')).first()
    if denzil:
        print(f"Denzil: {denzil.rate_type} - R{denzil.rate_value}")
        denzil_timesheets = Timesheet.query.filter(Timesheet.employee_id == denzil.id).all()
        print(f"  Timesheets: {len(denzil_timesheets)}")
        for ts in denzil_timesheets[:3]:
            print(f"    {ts.date}: {ts.hours_worked}h ({ts.status})")
    
    # Test calculation
    print("\n=== Test Cost Calculation ===")
    if wanda and wanda.rate_value:
        print(f"Wanda rate: R{wanda.rate_value} per {wanda.rate_type}")
        if wanda.rate_type == 'weekly':
            # For 40 hours worked in a week
            test_hours = 40
            weeks = test_hours / 40
            cost = weeks * float(wanda.rate_value)
            print(f"  40 hours = {weeks} weeks = R{cost}")
        
    if denzil and denzil.rate_value:
        print(f"Denzil rate: R{denzil.rate_value} per {denzil.rate_type}")
        if denzil.rate_type == 'weekly':
            # For 40 hours worked in a week
            test_hours = 40
            weeks = test_hours / 40
            cost = weeks * float(denzil.rate_value)
            print(f"  40 hours = {weeks} weeks = R{cost}")
