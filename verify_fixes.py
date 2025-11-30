import requests
import hmac
import hashlib
import base64
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1/webhooks/orders/create"
SECRET = "your_webhook_secret" # Must match app/core/config.py

def generate_hmac(data):
    """Generates the Shopify HMAC signature."""
    secret = SECRET.encode('utf-8')
    digest = hmac.new(secret, data, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')

def run_tests():
    print("Starting Verification Tests...\n")
    
    # --- TEST 1: Security (Missing Header) ---
    print("1. Testing Security (Missing Header)...")
    try:
        res = requests.post(BASE_URL, json={})
        if res.status_code == 401:
            print("   PASSED: Rejected with 401 (Missing HMAC)")
        else:
            print(f"   FAILED: Expected 401, got {res.status_code}")
    except Exception as e:
        print(f"   ERROR: Could not connect ({e})")
    print("-" * 30)

    # --- TEST 2: Security (Invalid Header) ---
    print("2. Testing Security (Invalid Header)...")
    try:
        res = requests.post(BASE_URL, json={}, headers={"X-Shopify-Hmac-Sha256": "fake_signature"})
        if res.status_code == 401:
            print("   PASSED: Rejected with 401 (Invalid HMAC)")
        else:
            print(f"   FAILED: Expected 401, got {res.status_code}")
    except Exception as e:
        print(f"   ERROR: Could not connect ({e})")
    print("-" * 30)

    # --- TEST 3: Happy Path (Valid Request) ---
    print("3. Testing Valid Request...")
    order_id = int(time.time())
    payload = {
        "id": order_id,
        "order_number": f"TEST-{order_id}",
        "email": "test@example.com",
        "customer": {"first_name": "Test", "last_name": "User", "phone": "+1234567890"},
        "total_price": "50.00",
        "currency": "USD"
    }
    data = json.dumps(payload).encode('utf-8')
    signature = generate_hmac(data)
    
    try:
        res = requests.post(
            BASE_URL, 
            data=data, 
            headers={"X-Shopify-Hmac-Sha256": signature, "Content-Type": "application/json"}
        )
        if res.status_code == 200 and res.json().get("status") == "success":
            print("   PASSED: Accepted with 200 (Success)")
            print(f"   Order ID: {order_id}")
        else:
            print(f"   FAILED: Expected success, got {res.status_code} {res.text}")
    except Exception as e:
        print(f"   ERROR: Could not connect ({e})")
    print("-" * 30)

    # --- TEST 4: Idempotency (Duplicate Request) ---
    print("4. Testing Idempotency (Duplicate Request)...")
    try:
        # Sending the exact same payload and signature again
        res = requests.post(
            BASE_URL, 
            data=data, 
            headers={"X-Shopify-Hmac-Sha256": signature, "Content-Type": "application/json"}
        )
        if res.status_code == 200 and res.json().get("status") == "skipped":
            print("   PASSED: Correctly identified as duplicate (Skipped)")
        else:
            print(f"   FAILED: Expected 'skipped', got {res.text}")
    except Exception as e:
        print(f"   ERROR: Could not connect ({e})")
    print("-" * 30)

    print("\nVerification Complete!")

if __name__ == "__main__":
    run_tests()
