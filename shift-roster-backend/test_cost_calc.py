import sqlite3
import os

# Connect to the database
db_path = r"c:\Users\wanda\Documents\SMART Apps\Davey\employee-shift-roster-app Manus\shift-roster-backend\src\database\app.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== DEBUGGING COST CALCULATION ===")
    
    # Test the exact query from our analytics
    print("\n1. Testing the cost analytics query:")
    query = """
    SELECT 
        u.id,
        u.name,
        u.surname,
        u.rate_type,
        u.`rate_-value`,
        SUM(t.hours_worked) as total_hours
    FROM users u
    JOIN timesheets t ON u.id = t.employee_id
    WHERE t.status = 'approved'
        AND u.`rate_-value` IS NOT NULL
        AND t.hours_worked > 0
    GROUP BY u.id, u.name, u.surname, u.rate_type, u.`rate_-value`
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"Found {len(results)} employees with cost data:")
    total_cost = 0
    
    for row in results:
        emp_id, name, surname, rate_type, rate_value, hours = row
        print(f"\nEmployee: {name} {surname}")
        print(f"  Rate Type: {rate_type}, Rate Value: R{rate_value}")
        print(f"  Total Hours: {hours}")
        
        # Calculate cost based on rate type
        cost = 0
        if rate_type == 'weekly' and hours and rate_value:
            weeks = float(hours) / 40
            cost = weeks * float(rate_value)
            print(f"  Calculation: {hours} hours / 40 * R{rate_value} = R{cost:.2f}")
        elif rate_type == 'monthly' and hours and rate_value:
            months = float(hours) / 160
            cost = months * float(rate_value)
            print(f"  Calculation: {hours} hours / 160 * R{rate_value} = R{cost:.2f}")
        elif rate_type == 'daily' and hours and rate_value:
            days = float(hours) / 8
            cost = days * float(rate_value)
            print(f"  Calculation: {hours} hours / 8 * R{rate_value} = R{cost:.2f}")
        elif rate_type == 'hourly' and hours and rate_value:
            cost = float(hours) * float(rate_value)
            print(f"  Calculation: {hours} hours * R{rate_value} = R{cost:.2f}")
        
        total_cost += cost
        print(f"  Cost: R{cost:.2f}")
    
    print(f"\nTotal Cost: R{total_cost:.2f}")
    
    # Also check what's in the timesheets table
    print("\n2. Sample approved timesheets:")
    cursor.execute("""
        SELECT employee_id, date, hours_worked, status 
        FROM timesheets 
        WHERE status = 'approved' AND hours_worked > 0
        LIMIT 5
    """)
    timesheets = cursor.fetchall()
    for ts in timesheets:
        print(f"  Employee ID: {ts[0]}, Date: {ts[1]}, Hours: {ts[2]}, Status: {ts[3]}")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")
