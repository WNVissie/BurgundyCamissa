#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.models.models import User, Timesheet, db
from sqlalchemy import func

def debug_cost_data():
    app = create_app()
    with app.app_context():
        print("=== DEBUGGING COST DATA ===")
        
        # Check users with rates
        print("\n1. Users with rate information:")
        users_with_rates = User.query.filter(User.rate_value.isnot(None)).all()
        for user in users_with_rates:
            print(f"   {user.name} {user.surname}: {user.rate_type} = R{user.rate_value}")
        
        if not users_with_rates:
            print("   NO USERS WITH RATES FOUND!")
            return
        
        # Check approved timesheets with hours_worked
        print("\n2. Approved timesheets with hours_worked:")
        approved_timesheets = Timesheet.query.filter(
            Timesheet.hours_worked.isnot(None),
            Timesheet.hours_worked > 0,
            Timesheet.status == 'approved'
        ).limit(10).all()
        
        for ts in approved_timesheets:
            user = User.query.get(ts.employee_id)
            print(f"   User {user.name if user else 'Unknown'}: {ts.hours_worked} hours on {ts.date} (Status: {ts.status})")
        
        if not approved_timesheets:
            print("   NO APPROVED TIMESHEETS WITH HOURS FOUND!")
            
            # Check all timesheets
            all_timesheets = Timesheet.query.limit(10).all()
            print(f"\n   Total timesheets in database: {Timesheet.query.count()}")
            for ts in all_timesheets:
                user = User.query.get(ts.employee_id)
                print(f"   User {user.name if user else 'Unknown'}: {ts.hours_worked} hours on {ts.date} (Status: {ts.status})")
        
        # Check if any users with rates have approved timesheets
        print("\n3. Users with rates AND approved timesheets:")
        user_ids_with_rates = [u.id for u in users_with_rates]
        timesheets_for_rate_users = Timesheet.query.filter(
            Timesheet.employee_id.in_(user_ids_with_rates),
            Timesheet.hours_worked.isnot(None),
            Timesheet.hours_worked > 0,
            Timesheet.status == 'approved'
        ).all()
        
        for ts in timesheets_for_rate_users:
            user = User.query.get(ts.employee_id)
            print(f"   {user.name} {user.surname}: {ts.hours_worked} hours on {ts.date} (Rate: {user.rate_type} R{user.rate_value})")
        
        if not timesheets_for_rate_users:
            print("   NO APPROVED TIMESHEETS FOUND FOR USERS WITH RATES!")
        
        print(f"\nSummary:")
        print(f"- Users with rates: {len(users_with_rates)}")
        print(f"- Approved timesheets with hours: {len(approved_timesheets)}")
        print(f"- Approved timesheets for users with rates: {len(timesheets_for_rate_users)}")

if __name__ == "__main__":
    debug_cost_data()
