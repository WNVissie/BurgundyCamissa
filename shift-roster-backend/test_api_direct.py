#!/usr/bin/env python3
"""
Direct test of the cost calculation logic without API calls
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.models import db, User, Timesheet
from src.config import Config
from flask import Flask
from datetime import date, datetime
from sqlalchemy import func, and_

# Create Flask app and configure database
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def test_cost_calculation():
    with app.app_context():
        print("Testing Cost Calculation Logic")
        print("=" * 50)
        
        # Get data similar to what the API does
        today = date.today()
        start_date_obj = today.replace(day=1)  # Start of month
        end_date_obj = today
        
        print(f"Date range: {start_date_obj} to {end_date_obj}")
        print()
        
        # Get cost data from approved timesheets
        cost_data = db.session.query(
            User.id,
            User.name,
            User.surname,
            User.rate_type,
            User.rate_value,
            func.sum(Timesheet.hours_worked).label('total_hours')
        ).join(Timesheet, User.id == Timesheet.employee_id).filter(
            and_(
                Timesheet.date >= start_date_obj,
                Timesheet.date <= end_date_obj,
                Timesheet.status == 'approved',
                User.rate_value.isnot(None)
            )
        ).group_by(User.id, User.name, User.surname, User.rate_type, User.rate_value).all()
        
        print(f"Found {len(cost_data)} employees with approved timesheets and rate data")
        print()
        
        total_cost = 0
        total_hours = 0
        
        for employee_id, name, surname, rate_type, rate_value, hours in cost_data:
            if rate_value and hours:
                hours = float(hours)
                rate = float(rate_value)
                
                print(f"Employee: {name} {surname}")
                print(f"  Rate Type: {rate_type}")
                print(f"  Rate Value: R{rate}")
                print(f"  Hours Worked: {hours}")
                
                # Convert rate to hourly rate first
                if rate_type == 'hourly':
                    hourly_rate = rate
                    conversion = "direct"
                elif rate_type == 'daily':
                    hourly_rate = rate / 8
                    conversion = f"R{rate} ÷ 8 hours"
                elif rate_type == 'weekly':
                    hourly_rate = rate / 40
                    conversion = f"R{rate} ÷ 40 hours"
                elif rate_type == 'monthly':
                    hourly_rate = rate / 160
                    conversion = f"R{rate} ÷ 160 hours"
                else:
                    hourly_rate = rate
                    conversion = "default to hourly"
                
                cost = hours * hourly_rate
                
                print(f"  Hourly Rate: R{hourly_rate:.2f} ({conversion})")
                print(f"  Total Cost: {hours} × R{hourly_rate:.2f} = R{cost:.2f}")
                print()
                
                total_cost += cost
                total_hours += hours
        
        print(f"TOTALS:")
        print(f"Total Hours: {total_hours}")
        print(f"Total Cost: R{total_cost:.2f}")
        if total_hours > 0:
            print(f"Average Cost per Hour: R{total_cost/total_hours:.2f}")

if __name__ == "__main__":
    test_cost_calculation()
