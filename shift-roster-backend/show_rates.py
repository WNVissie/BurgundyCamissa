#!/usr/bin/env python3
"""
Display the seeded hourly rates
"""
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from models.models import db, HourlyRates, User, Role
from config import Config
from flask import Flask

def show_rates():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("📋 Hourly Rates Summary")
        print("=" * 60)
        
        # Get all rates with user info
        rates = db.session.query(
            HourlyRates.rate_id,
            User.name,
            User.surname,
            Role.name.label('role_name'),
            HourlyRates.rate_per_hr,
            HourlyRates.effective_date
        ).join(User, HourlyRates.employee_id == User.id)\
         .join(Role, User.role_id == Role.id)\
         .order_by(HourlyRates.rate_per_hr.desc()).all()
        
        print(f"{'ID':<3} | {'Name':<25} | {'Role':<10} | {'Rate/Hr':<8} | {'Effective'}")
        print("-" * 60)
        
        role_counts = {}
        role_totals = {}
        
        for rate_id, name, surname, role_name, rate_per_hr, eff_date in rates:
            full_name = f"{name} {surname}"[:25]
            print(f"{rate_id:<3} | {full_name:<25} | {role_name:<10} | R{rate_per_hr:>6.0f} | {eff_date}")
            
            # Track role stats
            if role_name not in role_counts:
                role_counts[role_name] = 0
                role_totals[role_name] = 0
            role_counts[role_name] += 1
            role_totals[role_name] += float(rate_per_hr)
        
        print("\n📊 Summary by Role:")
        print("-" * 40)
        for role_name in ['Admin', 'Manager', 'Employee']:
            if role_name in role_counts:
                count = role_counts[role_name]
                avg = role_totals[role_name] / count
                print(f"{role_name:<10}: {count:>2} employees | Avg: R{avg:>5.0f}/hr")
        
        print(f"\nTotal employees with rates: {len(rates)}")

if __name__ == "__main__":
    show_rates()
