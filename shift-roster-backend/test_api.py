import requests
import json

# Test the cost analytics API
def test_cost_api():
    base_url = "http://127.0.0.1:5001"
    
    # First, get a token by logging in (update credentials as needed)
    login_data = {
        "username": "admin",  
        "password": "admin123"  
    }
    
    try:
        # Login
        print("Attempting login...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Got token: {token[:20]}...")
            
            # Test cost overview endpoint
            print("\nTesting cost overview endpoint...")
            cost_response = requests.get(f"{base_url}/api/analytics/costs/overview", headers=headers)
            print(f"Cost overview response: {cost_response.status_code}")
            print(f"Cost overview data: {cost_response.text}")
            
        else:
            print(f"Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

# Test without authentication first
print("Testing endpoints without auth...")
try:
    base_url = "http://127.0.0.1:5001"
    response = requests.get(f"{base_url}/api/analytics/costs/overview", timeout=5)
    print(f"No auth response: {response.status_code} - {response.text}")
except Exception as e:
    print(f"No auth error: {e}")

print("\n" + "="*50)
test_cost_api()
