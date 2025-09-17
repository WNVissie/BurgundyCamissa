#!/usr/bin/env python3
"""
Seed hourly rates for all employees
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
from datetime import date
import random

def seed_rates():
    # Create Flask app context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("🌱 Seeding Hourly Rates...")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users")
        
        # Rate ranges by role
        rate_ranges = {
            'Admin': (100, 120),        # R100-R120 per hour
            'Manager': (80, 110),       # R80-R110 per hour
            'Supervisor': (70, 90),     # R70-R90 per hour
            'Employee': (40, 70),       # R40-R70 per hour
        }
        
        # Get admin user for created_by
        admin_user = User.query.join(Role).filter(Role.name == 'Admin').first()
        created_by_id = admin_user.id if admin_user else 1
        
        seeded_count = 0
        
        for user in users:
            # Check if already has rate
            existing = HourlyRates.query.filter_by(employee_id=user.id).first()
            if existing:
                print(f"⚠️  {user.name} {user.surname} - already has rate")
                continue
            
            # Get role and rate range
            role_name = user.role_ref.name if user.role_ref else 'Employee'
            min_rate, max_rate = rate_ranges.get(role_name, (40, 70))
            
            # Generate random rate (rounded to nearest R5)
            rate = round(random.uniform(min_rate, max_rate) / 5) * 5
            
            # Create rate record
            new_rate = HourlyRates(
                employee_id=user.id,
                rate_per_hr=rate,
                currency='ZAR',
                effective_date=date.today(),
                created_by=created_by_id
            )
            
            db.session.add(new_rate)
            seeded_count += 1
            
            print(f"✅ {user.name} {user.surname} ({role_name}) - R{rate}/hr")
        
        # Commit changes
        if seeded_count > 0:
            db.session.commit()
            print(f"\n🎉 Seeded {seeded_count} hourly rates!")
            
            # Show summary
            print("\n📊 Summary by Role:")
            for role_name in ['Admin', 'Manager', 'Supervisor', 'Employee']:
                count = db.session.query(HourlyRates).join(User).join(Role).filter(Role.name == role_name).count()
                if count > 0:
                    avg_rate = db.session.query(db.func.avg(HourlyRates.rate_per_hr)).join(User).join(Role).filter(Role.name == role_name).scalar()
                    print(f"  {role_name}: {count} employees, avg R{avg_rate:.0f}/hr")
        else:
            print("⚠️  No rates seeded (all users already have rates)")

if __name__ == "__main__":
    seed_rates()
