import sqlite3
import os

def verify_database(db_path):
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("🗃️ Database Tables Found:")
        total_records = 0
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_records += count
            print(f"  📋 {table_name}: {count} records")
        
        print(f"\n📊 Total Records: {total_records}")
        
        # Check for critical tables
        critical_tables = ['user', 'employee', 'roster', 'timesheet', 'leave_request', 'community_post']
        missing_tables = []
        
        table_names = [t[0] for t in tables]
        for critical in critical_tables:
            if critical not in table_names:
                missing_tables.append(critical)
        
        if missing_tables:
            print(f"⚠️ Missing critical tables: {missing_tables}")
        else:
            print("✅ All critical tables present")
        
        # Show sample data from key tables
        print("\n📋 Sample Data:")
        for table in ['user', 'employee']:
            if table in table_names:
                try:
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    rows = cursor.fetchall()
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    print(f"\n  🔍 {table.upper()} table (showing first 3 rows):")
                    print(f"    Columns: {', '.join(columns)}")
                    for i, row in enumerate(rows, 1):
                        print(f"    Row {i}: {row[:3]}..." if len(row) > 3 else f"    Row {i}: {row}")
                except Exception as e:
                    print(f"    ⚠️ Could not preview {table}: {e}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    # Try to find database in common locations
    possible_paths = [
        "app.db",
        "src/database/app.db",
        "shift-roster-backend/src/database/app.db"
    ]
    
    db_found = False
    for db_path in possible_paths:
        if os.path.exists(db_path):
            print(f"🎯 Found database at: {db_path}")
            verify_database(db_path)
            db_found = True
            break
    
    if not db_found:
        print("❌ Database not found in expected locations:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nPlease run this script from the correct directory or specify the database path.")