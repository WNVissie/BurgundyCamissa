#!/usr/bin/env python3
"""
Database migration to add attachment fields to leave_requests table
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add the src directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def migrate_leave_attachments():
    """Add attachment fields to the leave_requests table"""
    
    # Database path
    db_path = os.path.join(current_dir, 'src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Migrating leave_requests table to add attachment fields...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(leave_requests);")
        columns = [col[1] for col in cursor.fetchall()]
        
        # List of new columns to add
        new_columns = [
            "attachment_filename VARCHAR(255)",
            "attachment_path VARCHAR(500)", 
            "attachment_mimetype VARCHAR(100)",
            "attachment_size INTEGER",
            "attachment_uploaded_at DATETIME"
        ]
        
        added_count = 0
        
        for column_def in new_columns:
            column_name = column_def.split()[0]
            
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE leave_requests ADD COLUMN {column_def};")
                    print(f"✅ Added column: {column_name}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"⚠️  Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        
        if added_count > 0:
            print(f"\n🎉 Successfully added {added_count} new columns to leave_requests table!")
            
            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(current_dir, 'src', 'static', 'uploads', 'leave_attachments')
            os.makedirs(uploads_dir, exist_ok=True)
            print(f"📁 Created uploads directory: {uploads_dir}")
            
        else:
            print("\n⚠️  No columns were added (all already exist)")
        
        # Show updated table structure
        print("\n📋 Updated table structure:")
        cursor.execute("PRAGMA table_info(leave_requests);")
        columns_info = cursor.fetchall()
        
        print("Column Name".ljust(25) + "Type".ljust(15) + "Nullable".ljust(10))
        print("-" * 50)
        for col_info in columns_info:
            cid, name, type_, notnull, default, pk = col_info
            nullable = "NO" if notnull else "YES"
            print(f"{name.ljust(25)}{type_.ljust(15)}{nullable.ljust(10)}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Leave Attachment Migration")
    print("=" * 50)
    
    if migrate_leave_attachments():
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your Flask app models")
        print("2. Update leave request API endpoints")
        print("3. Update frontend forms and views")
    else:
        print("\n❌ Migration failed!")
