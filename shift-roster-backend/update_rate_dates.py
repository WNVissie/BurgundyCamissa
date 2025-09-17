#!/usr/bin/env python3
"""
Update all hourly rates to be effective from 07/09/2025
"""
import sys
import os
from datetime import date

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from models.models import db, HourlyRates, User
from config import Config
from flask import Flask

def update_effective_dates():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        print("📅 Updating Hourly Rates Effective Dates")
        print("=" * 50)
        
        # New effective date: September 7, 2025
        new_effective_date = date(2025, 9, 7)
        
        # Get all hourly rates
        all_rates = HourlyRates.query.all()
        print(f"Found {len(all_rates)} hourly rates to update")
        print(f"Setting effective date to: {new_effective_date}")
        print()
        
        updated_count = 0
        
        for rate in all_rates:
            # Get employee name for display
            employee = User.query.get(rate.employee_id)
            employee_name = f"{employee.name} {employee.surname}" if employee else f"Employee ID {rate.employee_id}"
            
            old_date = rate.effective_date
            rate.effective_date = new_effective_date
            
            print(f"✅ {employee_name}: {old_date} → {new_effective_date}")
            updated_count += 1
        
        # Commit all changes
        if updated_count > 0:
            db.session.commit()
            print(f"\n🎉 Successfully updated {updated_count} effective dates!")
            
            # Verify the changes
            print("\n📋 Verification - First 5 rates:")
            verification_rates = db.session.query(
                HourlyRates.rate_id,
                User.name,
                User.surname,
                HourlyRates.rate_per_hr,
                HourlyRates.effective_date
            ).join(User, HourlyRates.employee_id == User.id)\
             .limit(5).all()
            
            for rate_id, name, surname, rate_per_hr, eff_date in verification_rates:
                print(f"  {name} {surname}: R{rate_per_hr}/hr (effective {eff_date})")
        else:
            print("⚠️  No rates were updated")

if __name__ == "__main__":
    update_effective_dates()
