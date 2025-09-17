import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.models import db, User
from flask import Flask
from sqlalchemy import inspect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:/Users/wanda/Documents/SMART Apps/Davey/employee-shift-roster-app Manus/shift-roster-backend/src/database/app.db'
db.init_app(app)

with app.app_context():
    inspector = inspect(db.engine)
    print('--- Database columns for users table ---')
    db_columns = inspector.get_columns('users')
    for col in db_columns:
        print(f"DB column: {col['name']} ({col['type']})")

    print('\n--- Model fields for User ---')
    model_fields = [c.name for c in User.__table__.columns]
    for field in model_fields:
        print(f"Model field: {field}")

    print('\n--- Fields in DB but not in model ---')
    db_col_names = set(col['name'] for col in db_columns)
    model_field_names = set(model_fields)
    print(db_col_names - model_field_names)

    print('\n--- Fields in model but not in DB ---')
    print(model_field_names - db_col_names)
