#!/usr/bin/env python3
"""
Migration script to add username and password_hash fields to the users table.
This script adds support for dual authentication (Google OAuth + username/password).

Run this script from the shift-roster-backend directory:
python migrate_user_auth_fields.py
"""

import sqlite3
import sys
import os
from pathlib import Path

def main():
    # Path to the database
    db_path = Path(__file__).parent / 'src' / 'database' / 'app.db'
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        print("Please ensure you're running this from the shift-roster-backend directory")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        needs_username = 'username' not in columns
        needs_password_hash = 'password_hash' not in columns
        needs_google_id_nullable = True  # We'll check this separately
        
        print("🔍 Checking current users table structure...")
        print(f"Current columns: {', '.join(columns)}")
        
        migrations_performed = []
        
        # Add username column if it doesn't exist
        if needs_username:
            print("➕ Adding 'username' column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN username VARCHAR(50)
            """)
            migrations_performed.append("Added 'username' column (without UNIQUE constraint)")
        else:
            print("✅ 'username' column already exists")
        
        # Add password_hash column if it doesn't exist
        if needs_password_hash:
            print("➕ Adding 'password_hash' column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN password_hash VARCHAR(255)
            """)
            migrations_performed.append("Added 'password_hash' column")
        else:
            print("✅ 'password_hash' column already exists")
        
        # Note about google_id nullable constraint
        print("\n📝 Note: The google_id column should be made nullable to support username/password users.")
        print("   This requires recreating the table in SQLite, which is more complex.")
        print("   For now, you can manually set google_id to a unique placeholder for username/password users.")
        
        # Commit the changes
        conn.commit()
        
        if migrations_performed:
            print(f"\n✅ Migration completed successfully!")
            for migration in migrations_performed:
                print(f"   - {migration}")
        else:
            print("\n✅ No migrations needed - all columns already exist!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(users)")
        columns_after = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        print(f"\n📊 Updated table structure:")
        for col in columns_after:
            print(f"   - {col}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 User Authentication Fields Migration")
    print("=" * 50)
    
    success = main()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Update your Flask application to use the new fields")
        print("   2. Add password hashing utilities (e.g., werkzeug.security)")
        print("   3. Create username/password login endpoints")
        print("   4. Update the frontend employee form to include username/password fields")
        sys.exit(0)
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)