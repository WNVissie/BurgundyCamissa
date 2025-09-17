#!/usr/bin/env python3
"""
Simple test to see if we can connect to the database
"""
import sys
import os

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

try:
    from models.models import db, HourlyRates, User, Role
    from config import Config
    from flask import Flask
    from datetime import date
    import random
    
    print("✅ All imports successful!")
    
    # Create Flask app context
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Test database connection
        users = User.query.all()
        print(f"✅ Database connection successful! Found {len(users)} users.")
        
        # Create the table if it doesn't exist
        db.create_all()
        print("✅ Tables created/verified!")
        
        # Test if hourly_rates table exists
        try:
            existing_rates = HourlyRates.query.count()
            print(f"✅ HourlyRates table exists with {existing_rates} records.")
        except Exception as e:
            print(f"❌ HourlyRates table issue: {e}")
            
        # Show users and their roles
        print("\n📋 Current Users:")
        for user in users[:5]:  # Show first 5 users
            role_name = user.role_ref.name if user.role_ref else 'No Role'
            print(f"  {user.name} {user.surname} - {role_name}")
        
        if len(users) > 5:
            print(f"  ... and {len(users) - 5} more users")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
