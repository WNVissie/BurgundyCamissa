#!/usr/bin/env python3
"""
Seed the hourly_rates table with example data
- Non-supervisors: R40-R80 per hour
- Supervisors/Managers/Admin: R80-R120 per hour
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.models import db, HourlyRates, User, Role
from src.config import Config
from flask import Flask
from datetime import date
import random

def seed_hourly_rates():
    """Seed the hourly_rates table with example data for all employees"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("🌱 Seeding hourly rates...")
        print("=" * 50)
        
        # Get all users
        users = User.query.all()
        print(f"Found {len(users)} users in the database")
        
        # Define rate ranges based on roles
        rate_ranges = {
            'Admin': (100, 120),        # R100-R120 per hour
            'Manager': (80, 110),       # R80-R110 per hour
            'Supervisor': (70, 90),     # R70-R90 per hour
            'Employee': (40, 70),       # R40-R70 per hour
            'default': (40, 60)         # Default for unknown roles
        }
        
        # Get admin user for created_by (assuming first admin user)
        admin_user = User.query.join(Role).filter(Role.name == 'Admin').first()
        created_by_id = admin_user.id if admin_user else 1
        
        seeded_count = 0
        skipped_count = 0
        
        for user in users:
            try:
                # Check if user already has a rate
                existing_rate = HourlyRates.get_current_rate(user.id)
                if existing_rate:
                    print(f"⚠️  {user.name} {user.surname} already has a rate: R{existing_rate.rate_per_hr}/hr")
                    skipped_count += 1
                    continue
                
                # Determine rate range based on role
                role_name = user.role_ref.name if user.role_ref else 'default'
                min_rate, max_rate = rate_ranges.get(role_name, rate_ranges['default'])
                
                # Generate random rate within range (rounded to nearest R5)
                rate = round(random.uniform(min_rate, max_rate) / 5) * 5
                
                # Create new hourly rate
                new_rate = HourlyRates(
                    employee_id=user.id,
                    rate_per_hr=rate,
                    currency='ZAR',
                    effective_date=date.today(),
                    created_by=created_by_id
                )
                
                db.session.add(new_rate)
                seeded_count += 1
                
                # Show role info
                role_display = role_name if role_name != 'default' else 'Unknown'
                designation = user.designation_ref.designation_name if user.designation_ref else 'No Designation'
                
                print(f"✅ {user.name} {user.surname}")
                print(f"   Role: {role_display} | Designation: {designation}")
                print(f"   Rate: R{rate}/hr (Range: R{min_rate}-R{max_rate})")
                print()
                
            except Exception as e:
                print(f"❌ Error creating rate for {user.name} {user.surname}: {e}")
        
        if seeded_count > 0:
            # Commit all changes
            db.session.commit()
            print("=" * 50)
            print(f"🎉 Successfully seeded {seeded_count} hourly rates!")
            print(f"⚠️  Skipped {skipped_count} users (already have rates)")
            
            # Show summary by role
            print("\n📊 Rate Summary by Role:")
            print("-" * 30)
            
            role_summary = db.session.query(
                Role.name,
                db.func.count(HourlyRates.rate_id).label('count'),
                db.func.min(HourlyRates.rate_per_hr).label('min_rate'),
                db.func.max(HourlyRates.rate_per_hr).label('max_rate'),
                db.func.avg(HourlyRates.rate_per_hr).label('avg_rate')
            ).join(User, HourlyRates.employee_id == User.id)\
             .join(Role, User.role_id == Role.id)\
             .group_by(Role.name).all()
            
            for role_name, count, min_rate, max_rate, avg_rate in role_summary:
                print(f"{role_name:12} | {count:2} employees | R{min_rate:5.0f} - R{max_rate:5.0f} | Avg: R{avg_rate:5.1f}")
        
        else:
            print("⚠️  No rates were seeded.")

def show_current_rates():
    """Display all current hourly rates"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("\n📋 Current Hourly Rates:")
        print("=" * 60)
        
        rates = db.session.query(
            HourlyRates.rate_id,
            HourlyRates.employee_id,
            User.name,
            User.surname,
            Role.name.label('role_name'),
            HourlyRates.rate_per_hr,
            HourlyRates.effective_date
        ).join(User, HourlyRates.employee_id == User.id)\
         .join(Role, User.role_id == Role.id)\
         .order_by(Role.name, HourlyRates.rate_per_hr.desc()).all()
        
        if rates:
            print(f"{'ID':<3} | {'Name':<20} | {'Role':<10} | {'Rate':<8} | {'Effective'}")
            print("-" * 60)
            
            for rate_id, emp_id, name, surname, role_name, rate_per_hr, eff_date in rates:
                full_name = f"{name} {surname}"[:20]
                print(f"{rate_id:<3} | {full_name:<20} | {role_name:<10} | R{rate_per_hr:>6.0f} | {eff_date}")
        else:
            print("No rates found.")

if __name__ == "__main__":
    print("Seeding Hourly Rates Table")
    print("=" * 50)
    
    # First create the table if it doesn't exist
    try:
        # Run the migration first
        print("Ensuring hourly_rates table exists...")
        import subprocess
        result = subprocess.run([
            'python', 'migrate_hourly_rates.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode != 0:
            print("Creating table manually...")
            # Create table manually if migration fails
            from src.models.models import db
            app = Flask(__name__)
            app.config.from_object(Config)
            db.init_app(app)
            
            with app.app_context():
                db.create_all()
                print("✅ Tables created successfully!")
    
    except Exception as e:
        print(f"Note: {e}")
    
    # Seed the data
    seed_hourly_rates()
    
    # Show the results
    show_current_rates()
