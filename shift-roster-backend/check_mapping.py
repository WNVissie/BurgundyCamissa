import sys
sys.path.append('.')
from src.models.models import Timesheet, User
from src import create_app

app = create_app()
with app.app_context():
    print("=== DEBUGGING TIMESHEET TO USER MAPPING ===")
    
    # Get all approved timesheets
    approved_timesheets = Timesheet.query.filter(
        Timesheet.status == 'approved',
        Timesheet.hours_worked.isnot(None),
        Timesheet.hours_worked > 0
    ).all()
    
    print(f"\nFound {len(approved_timesheets)} approved timesheets with hours")
    
    # Check each timesheet and find corresponding user
    for ts in approved_timesheets:
        user = User.query.get(ts.employee_id)
        if user:
            print(f"Timesheet ID {ts.id}: Employee ID {ts.employee_id} -> {user.name} {user.surname}")
            print(f"  Date: {ts.date}, Hours: {ts.hours_worked}")
            print(f"  User rate: {user.rate_type} = R{user.rate_value}")
            print(f"  User has rate: {'YES' if user.rate_value else 'NO'}")
        else:
            print(f"Timesheet ID {ts.id}: Employee ID {ts.employee_id} -> NO USER FOUND!")
        print()
    
    # Check users with rates
    users_with_rates = User.query.filter(User.rate_value.isnot(None)).all()
    print(f"\nUsers with rates:")
    for user in users_with_rates:
        print(f"  ID {user.id}: {user.name} {user.surname} - {user.rate_type} = R{user.rate_value}")
        
        # Check if this user has approved timesheets
        user_timesheets = Timesheet.query.filter(
            Timesheet.employee_id == user.id,
            Timesheet.status == 'approved',
            Timesheet.hours_worked > 0
        ).count()
        print(f"    Approved timesheets: {user_timesheets}")
