#!/usr/bin/env python3
"""
Migration script to create the notifications table for admin alerts.
Run this script to add the notifications table to your existing database.
"""
import sqlite3
import os
from datetime import datetime

def create_notifications_table():
    """Create the notifications table in the SQLite database."""
    db_path = os.path.join('src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='notifications'
        """)
        
        if cursor.fetchone():
            print("Notifications table already exists.")
            conn.close()
            return True
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                ref_id INTEGER,
                message TEXT NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✓ Notifications table created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating notifications table: {e}")
        return False

if __name__ == "__main__":
    print("Creating notifications table...")
    if create_notifications_table():
        print("Migration completed successfully!")
    else:
        print("Migration failed!")