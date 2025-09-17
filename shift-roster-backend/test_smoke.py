import os
import json
import sys
import time

import requests

BASE_URL = os.environ.get("API_BASE", "http://127.0.0.1:5001/api")

ADMIN_PAYLOAD = {
    "email": "wanda.nezar@gmail.com",
    "google_id": "admin123",
    "name": "John",
    "surname": "Admin"
}

# Simple smoke test: login and hit analytics dashboard
if __name__ == "__main__":
    r = requests.post(f"{BASE_URL}/auth/google", json=ADMIN_PAYLOAD, timeout=10)
    print("LOGIN:", r.status_code)
    print(r.text[:200])
    r.raise_for_status()
    tokens = r.json()
    access = tokens.get("access_token")
    if not access:
        raise SystemExit("No access token returned")

    headers = {"Authorization": f"Bearer {access}"}
    r2 = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers, timeout=10)
    print("ANALYTICS:", r2.status_code)
    print(r2.text[:200])
    r2.raise_for_status()

    print("SMOKE PASS")
