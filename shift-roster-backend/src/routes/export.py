from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, ShiftRoster as Roster, Shift, Role, AreaOfResponsibility as Area, Skill, Timesheet, LeaveRequest
from src.utils.decorators import admin_required, manager_required
import pandas as pd
import io
import csv
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import tempfile
import os

export_bp = Blueprint('export', __name__)

@export_bp.route('/employees/csv', methods=['GET'])
@jwt_required()
@manager_required
def export_employees_csv():
    """Export employees data to CSV format"""
    try:
        employees = User.query.all()

        # Prepare data for CSV
        data = []
        for emp in employees:
            role_name = emp.role_ref.name if getattr(emp, 'role_ref', None) else ''
            area_name = emp.area_ref.name if getattr(emp, 'area_ref', None) else ''
            skills = ', '.join([skill.name for skill in getattr(emp, 'skills', [])])

            data.append({
                'Employee ID': emp.employee_id or '',
                'Name': emp.name or '',
                'Surname': emp.surname or '',
                'Email': emp.email or '',
                'Contact Number': emp.contact_no or '',
                'Role': role_name,
                'Area of Responsibility': area_name,
                'Skills': skills,
                'Hire Date': '',
                'Status': 'Active'
            })

        # Create CSV in memory
        output = io.StringIO()
        if data:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        # Create response
        output.seek(0)
        response_data = output.getvalue()
        output.close()

        # Create file-like object for response
        file_obj = io.BytesIO(response_data.encode('utf-8'))

        return send_file(
            file_obj,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/timesheets/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_timesheets_excel():
    """Export timesheets to Excel format"""
    try:
        print("=== EXPORT DEBUG: Starting Excel export ===")
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')
        print(f"Raw parameters: start_date='{start_date}', end_date='{end_date}', employee_id='{employee_id}'")

        # Clean up empty string parameters
        if start_date == '':
            start_date = None
        if end_date == '':
            end_date = None
        if employee_id == '':
            employee_id = None
        print(f"Cleaned parameters: start_date='{start_date}', end_date='{end_date}', employee_id='{employee_id}'")

        print("Building query...")
        query = Timesheet.query
        if start_date:
            query = query.filter(Timesheet.date >= start_date)
            print(f"Added start_date filter: {start_date}")
        if end_date:
            query = query.filter(Timesheet.date <= end_date)
            print(f"Added end_date filter: {end_date}")
        if employee_id:
            query = query.filter(Timesheet.employee_id == employee_id)
            print(f"Added employee_id filter: {employee_id}")

        print("Executing query...")
        timesheets = query.all()
        print(f"Found {len(timesheets)} timesheets")

        if not timesheets:
            print("No timesheets found, creating empty response")
            # Return simple DataFrame for empty results
            df = pd.DataFrame([{'Message': 'No timesheets found for the selected criteria'}])
        else:
            print("Processing timesheets...")
            data = []
            for i, ts in enumerate(timesheets):
                print(f"Processing timesheet {i+1}/{len(timesheets)}: ID={ts.id}")
                
                # Create a row with proper data
                row = {
                    'Date': str(ts.date) if ts.date else 'N/A',
                    'Employee ID': 'N/A',
                    'Employee Name': 'N/A', 
                    'Shift': 'N/A',
                    'Hours Worked': float(ts.hours_worked) if ts.hours_worked else 0.0,
                    'Status': str(ts.status) if ts.status else 'Unknown',
                    'Approved By': 'Pending',
                    'Notes': str(ts.notes) if ts.notes else ''
                }
                
                # Get employee info safely
                try:
                    if hasattr(ts, 'employee') and ts.employee:
                        row['Employee ID'] = str(ts.employee.employee_id) if ts.employee.employee_id else 'N/A'
                        row['Employee Name'] = f"{ts.employee.name} {ts.employee.surname}" if (ts.employee.name and ts.employee.surname) else 'N/A'
                        print(f"  Employee: {row['Employee Name']}")
                except Exception as e:
                    print(f"  Employee error: {str(e)}")
                
                # Get shift info safely
                try:
                    if hasattr(ts, 'roster') and ts.roster:
                        if hasattr(ts.roster, 'shift') and ts.roster.shift:
                            row['Shift'] = str(ts.roster.shift.name) if ts.roster.shift.name else 'N/A'
                            print(f"  Shift: {row['Shift']}")
                except Exception as e:
                    print(f"  Shift error: {str(e)}")
                
                # Get approver info safely
                try:
                    if hasattr(ts, 'timesheet_approver') and ts.timesheet_approver:
                        approver_name = f"{ts.timesheet_approver.name} {ts.timesheet_approver.surname}" if (ts.timesheet_approver.name and ts.timesheet_approver.surname) else 'N/A'
                        row['Approved By'] = approver_name
                        print(f"  Approved by: {row['Approved By']}")
                except Exception as e:
                    print(f"  Approver error: {str(e)}")
                
                data.append(row)
                print(f"  Row added successfully")
            
            print(f"Creating DataFrame with {len(data)} rows...")
            df = pd.DataFrame(data)

        print("Creating Excel file...")
        output = io.BytesIO()
        
        print("Writing to Excel...")
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Timesheets', index=False)
            print("Excel write completed")

        output.seek(0)
        print("Seeking to start of file")
        
        print("=== EXPORT DEBUG: Sending file ===")
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'timesheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        print(f"=== EXPORT ERROR: {str(e)} ===")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'timesheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/roster/grid/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_roster_grid_excel():
    """Export roster data to an Excel file with a grid layout (employees x days)."""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({'error': 'start_date and end_date are required'}), 400

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Fetch all employees and roster entries for the period
        employees = User.query.order_by(User.name).all()
        roster_entries = Roster.query.filter(Roster.date.between(start_date, end_date)).all()

        # Create a map for quick lookup
        roster_map = {}
        for entry in roster_entries:
            key = (entry.employee_id, entry.date)
            roster_map[key] = entry.shift.name if entry.shift else 'Unknown'

        # Create date range for columns
        date_range = pd.date_range(start=start_date, end=end_date)

        # Prepare data for DataFrame
        data = []
        for emp in employees:
            row = {'Employee': f"{emp.name} {emp.surname}"}
            for dt in date_range:
                shift_name = roster_map.get((emp.id, dt.date()), '')
                row[dt.strftime('%Y-%m-%d (%a)')] = shift_name
            data.append(row)

        df = pd.DataFrame(data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Roster Grid', index=False)
            worksheet = writer.sheets['Roster Grid']
            # Adjust column widths
            for i, col in enumerate(df.columns):
                column_letter = chr(ord('A') + i)
                max_len = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[column_letter].width = max_len + 2

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'roster_grid_{start_date_str}_to_{end_date_str}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/employees/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_employees_excel():
    """Export employees data to Excel format"""
    try:
        employees = User.query.all()

        # Prepare data for Excel
        data = []
        for emp in employees:
            role_name = emp.role_ref.name if getattr(emp, 'role_ref', None) else ''
            area_name = emp.area_ref.name if getattr(emp, 'area_ref', None) else ''
            skills = ', '.join([skill.name for skill in getattr(emp, 'skills', [])])

            data.append({
                'Employee ID': emp.employee_id or '',
                'Name': emp.name or '',
                'Surname': emp.surname or '',
                'Email': emp.email or '',
                'Contact Number': emp.contact_no or '',
                'Role': role_name,
                'Area of Responsibility': area_name,
                'Skills': skills,
                'Hire Date': '',
                'Status': 'Active'
            })

        # Create Excel file in memory
        df = pd.DataFrame(data)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Employees', index=False)

            # Auto-adjust column widths
            worksheet = writer.sheets['Employees']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'employees_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/roster/csv', methods=['GET'])
@jwt_required()
@manager_required
def export_roster_csv():
    """Export roster data to CSV format"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Roster.query
        if start_date:
            query = query.filter(Roster.date >= start_date)
        if end_date:
            query = query.filter(Roster.date <= end_date)
            
        roster_entries = query.all()
        
        # Prepare data for CSV
        data = []
        for entry in roster_entries:
            employee = entry.employee
            shift = entry.shift
            
            data.append({
                'Date': entry.date.strftime('%Y-%m-%d'),
                'Employee ID': employee.employee_id,
                'Employee Name': f"{employee.name} {employee.surname}",
                'Role': employee.role_ref.name if employee.role_ref else '',
                'Area': employee.area_ref.name if employee.area_ref else '',
                'Shift': shift.name,
                'Start Time': shift.start_time.strftime('%H:%M') if shift.start_time else '',
                'End Time': shift.end_time.strftime('%H:%M') if shift.end_time else '',
                'Duration (Hours)': shift.hours,
                'Status': entry.status.title(),
                'Approved By': entry.approver.name if entry.approver else '',
                'Approved At': entry.approved_at.strftime('%Y-%m-%d %H:%M') if entry.approved_at else ''
            })
        
        # Create CSV in memory
        output = io.StringIO()
        if data:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        output.seek(0)
        response_data = output.getvalue()
        output.close()
        
        file_obj = io.BytesIO(response_data.encode('utf-8'))
        
        return send_file(
            file_obj,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/roster/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_roster_excel():
    """Export roster data to Excel format"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Roster.query
        if start_date:
            query = query.filter(Roster.date >= start_date)
        if end_date:
            query = query.filter(Roster.date <= end_date)
            
        roster_entries = query.all()
        
        # Prepare data for Excel
        data = []
        for entry in roster_entries:
            employee = entry.employee
            shift = entry.shift
            
            data.append({
                'Date': entry.date.strftime('%Y-%m-%d'),
                'Employee ID': employee.employee_id,
                'Employee Name': f"{employee.name} {employee.surname}",
                'Role': employee.role_ref.name if employee.role_ref else '',
                'Area': employee.area_ref.name if employee.area_ref else '',
                'Shift': shift.name,
                'Start Time': shift.start_time.strftime('%H:%M') if shift.start_time else '',
                'End Time': shift.end_time.strftime('%H:%M') if shift.end_time else '',
                'Duration (Hours)': shift.hours,
                'Status': entry.status.title(),
                'Approved By': entry.approver.name if entry.approver else '',
                'Approved At': entry.approved_at.strftime('%Y-%m-%d %H:%M') if entry.approved_at else ''
            })
        
        # Create Excel file in memory
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Roster', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Roster']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/roster/pdf', methods=['GET'])
@jwt_required()
@manager_required
def export_roster_pdf():
    """Export roster to PDF with basic table."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        query = Roster.query
        if start_date:
            query = query.filter(Roster.date >= start_date)
        if end_date:
            query = query.filter(Roster.date <= end_date)
        roster_entries = query.all()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        title = Paragraph("Shift Roster", styles['Heading1'])
        story.append(title)
        story.append(Spacer(1, 12))
        if start_date and end_date:
            story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
            story.append(Spacer(1, 12))

        data = [['Date', 'Employee', 'Shift', 'Time', 'Hours', 'Status', 'Approved By']]
        for entry in roster_entries:
            emp = entry.employee
            shift = entry.shift
            approver = entry.approver.name if entry.approver else ''
            data.append([
                entry.date.strftime('%Y-%m-%d'),
                f"{emp.name} {emp.surname}",
                shift.name if shift else '',
                f"{shift.start_time.strftime('%H:%M') if shift and shift.start_time else ''} - {shift.end_time.strftime('%H:%M') if shift and shift.end_time else ''}",
                str(entry.hours),
                entry.status.title(),
                approver
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        doc.build(story)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/timesheets/pdf', methods=['GET'])
@jwt_required()
@manager_required
def export_timesheets_pdf():
    """Export timesheets to PDF format"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        employee_id = request.args.get('employee_id')

        query = Timesheet.query
        if start_date:
            query = query.filter(Timesheet.date >= start_date)
        if end_date:
            query = query.filter(Timesheet.date <= end_date)
        if employee_id:
            query = query.filter(Timesheet.employee_id == employee_id)
            
        timesheets = query.all()
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Content
        story = []
        
        # Title
        title = Paragraph("Timesheet Report", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Date range info
        if start_date and end_date:
            date_info = Paragraph(f"Period: {start_date} to {end_date}", styles['Normal'])
            story.append(date_info)
            story.append(Spacer(1, 12))
        
        # Table data
        data = [['Date', 'Employee', 'Shift', 'Hours', 'Status', 'Approved By']]
        
        for timesheet in timesheets:
            employee = timesheet.employee
            shift = timesheet.roster.shift if timesheet.roster else None
            approved_by = f"{timesheet.timesheet_approver.name} {timesheet.timesheet_approver.surname}" if timesheet.timesheet_approver else 'Pending'
            
            data.append([
                timesheet.date.strftime('%Y-%m-%d'),
                f"{employee.name} {employee.surname}",
                shift.name if shift else 'N/A',
                str(timesheet.hours_worked),
                timesheet.status.title(),
                approved_by
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'timesheets_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/templates/employees', methods=['GET'])
@jwt_required()
@manager_required
def download_employee_template():
    """Download CSV template for employee import"""
    try:
        # Template headers
        headers = [
            'Employee ID',
            'Name',
            'Surname', 
            'Email',
            'Contact Number',
            'Role',
            'Area of Responsibility',
            'Skills (comma-separated)',
            'Hire Date (YYYY-MM-DD)',
            'Status (Active/Inactive)'
        ]
        
        # Sample data
        sample_data = [
            'EMP001',
            'John',
            'Doe',
            'john.doe@company.com',
            '+1234567890',
            'Employee',
            'Kitchen',
            'Food Preparation, Customer Service',
            '2024-01-15',
            'Active'
        ]
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerow(sample_data)  # Include sample row
        
        output.seek(0)
        response_data = output.getvalue()
        output.close()
        
        file_obj = io.BytesIO(response_data.encode('utf-8'))
        
        return send_file(
            file_obj,
            mimetype='text/csv',
            as_attachment=True,
            download_name='employee_import_template.csv'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@export_bp.route('/analytics/pdf', methods=['GET'])
@jwt_required()
@manager_required
def export_analytics_pdf():
    """Export analytics dashboard to PDF format"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        
        # Content
        story = []
        
        # Title
        title = Paragraph("Analytics Dashboard Report", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Date range
        if start_date and end_date:
            date_info = Paragraph(f"Report Period: {start_date} to {end_date}", styles['Normal'])
            story.append(date_info)
            story.append(Spacer(1, 20))
        
        # Key Metrics
        story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Sample metrics (in real app, fetch from database)
        metrics_data = [
            ['Metric', 'Value', 'Change'],
            ['Total Employees', '35', '+2'],
            ['Active Shifts', '197', '+15'],
            ['Approval Rate', '94%', '+2%'],
            ['Utilization Rate', '92%', '+1%']
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 20))
        
        # Employee Distribution
        story.append(Paragraph("Employee Distribution by Role", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        role_data = [
            ['Role', 'Count', 'Percentage'],
            ['Admin', '2', '6%'],
            ['Manager', '5', '14%'],
            ['Employee', '25', '71%'],
            ['Guest', '3', '9%']
        ]
        
        role_table = Table(role_data)
        role_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(role_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'analytics_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_bp.route('/reports/shift-acceptance/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_shift_acceptance_excel():
    """Export shift acceptance report to Excel format"""
    try:
        from sqlalchemy import and_
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        query = db.session.query(Roster, Shift, User).join(
            Shift, Roster.shift_id == Shift.id
        ).join(
            User, Roster.employee_id == User.id
        ).filter(
            Roster.status.in_(['approved', 'accepted'])
        )

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Roster.date >= start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Roster.date <= end_date)

        roster_entries = query.order_by(Roster.date, Roster.employee_id).all()

        # Format the data for Excel
        data = []
        for roster, shift, user in roster_entries:
            approved_by = roster.approver.name + ' ' + roster.approver.surname if roster.approver else 'N/A'
            data.append({
                'Employee': f"{user.name} {user.surname}",
                'Date': roster.date.strftime('%Y-%m-%d'),
                'Shift': shift.name,
                'Hours': shift.hours if shift else 0,
                'Status': roster.status,
                'Approved By': approved_by,
                'Approved Time': roster.approved_at.strftime('%Y-%m-%d %H:%M:%S') if roster.approved_at else 'N/A',
                'Accepted Time': roster.accepted_at.strftime('%Y-%m-%d %H:%M:%S') if roster.accepted_at else 'N/A'
            })

        df = pd.DataFrame(data)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Shift Acceptance Report', index=False)

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'shift_acceptance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_bp.route('/reports/employee-history/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_employee_history_excel():
    """Export employee history report to Excel format"""
    try:
        employee_id = request.args.get('employee_id', type=int)
        if not employee_id:
            return jsonify({'error': 'employee_id is required'}), 400

        employee = User.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404

        # Get all shift roster entries for this employee
        history = Roster.query.filter_by(employee_id=employee_id).order_by(Roster.date.desc()).all()

        # Format the data for Excel
        data = []
        for entry in history:
            shift = entry.shift
            approved_by = entry.approver.name + ' ' + entry.approver.surname if entry.approver else 'N/A'
            data.append({
                'Date': entry.date.strftime('%Y-%m-%d'),
                'Shift': shift.name if shift else '',
                'Status': entry.status,
                'Hours': shift.hours if shift else 0,
                'Approved At': entry.approved_at.strftime('%Y-%m-%d %H:%M:%S') if entry.approved_at else 'N/A',
                'Accepted At': entry.accepted_at.strftime('%Y-%m-%d %H:%M:%S') if entry.accepted_at else 'N/A',
                'Approved By': approved_by
            })

        df = pd.DataFrame(data)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Employee info sheet
            emp_info = pd.DataFrame([{
                'Employee ID': employee.employee_id,
                'Name': f"{employee.name} {employee.surname}",
                'Email': employee.email,
                'Role': employee.role_ref.name if employee.role_ref else '',
                'Area': employee.area_ref.name if employee.area_ref else ''
            }])
            emp_info.to_excel(writer, sheet_name='Employee Info', index=False)
            
            # History data
            df.to_excel(writer, sheet_name='Shift History', index=False)

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'employee_history_{employee.name}_{employee.surname}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@export_bp.route('/reports/leave-requests/excel', methods=['GET'])
@jwt_required()
@manager_required
def export_leave_requests_excel():
    """Export leave requests report to Excel format"""
    try:
        print("=== LEAVE REQUESTS EXCEL EXPORT DEBUG ===")
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        leave_type = request.args.get('leave_type')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        print(f"Params received: employee_id={employee_id}, status={status}, leave_type={leave_type}")
        
        # Build query - use the same pattern as working exports
        print("Building query...")
        query = db.session.query(LeaveRequest, User).join(
            User, LeaveRequest.employee_id == User.id
        )
        
        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)
            print(f"Added employee filter: {employee_id}")
        if status and status != 'all':
            query = query.filter(LeaveRequest.status == status)
            print(f"Added status filter: {status}")
        if leave_type:
            query = query.filter(LeaveRequest.leave_type == leave_type)
            print(f"Added leave_type filter: {leave_type}")
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(LeaveRequest.start_date >= start_date)
            print(f"Added start_date filter: {start_date}")
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(LeaveRequest.end_date <= end_date)
            print(f"Added end_date filter: {end_date}")
        
        print("Executing query...")
        leave_entries = query.order_by(LeaveRequest.start_date.desc()).all()
        print(f"Found {len(leave_entries)} leave requests")

        # Format the data for Excel
        data = []
        for i, (leave, user) in enumerate(leave_entries):
            try:
                print(f"Processing leave request {i+1}/{len(leave_entries)}: ID={leave.id}")
                
                if not user:
                    print(f"  WARNING: Leave request {leave.id} has no user!")
                    continue
                    
                approved_by = leave.approver.name + ' ' + leave.approver.surname if leave.approver else ''
                days_value = float(leave.days) if leave.days is not None else 0
                print(f"  Days: {days_value}")
                
                data.append({
                    'Employee': f"{user.name} {user.surname}",
                    'Leave Type': leave.leave_type,
                    'Start Date': leave.start_date.strftime('%Y-%m-%d'),
                    'End Date': leave.end_date.strftime('%Y-%m-%d'),
                    'Days': days_value,
                    'Status': leave.status,
                    'Reason': leave.reason or '',
                    'Applied Date': leave.created_at.strftime('%Y-%m-%d') if leave.created_at else '',
                    'Approved By': approved_by,
                    'Comments': leave.action_comment or ''
                })
                print(f"  Successfully processed leave request {leave.id}")
            except Exception as e:
                print(f"  ERROR processing leave request {leave.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        print(f"Creating DataFrame with {len(data)} rows...")
        df = pd.DataFrame(data)
        output = io.BytesIO()

        print("Writing to Excel...")
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leave Requests', index=False)

        output.seek(0)
        print("Excel file created successfully, sending response...")

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'leave_requests_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )

    except Exception as e:
        print(f"=== LEAVE REQUESTS EXCEL EXPORT ERROR: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

