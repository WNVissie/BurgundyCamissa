#!/usr/bin/env python3
import sys
import os
sys.path.append('src')
sys.path.append('.')

from src.config import Config
from src.models.models import db, Timesheet, User
from flask import Flask
import pandas as pd
import io

# Create minimal Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def test_export():
    with app.app_context():
        try:
            print("Testing timesheet export logic...")
            
            # Get some test timesheets
            timesheets = Timesheet.query.limit(5).all()
            print(f"Found {len(timesheets)} timesheets to test")
            
            data = []
            for i, ts in enumerate(timesheets):
                print(f"\n--- Processing timesheet {i+1}: ID {ts.id} ---")
                
                try:
                    # Test employee access
                    employee = ts.employee
                    if employee:
                        print(f"Employee: {employee.name} {employee.surname} (ID: {employee.employee_id})")
                    else:
                        print("ERROR: No employee found!")
                        continue
                    
                    # Test roster access
                    if hasattr(ts, 'roster') and ts.roster:
                        print(f"Roster ID: {ts.roster.id}")
                        
                        # Test shift access
                        if hasattr(ts.roster, 'shift') and ts.roster.shift:
                            print(f"Shift: {ts.roster.shift.name}")
                            shift_name = ts.roster.shift.name
                        else:
                            print("No shift found for this roster")
                            shift_name = 'N/A'
                    else:
                        print("No roster found for this timesheet")
                        shift_name = 'N/A'
                    
                    # Test approver access
                    if ts.timesheet_approver:
                        approved_by = f"{ts.timesheet_approver.name} {ts.timesheet_approver.surname}"
                        print(f"Approved by: {approved_by}")
                    else:
                        approved_by = 'Pending'
                        print("Status: Pending approval")
                    
                    # Create data row
                    row = {
                        'Date': ts.date.strftime('%Y-%m-%d'),
                        'Employee ID': employee.employee_id,
                        'Employee Name': f"{employee.name} {employee.surname}",
                        'Shift': shift_name,
                        'Hours Worked': ts.hours_worked,
                        'Status': ts.status.title(),
                        'Approved By': approved_by
                    }
                    data.append(row)
                    print("Row added successfully")
                    
                except Exception as e:
                    print(f"ERROR processing timesheet {ts.id}: {str(e)}")
                    print(f"Exception type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            print(f"\n--- Creating DataFrame with {len(data)} rows ---")
            df = pd.DataFrame(data)
            print("DataFrame created successfully")
            print(df.head())
            
            print("\n--- Testing Excel export ---")
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Timesheets', index=False)
            print("Excel export successful!")
            
            return True
            
        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_export()
    if success:
        print("\n✅ Export test completed successfully!")
    else:
        print("\n❌ Export test failed!")