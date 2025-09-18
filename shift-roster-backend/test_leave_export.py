#!/usr/bin/env python3
"""
Test script for leave requests Excel export
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app, db
from src.models.models import User, LeaveRequest
from flask import json

def test_leave_export():
    with app.test_client() as client:
        with app.app_context():
            print("Testing leave requests Excel export...")
            
            # Check if we have data
            leave_count = LeaveRequest.query.count()
            user_count = User.query.count()
            print(f"Database has {leave_count} leave requests and {user_count} users")
            
            # Make the export request
            response = client.post('/export/reports/leave-requests/excel', 
                                 json={'status': 'all'},
                                 content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"SUCCESS! Content-Length: {len(response.data)} bytes")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
            else:
                print(f"ERROR: {response.get_data(as_text=True)}")

if __name__ == '__main__':
    test_leave_export()