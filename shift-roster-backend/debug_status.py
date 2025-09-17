import sqlite3
from datetime import date, timedelta

# Connect to the database
conn = sqlite3.connect('src/database/app.db')
cursor = conn.cursor()

today = date.today()
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)

print(f"Today: {today}")
print(f"This week: {monday} to {sunday}")
print("=" * 50)

# Check all shifts for today with their statuses
print("SHIFTS FOR TODAY:")
cursor.execute("""
    SELECT sr.id, sr.employee_id, sr.date, sr.status, sr.hours, u.name, u.surname 
    FROM shift_roster sr 
    JOIN users u ON sr.employee_id = u.id 
    WHERE sr.date = ?
    ORDER BY sr.employee_id
""", (today.isoformat(),))
shifts_today = cursor.fetchall()
print(f"Total shifts today: {len(shifts_today)}")
for shift in shifts_today:
    print(f"  ID={shift[0]}, Employee={shift[5]} {shift[6]}, Status='{shift[3]}', Hours={shift[4]}")

# Check all unique statuses in shift_roster
print("\nALL SHIFT STATUSES IN DATABASE:")
cursor.execute("SELECT DISTINCT status FROM shift_roster WHERE status IS NOT NULL")
all_statuses = cursor.fetchall()
for status in all_statuses:
    cursor.execute("SELECT COUNT(*) FROM shift_roster WHERE status = ?", (status[0],))
    count = cursor.fetchone()[0]
    print(f"  '{status[0]}': {count} records")

# Check shifts for this week
print(f"\nSHIFTS FOR THIS WEEK ({monday} to {sunday}):")
cursor.execute("""
    SELECT sr.date, sr.status, COUNT(*) as count, COUNT(DISTINCT sr.employee_id) as unique_employees
    FROM shift_roster sr 
    WHERE sr.date >= ? AND sr.date <= ?
    GROUP BY sr.date, sr.status
    ORDER BY sr.date, sr.status
""", (monday.isoformat(), sunday.isoformat()))
shifts_week = cursor.fetchall()
for shift in shifts_week:
    print(f"  {shift[0]}: Status='{shift[1]}', Count={shift[2]}, Unique Employees={shift[3]}")

# Check leave requests for today
print(f"\nLEAVE REQUESTS FOR TODAY ({today}):")
cursor.execute("""
    SELECT lr.id, lr.employee_id, lr.start_date, lr.end_date, lr.status, u.name, u.surname 
    FROM leave_requests lr 
    JOIN users u ON lr.employee_id = u.id 
    WHERE lr.start_date <= ? AND lr.end_date >= ?
    ORDER BY lr.employee_id
""", (today.isoformat(), today.isoformat()))
leave_today = cursor.fetchall()
print(f"Total leave requests today: {len(leave_today)}")
for leave in leave_today:
    print(f"  ID={leave[0]}, Employee={leave[5]} {leave[6]}, Status='{leave[4]}', From={leave[2]} To={leave[3]}")

# Check all unique statuses in leave_requests
print("\nALL LEAVE STATUSES IN DATABASE:")
cursor.execute("SELECT DISTINCT status FROM leave_requests WHERE status IS NOT NULL")
all_leave_statuses = cursor.fetchall()
for status in all_leave_statuses:
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status = ?", (status[0],))
    count = cursor.fetchone()[0]
    print(f"  '{status[0]}': {count} records")

# Check leave requests for this week
print(f"\nLEAVE REQUESTS FOR THIS WEEK ({monday} to {sunday}):")
cursor.execute("""
    SELECT lr.start_date, lr.end_date, lr.status, COUNT(*) as count, COUNT(DISTINCT lr.employee_id) as unique_employees
    FROM leave_requests lr 
    WHERE lr.start_date <= ? AND lr.end_date >= ?
    GROUP BY lr.start_date, lr.end_date, lr.status
    ORDER BY lr.start_date, lr.status
""", (sunday.isoformat(), monday.isoformat()))
leave_week = cursor.fetchall()
for leave in leave_week:
    print(f"  {leave[0]} to {leave[1]}: Status='{leave[2]}', Count={leave[3]}, Unique Employees={leave[4]}")

conn.close()
