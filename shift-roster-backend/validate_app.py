import os
import sys
import requests
import json
import time
from sqlalchemy import inspect

# Ensure the app can be imported
sys.path.insert(0, os.path.dirname(__file__))

from src.main import app
from src.models.models import db

def main():
    """
    Main function to run all validation checks.
    """
    print("--- Running Application Validation Script ---")

    with app.app_context():
        validate_schema()

    validate_apis()

def validate_apis():
    """
    Logs in as an admin and performs a GET request on all major endpoints.
    """
    print("\n--- 2. API Endpoint Validation (Admin Role) ---")
    BASE_URL = "http://127.0.0.1:5001/api"
    ADMIN_PAYLOAD = {
        "email": "wanda.nezar@gmail.com",
        "google_id": "validation_admin",
        "name": "Validation",
        "surname": "Admin"
    }

    # Start a server session to test against
    # This is a simplified version of the test runner
    print("Starting a temporary server for API tests...")
    os.system('python src/main.py > /dev/null 2>&1 &')
    server_pid = os.popen('pgrep -f "src/main.py"').read().strip()
    time.sleep(3) # Give server time to start

    try:
        # 1. Login as Admin
        print("\nAttempting to log in as Admin...")
        r = requests.post(f"{BASE_URL}/auth/google", json=ADMIN_PAYLOAD, timeout=10)
        if r.status_code != 200:
            print(f"  [FAIL] Login failed with status {r.status_code}: {r.text[:100]}")
            return

        access_token = r.json().get("access_token")
        if not access_token:
            print("  [FAIL] Login succeeded but no access token was returned.")
            return

        print("  [SUCCESS] Logged in as Admin.")
        headers = {"Authorization": f"Bearer {access_token}"}

        # 2. Define endpoints to test
        endpoints = [
            "/employees",
            "/roles",
            "/areas",
            "/skills",
            "/shifts",
            "/licenses",
            "/leave",
            "/roster",
            "/timesheets",
            "/reports/employee-search",
            "/designations",
            "/community/posts",
            "/analytics/dashboard",
        ]

        all_passed = True
        print("\nTesting GET endpoints...")
        for endpoint in endpoints:
            try:
                r_get = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
                if r_get.status_code == 200:
                    print(f"  [SUCCESS] GET {endpoint} responded with 200 OK.")
                else:
                    print(f"  [FAIL] GET {endpoint} responded with status {r_get.status_code}.")
                    all_passed = False
            except requests.exceptions.RequestException as e:
                print(f"  [FAIL] GET {endpoint} failed with an exception: {e}")
                all_passed = False

        if all_passed:
            print("\nAll API endpoint checks passed.")
        else:
            print("\nSome API endpoint checks failed.")

    finally:
        # 3. Kill the server
        if server_pid:
            print(f"\nShutting down temporary server (PID: {server_pid})...")
            os.system(f"kill {server_pid}")
        else:
            print("\nCould not find server PID to shut down.")

def validate_schema():
    """
    Connects to the database and prints the schema of all tables.
    """
    print("\n--- 1. Database Schema Validation ---")
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables: {', '.join(tables)}")

        for table_name in tables:
            print(f"\nTable: {table_name}")
            columns = inspector.get_columns(table_name)
            for i, column in enumerate(columns):
                print(f"  {i+1}. {column['name']} ({column['type']})")

        print("\nSchema validation check complete.")
    except Exception as e:
        print(f"ERROR: Could not inspect database schema. Reason: {e}")

    print("\n--- Validation Complete ---")

if __name__ == "__main__":
    main()
