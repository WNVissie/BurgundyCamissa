from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from src.models.models import db, User as Employee, Role, AreaOfResponsibility as Area, Skill, Shift
from src.utils.decorators import admin_required
import pandas as pd
import io
import json
from datetime import datetime

import_bp = Blueprint('import', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@import_bp.route('/employees/csv', methods=['POST'])
@jwt_required()
@admin_required
def import_employees_csv():
    """Import employees from CSV/Excel file into the Users table."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV and Excel are allowed'}), 400

        # Read DataFrame
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required = ['Employee ID', 'Name', 'Surname', 'Email']
        missing = [c for c in required if c not in df.columns]
        if missing:
            return jsonify({'error': f'Missing required columns: {", ".join(missing)}'}), 400

        imported = 0
        errors = []

        # Detect skills column name variations
        skills_col = None
        for c in df.columns:
            cl = str(c).strip().lower()
            if cl in ('skills', 'skills (comma-separated)'):
                skills_col = c
                break

        for idx, row in df.iterrows():
            try:
                emp_id_val = str(row['Employee ID']).strip() if pd.notna(row['Employee ID']) else None
                email = str(row['Email']).strip() if pd.notna(row['Email']) else None
                name = str(row['Name']).strip() if pd.notna(row['Name']) else ''
                surname = str(row['Surname']).strip() if pd.notna(row['Surname']) else ''

                if not email:
                    errors.append(f"Row {idx+2}: Email is required")
                    continue

                # Duplicate check
                if emp_id_val and Employee.query.filter_by(employee_id=emp_id_val).first():
                    errors.append(f"Row {idx+2}: Employee ID {emp_id_val} already exists")
                    continue
                if Employee.query.filter_by(email=email).first():
                    errors.append(f"Row {idx+2}: Email {email} already exists")
                    continue

                # Role
                role_name = str(row.get('Role')).strip() if pd.notna(row.get('Role')) else 'Employee'
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    role = Role(name=role_name, permissions='{}')
                    db.session.add(role)
                    db.session.flush()

                # Area
                area = None
                if pd.notna(row.get('Area of Responsibility')):
                    area_name = str(row['Area of Responsibility']).strip()
                    area = Area.query.filter_by(name=area_name).first()
                    if not area:
                        area = Area(name=area_name, description=f"Auto-created area: {area_name}")
                        db.session.add(area)
                        db.session.flush()

                # Create user (User table is the employees table)
                google_id = f"import_{emp_id_val or email}"
                employee = Employee(
                    google_id=google_id,
                    email=email,
                    name=name,
                    surname=surname,
                    employee_id=emp_id_val,
                    contact_no=str(row.get('Contact Number', '')).strip() if pd.notna(row.get('Contact Number')) else '',
                    role_id=role.id,
                    area_of_responsibility_id=area.id if area else None,
                )
                db.session.add(employee)
                db.session.flush()

                # Skills
                if skills_col and pd.notna(row.get(skills_col)):
                    for s in str(row[skills_col]).split(','):
                        skill_name = s.strip()
                        if not skill_name:
                            continue
                        skill = Skill.query.filter_by(name=skill_name).first()
                        if not skill:
                            skill = Skill(name=skill_name, description=f"Auto-created skill: {skill_name}")
                            db.session.add(skill)
                            db.session.flush()
                        employee.skills.append(skill)

                imported += 1
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")

        db.session.commit()
        return jsonify({'message': f'Successfully imported {imported} employees', 'imported_count': imported, 'errors': errors}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@import_bp.route('/employees/validate', methods=['POST'])
@jwt_required()
@admin_required
def validate_employee_import():
    """Validate a CSV/Excel file structure and potential duplicates."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV and Excel are allowed'}), 400

        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        required = ['Employee ID', 'Name', 'Surname', 'Email']
        missing = [c for c in required if c not in df.columns]

        result = {
            'valid': len(missing) == 0,
            'total_rows': int(len(df)),
            'missing_columns': missing,
            'available_columns': list(df.columns),
            'sample_data': df.head(3).to_dict('records') if len(df) > 0 else [],
            'warnings': []
        }

        if result['valid']:
            # Duplicates in file
            dup_ids = df[df.duplicated(['Employee ID'], keep=False)]['Employee ID'].dropna().astype(str).tolist()
            if dup_ids:
                result['warnings'].append(f"Duplicate Employee IDs in file: {', '.join(sorted(set(dup_ids)))}")

            # Existing in DB
            existing_ids = []
            for emp_id in df['Employee ID']:
                emp_id_val = str(emp_id).strip() if pd.notna(emp_id) else None
                if emp_id_val and Employee.query.filter_by(employee_id=emp_id_val).first():
                    existing_ids.append(emp_id_val)
            if existing_ids:
                result['warnings'].append(f"Employee IDs already exist in database: {', '.join(sorted(set(existing_ids)))}")

            # Email format
            bad_emails = []
            for i, row in df.iterrows():
                email = str(row.get('Email', '')).strip()
                if email and '@' not in email:
                    bad_emails.append(f"Row {i+2}: {email}")
            if bad_emails:
                result['warnings'].append(f"Invalid email formats: {', '.join(bad_emails[:5])}")

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@import_bp.route('/backup/create', methods=['POST'])
@jwt_required()
@admin_required
def create_backup():
    """Create a lightweight JSON backup of master data."""
    try:
        backup = {
            'timestamp': datetime.now().isoformat(),
            'employees': [],
            'roles': [],
            'areas': [],
            'skills': [],
            'shifts': []
        }

        for emp in Employee.query.all():
            backup['employees'].append({
                'employee_id': emp.employee_id,
                'name': emp.name,
                'surname': emp.surname,
                'email': emp.email,
                'contact_number': emp.contact_no,
                'role': emp.role_ref.name if emp.role_ref else None,
                'area': emp.area_ref.name if emp.area_ref else None,
                'skills': [s.name for s in emp.skills],
                'created_at': emp.created_at.isoformat() if emp.created_at else None,
            })

        for role in Role.query.all():
            backup['roles'].append({
                'name': role.name,
                'permissions': role.permissions,
            })

        for area in Area.query.all():
            backup['areas'].append({
                'name': area.name,
                'description': area.description,
            })

        for skill in Skill.query.all():
            backup['skills'].append({
                'name': skill.name,
                'description': skill.description,
            })

        for sh in Shift.query.all():
            backup['shifts'].append({
                'name': sh.name,
                'start_time': sh.start_time.strftime('%H:%M') if sh.start_time else None,
                'end_time': sh.end_time.strftime('%H:%M') if sh.end_time else None,
                'hours': sh.hours,
            })

        data = json.dumps(backup, indent=2)
        buf = io.BytesIO(data.encode('utf-8'))
        return send_file(
            buf,
            mimetype='application/json',
            as_attachment=True,
            download_name=f"system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@import_bp.route('/backup/restore', methods=['POST'])
@jwt_required()
@admin_required
def restore_backup():
    """Validate a backup file and report summary (no DB writes)."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No backup file provided'}), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.lower().endswith('.json'):
            return jsonify({'error': 'Invalid file type. Please upload a .json backup file'}), 400

        try:
            payload = json.load(file)
        except Exception as e:
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

        summary = {
            'employees': len(payload.get('employees', [])),
            'roles': len(payload.get('roles', [])),
            'areas': len(payload.get('areas', [])),
            'skills': len(payload.get('skills', [])),
            'shifts': len(payload.get('shifts', [])),
        }
        return jsonify({'message': 'Backup validated. Restore not implemented in this build.', 'summary': summary}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

