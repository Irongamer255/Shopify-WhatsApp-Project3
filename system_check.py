import os
import sys
import requests
import hmac
import hashlib
import base64
import json
import time
from sqlalchemy import create_engine, text
# Add current directory to path to allow imports from app
sys.path.append(os.getcwd())

try:
    from app.core.config import settings
except ImportError as e:
    print(f"CRITICAL: Could not import app settings. {e}")
    sys.exit(1)

REPORT_FILE = "verification_report.txt"
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BASE_URL}/api/v1/webhooks/orders/create"

def log(message, status="INFO"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{status}] {message}"
    print(formatted_message)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(formatted_message + "\n")

def check_files():
    log("--- Checking File Integrity ---")
    required_files = [
        "app/main.py",
        "app/core/config.py",
        "app/db/models.py",
        "app/db/database.py",
        "static/index.html",
        "static/js/app.js",
        "static/css/styles.css",
        "requirements.txt",
        "schema.sql"
    ]
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            log(f"File found: {file_path}", "PASS")
        else:
            log(f"File MISSING: {file_path}", "FAIL")
            all_exist = False
    return all_exist

def check_config():
    log("--- Checking Configuration ---")
    try:
        if settings.DATABASE_URL:
            log("DATABASE_URL is set", "PASS")
        else:
            log("DATABASE_URL is missing", "FAIL")
            
        if settings.SHOPIFY_WEBHOOK_SECRET:
            log("SHOPIFY_WEBHOOK_SECRET is set", "PASS")
        else:
            log("SHOPIFY_WEBHOOK_SECRET is missing", "FAIL")
        return True
    except Exception as e:
        log(f"Config check failed: {e}", "FAIL")
        return False

def check_database():
    log("--- Checking Database Connection ---")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            log("Successfully connected to MySQL database", "PASS")
        return True
    except Exception as e:
        log(f"Database connection failed: {e}", "FAIL")
        return False

def check_frontend():
    log("--- Checking Frontend Accessibility ---")
    try:
        res = requests.get(BASE_URL)
        if res.status_code == 200:
            log(f"Frontend reachable at {BASE_URL}", "PASS")
        else:
            log(f"Frontend returned status {res.status_code}", "FAIL")
            return False
            
        # Check static asset
        res_js = requests.get(f"{BASE_URL}/static/js/app.js")
        if res_js.status_code == 200:
            log("Static asset (app.js) reachable", "PASS")
        else:
            log(f"Static asset returned status {res_js.status_code}", "FAIL")
            return False
        return True
    except requests.exceptions.ConnectionError:
        log("Could not connect to server. Is it running?", "FAIL")
        return False

def generate_hmac(data):
    secret = settings.SHOPIFY_WEBHOOK_SECRET.encode('utf-8')
    digest = hmac.new(secret, data, hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')

def check_api_security():
    log("--- Checking API Security & Logic ---")
    
    # 1. Security: Missing Header
    try:
        res = requests.post(WEBHOOK_URL, json={})
        if res.status_code == 401:
            log("Security Check: Rejected missing HMAC", "PASS")
        else:
            log(f"Security Check: Failed (Expected 401, got {res.status_code})", "FAIL")
    except Exception as e:
        log(f"API check failed: {e}", "FAIL")
        return False

    # 2. Happy Path
    order_id = int(time.time())
    payload = {
        "id": order_id,
        "order_number": f"CHECK-{order_id}",
        "email": "check@example.com",
        "customer": {"first_name": "System", "last_name": "Check", "phone": "+1234567890"},
        "total_price": "10.00",
        "currency": "USD"
    }
    data = json.dumps(payload).encode('utf-8')
    signature = generate_hmac(data)
    
    try:
        res = requests.post(
            WEBHOOK_URL, 
            data=data, 
            headers={"X-Shopify-Hmac-Sha256": signature, "Content-Type": "application/json"}
        )
        if res.status_code == 200 and res.json().get("status") == "success":
            log("Happy Path: Order created successfully", "PASS")
        else:
            log(f"Happy Path: Failed ({res.status_code} {res.text})", "FAIL")
    except Exception as e:
        log(f"API check failed: {e}", "FAIL")

    # 3. Idempotency
    try:
        res = requests.post(
            WEBHOOK_URL, 
            data=data, 
            headers={"X-Shopify-Hmac-Sha256": signature, "Content-Type": "application/json"}
        )
        if res.status_code == 200 and res.json().get("status") == "skipped":
            log("Idempotency: Duplicate order skipped", "PASS")
        else:
            log(f"Idempotency: Failed (Expected skipped, got {res.text})", "FAIL")
    except Exception as e:
        log(f"API check failed: {e}", "FAIL")
    
    return True

def main():
    # Clear previous report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("SYSTEM VERIFICATION REPORT\n==========================\n\n")
    
    print(f"Running System Checks... Output saved to {REPORT_FILE}\n")
    
    check_files()
    print("")
    check_config()
    print("")
    check_database()
    print("")
    check_frontend()
    print("")
    check_api_security()
    
    print(f"\nChecks Complete. Please review {REPORT_FILE}")

if __name__ == "__main__":
    main()
