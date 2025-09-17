#!/usr/bin/env python3
"""
Reference file showing how to create a simple hourly rates table
Note: This is just for reference - the actual table has been created using the models.py
"""

# This file is for reference only and shows the structure we implemented
# The actual table was created using SQLAlchemy models in models.py

# Example SQLAlchemy model (already implemented in models.py):
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class HourlyRates(db.Model):
    __tablename__ = 'hourly_rates'
    
    # Primary Key - auto-incrementing
    rate_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to link to employees (users table)  
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Hourly rate - use Numeric for precise currency calculations
    rate_per_hr = db.Column(db.Numeric(10, 2), nullable=False)  # e.g., 125.50
    
    # Currency (defaults to ZAR)
    currency = db.Column(db.String(3), default='ZAR', nullable=False)
    
    # When this rate becomes effective
    effective_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # When this rate expires (NULL means current)
    end_date = db.Column(db.Date, nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    employee = db.relationship('User', foreign_keys=[employee_id], backref='hourly_rates')
    created_by_user = db.relationship('User', foreign_keys=[created_by])
"""

# SQL to create the table:
CREATE_TABLE_SQL = """
CREATE TABLE hourly_rates (
    rate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    rate_per_hr DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ZAR' NOT NULL,
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NULL,
    
    FOREIGN KEY (employee_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX ix_hourly_rates_employee_effective ON hourly_rates(employee_id, effective_date);
CREATE INDEX ix_hourly_rates_active ON hourly_rates(employee_id, effective_date, end_date);
"""
