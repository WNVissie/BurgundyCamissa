#!/usr/bin/env python3
"""
Simple test for leave requests Excel export - mimicking frontend request
"""

import requests
import sys
import os

def test_leave_export():
    url = 'http://localhost:5001/export/reports/leave-requests/excel'
    
    # Test the exact same params the frontend would send
    params = {
        'status': 'all'  # This matches what frontend sends when activeStatusView is 'all'
    }
    
    try:
        print(f"Testing GET request to: {url}")
        print(f"With params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"SUCCESS! Content-Length: {len(response.content)} bytes")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            # Save the file to test it works
            with open('test_leave_export.xlsx', 'wb') as f:
                f.write(response.content)
            print("Saved test file: test_leave_export.xlsx")
            
        else:
            print(f"ERROR Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == '__main__':
    test_leave_export()