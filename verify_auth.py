import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_auth_flow():
    email = f"testuser_{int(time.time())}@example.com"
    password = "password123"
    
    print(f"1. Signing up with {email}...")
    res = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"Signup failed: {res.text}")
        return
    print("Signup successful!")
    
    print("2. Logging in...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    token = res.json()["access_token"]
    print("Login successful! Token received.")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("3. Accessing protected endpoint (Orders)...")
    res = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
    if res.status_code == 200:
        print(f"Access granted! Orders: {len(res.json())}")
    else:
        print(f"Access denied: {res.status_code} {res.text}")
        
    print("4. Accessing protected endpoint (Analytics)...")
    res = requests.get(f"{BASE_URL}/admin/analytics", headers=headers)
    if res.status_code == 200:
        print(f"Access granted! Analytics: {res.json()}")
    else:
        print(f"Access denied: {res.status_code} {res.text}")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"Error: {e}")
