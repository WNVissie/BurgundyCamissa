#!/usr/bin/env python3
"""
Migration script to create employee_rates table and migrate existing rate data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app
from src.models.models import db, User, EmployeeRate
from datetime import date
from sqlalchemy import text

def migrate_rates():
    app = create_app()
    with app.app_context():
        print("=== EMPLOYEE RATES MIGRATION ===")
        
        # Create the new table
        print("1. Creating employee_rates table...")
        try:
            db.create_all()
            print("   ✓ Table created successfully")
        except Exception as e:
            print(f"   ✗ Error creating table: {e}")
            return
        
        # Check if there are existing users with rates
        print("\n2. Checking existing user rates...")
        users_with_rates = User.query.filter(
            User.rate_value.isnot(None),
            User.rate_value > 0
        ).all()
        
        print(f"   Found {len(users_with_rates)} users with existing rates")
        
        # Migrate existing rates
        migrated_count = 0
        for user in users_with_rates:
            try:
                # Check if rate already migrated
                existing_rate = EmployeeRate.query.filter_by(
                    employee_id=user.id,
                    end_date=None
                ).first()
                
                if existing_rate:
                    print(f"   - {user.name} {user.surname}: Rate already migrated")
                    continue
                
                # Create new rate record
                new_rate = EmployeeRate(
                    employee_id=user.id,
                    rate_type=user.rate_type or 'weekly',  # Default to weekly if not set
                    rate_value=user.rate_value,
                    currency='ZAR',
                    effective_date=date.today(),  # Set as current
                    created_by=1,  # Assume admin user ID 1
                    notes=f"Migrated from users table on {date.today()}"
                )
                
                db.session.add(new_rate)
                migrated_count += 1
                
                print(f"   ✓ {user.name} {user.surname}: {user.rate_type} R{user.rate_value}")
                
            except Exception as e:
                print(f"   ✗ Error migrating {user.name} {user.surname}: {e}")
        
        # Commit the migration
        try:
            db.session.commit()
            print(f"\n3. Migration completed successfully!")
            print(f"   ✓ Migrated {migrated_count} employee rates")
        except Exception as e:
            db.session.rollback()
            print(f"\n3. Migration failed: {e}")
            return
        
        # Verify migration
        print("\n4. Verifying migration...")
        total_rates = EmployeeRate.query.count()
        current_rates = EmployeeRate.query.filter_by(end_date=None).count()
        
        print(f"   Total rates in new table: {total_rates}")
        print(f"   Current active rates: {current_rates}")
        
        # Show sample migrated rates
        print("\n5. Sample migrated rates:")
        sample_rates = EmployeeRate.query.filter_by(end_date=None).limit(5).all()
        for rate in sample_rates:
            user = User.query.get(rate.employee_id)
            print(f"   {user.name} {user.surname}: {rate.rate_type} R{rate.rate_value}")

if __name__ == "__main__":
    migrate_rates()
