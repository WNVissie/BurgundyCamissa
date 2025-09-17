import csv
import os
import json
from src.models.models import db, User, Role, AreaOfResponsibility, Skill, License, EmployeeLicense
from src.main import create_app
from sqlalchemy.exc import IntegrityError

# CSV file paths (adjust if needed): try ENV var then a few common fallbacks
def resolve_csv_dir():
    env_dir = os.environ.get('CSV_DIR')
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    here = os.path.dirname(__file__)
    candidates = [
        os.path.join(here, 'Re_ Employee Shift Roster'),
        os.path.join(os.path.dirname(here), 'Re_ Employee Shift Roster'),
        os.path.join(here, 'Re-Employee Shft Roster'),
        os.path.join(os.path.dirname(here), 'Re-Employee Shft Roster'),
        os.path.join(here, 'data', 'Re_ Employee Shift Roster'),
        os.path.join(here, 'data', 'Re-Employee Shft Roster'),
        os.path.join(here, 'data'),
        here,
    ]
    for d in candidates:
        if os.path.isdir(d):
            return d
    return here

def first_existing(base_dir, names):
    for n in names:
        p = os.path.join(base_dir, n)
        if os.path.isfile(p):
            return p
    return os.path.join(base_dir, names[0])

CSV_DIR = resolve_csv_dir()
EMPLOYEES_CSV = first_existing(CSV_DIR, ['employees.csv', 'employees_template.csv'])
SKILLS_CSV = first_existing(CSV_DIR, ['skills.csv', 'skills_template.csv'])
AREAS_CSV = first_existing(CSV_DIR, ['areas.csv', 'areas_template.csv'])
LICENSES_CSV = first_existing(CSV_DIR, ['licenses.csv'])

ADMIN_EMAIL = 'wanda.nezar@gmail.com'

app = create_app()

# Helper to clear all data
def clear_tables():
    db.session.query(EmployeeLicense).delete()
    db.session.query(User).delete()
    db.session.query(Role).delete()
    db.session.query(AreaOfResponsibility).delete()
    db.session.query(Skill).delete()
    db.session.query(License).delete()
    db.session.commit()

# Seed Roles
ROLES = [
    {
        'name': 'Admin',
        'permissions': {
            'manage_employees': True,
            'manage_roles': True,
            'manage_areas': True,
            'manage_skills': True,
            'manage_shifts': True,
            'view_analytics': True
        }
    },
    {
        'name': 'Manager',
        'permissions': {
            'manage_employees': True,
            'manage_shifts': True,
            'view_analytics': True
        }
    },
    {
        'name': 'Employee',
        'permissions': {
            'view_analytics': False
        }
    }
]

def seed_roles():
    for role in ROLES:
        db.session.add(Role(name=role['name'], permissions=json.dumps(role['permissions'])))
    db.session.commit()

def seed_areas():
    if not os.path.isfile(AREAS_CSV):
        print(f'Skipping areas: file not found -> {AREAS_CSV}')
        return
    with open(AREAS_CSV, newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
            if ';' in sample:
                dialect = csv.excel
                dialect.delimiter = ';'
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            name = (row.get('area_name') or row.get('name') or '').strip()
            if name:
                db.session.add(AreaOfResponsibility(name=name))
    db.session.commit()

def seed_skills():
    if not os.path.isfile(SKILLS_CSV):
        print(f'Skipping skills: file not found -> {SKILLS_CSV}')
        return
    with open(SKILLS_CSV, newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
            if ';' in sample:
                dialect = csv.excel
                dialect.delimiter = ';'
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            name = (row.get('skill_name') or row.get('name') or '').strip()
            if name:
                db.session.add(Skill(name=name))
    db.session.commit()

def seed_licenses():
    if not os.path.isfile(LICENSES_CSV):
        print(f'Skipping licenses: file not found -> {LICENSES_CSV}')
        return
    with open(LICENSES_CSV, newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
            if ';' in sample:
                dialect = csv.excel
                dialect.delimiter = ';'
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            name = (row.get('license_name') or row.get('name') or '').strip()
            desc = (row.get('description') or row.get('sku') or '').strip()
            if name:
                db.session.add(License(name=name, description=desc))
    db.session.commit()

def seed_employees():
    if not os.path.isfile(EMPLOYEES_CSV):
        print(f'Skipping employees: file not found -> {EMPLOYEES_CSV}')
        return
    # Get roles, designations, areas
    roles = {r.name: r for r in Role.query.all()}
    areas = {a.name: a for a in AreaOfResponsibility.query.all()}
    with open(EMPLOYEES_CSV, newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except Exception:
            dialect = csv.excel
            if ';' in sample:
                dialect = csv.excel
                dialect.delimiter = ';'
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            email = (row.get('email') or '').strip()
            emp_id = (row.get('employee_id') or '').strip()
            if not email:
                # synthesize a unique, non-empty email for required field
                base = emp_id.lower() or (row.get('name','').strip().replace(' ','.').lower() or 'user')
                email = f"{base}@example.com"
            role_name = 'Admin' if email == ADMIN_EMAIL else 'Manager'
            role = roles.get(role_name)
            area_name = (row.get('area_of_responsibility') or row.get('area') or '').strip()
            area = areas.get(area_name)
            user = User(
                google_id=row.get('google_id', '') or f"dev-{row.get('employee_id','')}",
                email=email,
                name=row.get('name', ''),
                surname=row.get('surname', ''),
                employee_id=emp_id,
                contact_no=row.get('contact_no', ''),
                alt_contact_name=row.get('alt_contact_name', ''),
                alt_contact_no=row.get('alt_contact_no', ''),
                role_id=role.id if role else None,
                area_of_responsibility_id=area.id if area else None,
                designation=row.get('designation', '')
            )
            db.session.add(user)
    db.session.commit()

def main():
    with app.app_context():
        print('CSV_DIR:', CSV_DIR)
        print('Clearing tables...')
        clear_tables()
        print('Seeding roles...')
        seed_roles()
        print('Seeding areas...')
        seed_areas()
        print('Seeding skills...')
        seed_skills()
        print('Seeding licenses...')
        seed_licenses()
        print('Seeding employees...')
        seed_employees()
        print('Done.')

if __name__ == '__main__':
    main()
