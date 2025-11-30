import requests
import hmac
import hashlib
import base64
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/webhooks/orders/create"
SECRET = "your_webhook_secret"

def generate_hmac(data):
    secret = SECRET.encode('utf-8')
    digest = hmac.new(secret, data, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')

def trigger_new_order():
    print("Triggering New Order for Selenium Test...")
    order_id = int(time.time())
    payload = {
        "id": order_id,
        "order_number": f"SEL-TEST-{order_id}",
        "email": "selenium@test.com",
        "customer": {"first_name": "Selenium", "last_name": "User", "phone": "+19998887777"}, # Replace with valid number if needed
        "total_price": "150.00",
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
        if res.status_code == 200:
            print(f"   Order Created: {payload['order_number']}")
            print("   Check the server logs for Selenium activity.")
        else:
            print(f"   Failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    trigger_new_order()
