#!/usr/bin/env python3
"""
Database migration script to create the hourly_rates table
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.models import db, HourlyRates
from src.config import Config
from flask import Flask
import sqlite3

def create_hourly_rates_table():
    """Create the hourly_rates table in the database"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    # SQL to create the table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS hourly_rates (
        rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        rate_per_hr DECIMAL(10,2) NOT NULL,
        currency VARCHAR(3) DEFAULT 'ZAR' NOT NULL,
        effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
        end_date DATE NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER NULL,
        
        FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
    );
    """
    
    # Create indexes
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS ix_hourly_rates_employee_effective ON hourly_rates(employee_id, effective_date);",
        "CREATE INDEX IF NOT EXISTS ix_hourly_rates_active ON hourly_rates(employee_id, effective_date, end_date);"
    ]
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creating hourly_rates table...")
        cursor.execute(create_table_sql)
        
        print("Creating indexes...")
        for index_sql in create_indexes_sql:
            cursor.execute(index_sql)
        
        conn.commit()
        print("✅ hourly_rates table created successfully!")
        
        # Display table structure
        cursor.execute("PRAGMA table_info(hourly_rates);")
        columns = cursor.fetchall()
        
        print("\nTable structure:")
        print("Column Name".ljust(20) + "Type".ljust(15) + "Null".ljust(8) + "Default".ljust(15) + "PK")
        print("-" * 70)
        for col in columns:
            cid, name, type_, notnull, default, pk = col
            null_str = "NO" if notnull else "YES"
            default_str = str(default) if default else ""
            pk_str = "YES" if pk else ""
            print(f"{name.ljust(20)}{type_.ljust(15)}{null_str.ljust(8)}{default_str.ljust(15)}{pk_str}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Error creating table: {e}")
        return False
    
    return True

def migrate_existing_rates():
    """Migrate existing hourly rates from users table to hourly_rates table"""
    
    # Create Flask app context for ORM operations
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        from src.models.models import User
        
        # Get users with hourly rates
        users_with_hourly_rates = User.query.filter(
            User.rate_type == 'hourly',
            User.rate_value.isnot(None)
        ).all()
        
        print(f"\nFound {len(users_with_hourly_rates)} users with hourly rates to migrate...")
        
        migrated_count = 0
        for user in users_with_hourly_rates:
            try:
                # Check if rate already exists
                existing_rate = HourlyRates.get_current_rate(user.id)
                if existing_rate:
                    print(f"⚠️  Rate already exists for {user.name} {user.surname}")
                    continue
                
                # Create new hourly rate
                new_rate = HourlyRates(
                    employee_id=user.id,
                    rate_per_hr=user.rate_value,
                    currency='ZAR',
                    created_by=1  # Assuming admin user ID 1
                )
                
                db.session.add(new_rate)
                migrated_count += 1
                print(f"✅ Migrated rate for {user.name} {user.surname}: R{user.rate_value}/hr")
                
            except Exception as e:
                print(f"❌ Error migrating rate for {user.name} {user.surname}: {e}")
        
        if migrated_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully migrated {migrated_count} hourly rates!")
        else:
            print("\n⚠️  No rates to migrate.")

if __name__ == "__main__":
    print("Creating hourly_rates table...")
    
    if create_hourly_rates_table():
        print("\nMigrating existing hourly rates...")
        migrate_existing_rates()
        print("\n🎉 Migration completed!")
    else:
        print("\n❌ Failed to create table. Migration aborted.")
