import sqlite3
import os

# Connect to the database
db_path = r"c:\Users\wanda\Documents\SMART Apps\Davey\employee-shift-roster-app Manus\shift-roster-backend\src\database\app.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== CHECKING DATABASE ===")
    
    # Check users with rates
    print("\n1. Users with rates:")
    cursor.execute("SELECT name, surname, rate_type, `rate_-value` FROM users WHERE `rate_-value` IS NOT NULL")
    users_with_rates = cursor.fetchall()
    for user in users_with_rates:
        print(f"   {user[0]} {user[1]}: {user[2]} = R{user[3]}")
    
    if not users_with_rates:
        print("   NO USERS WITH RATES FOUND!")
    
    # Check timesheets
    print("\n2. Timesheet data:")
    cursor.execute("SELECT COUNT(*) FROM timesheets")
    total_timesheets = cursor.fetchone()[0]
    print(f"   Total timesheets: {total_timesheets}")
    
    if total_timesheets > 0:
        cursor.execute("SELECT user_id, date, hours_worked, status FROM timesheets WHERE hours_worked IS NOT NULL AND hours_worked > 0 LIMIT 10")
        timesheets = cursor.fetchall()
        for ts in timesheets:
            print(f"   User {ts[0]}: {ts[2]} hours on {ts[1]} (Status: {ts[3]})")
        
        # Check approved timesheets
        cursor.execute("SELECT COUNT(*) FROM timesheets WHERE status = 'approved' AND hours_worked > 0")
        approved_count = cursor.fetchone()[0]
        print(f"   Approved timesheets with hours: {approved_count}")
    
    # Check if there are any timesheets for users with rates
    if users_with_rates:
        user_ids = [str(u[0]) for u in users_with_rates if u[0]]  # Get user IDs
        user_names = {u[0]: f"{u[1]} {u[2]}" for u in users_with_rates}  # Map ID to name
        
        # Get user IDs from users table
        cursor.execute("SELECT id, name, surname FROM users WHERE `rate_-value` IS NOT NULL")
        rate_users = cursor.fetchall()
        user_ids_with_rates = [str(u[0]) for u in rate_users]
        user_names = {u[0]: f"{u[1]} {u[2]}" for u in rate_users}
        
        if user_ids_with_rates:
            placeholders = ','.join(['?'] * len(user_ids_with_rates))
            cursor.execute(f"""
                SELECT user_id, date, hours_worked, status 
                FROM timesheets 
                WHERE user_id IN ({placeholders}) 
                AND hours_worked > 0 
                AND status = 'approved'
                LIMIT 10
            """, user_ids_with_rates)
            
            rate_user_timesheets = cursor.fetchall()
            print(f"\n3. Approved timesheets for users with rates:")
            for ts in rate_user_timesheets:
                user_name = user_names.get(ts[0], f"User {ts[0]}")
                print(f"   {user_name}: {ts[2]} hours on {ts[1]}")
            
            if not rate_user_timesheets:
                print("   NO APPROVED TIMESHEETS FOR USERS WITH RATES!")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")
