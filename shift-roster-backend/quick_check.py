import sys
sys.path.append('.')
from src.models.models import Timesheet, User
from src import create_app

app = create_app()
with app.app_context():
    total_timesheets = Timesheet.query.count()
    approved_timesheets = Timesheet.query.filter(Timesheet.status == 'approved').count()
    print(f'Total timesheets: {total_timesheets}')
    print(f'Approved timesheets: {approved_timesheets}')
    
    # Show some sample timesheets
    samples = Timesheet.query.limit(5).all()
    for ts in samples:
        print(f'  ID: {ts.id}, Employee: {ts.employee_id}, Hours: {ts.hours_worked}, Status: {ts.status}, Date: {ts.date}')
    
    # Check users with rates
    users_with_rates = User.query.filter(User.rate_value.isnot(None)).count()
    print(f'Users with rates: {users_with_rates}')
