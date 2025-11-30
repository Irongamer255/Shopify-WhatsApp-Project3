import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app.services.whatsapp import whatsapp_service
from app.core.config import settings

# --- CONFIGURATION ---
# REPLACE THIS WITH YOUR REAL TESTING PHONE NUMBER
# Format: Country code + Number (e.g., "15551234567")
TEST_PHONE_NUMBER = "REPLACE_WITH_YOUR_NUMBER" 

async def test_whatsapp_sending():
    print("📱 Starting WhatsApp Verification...\n")
    
    if settings.WHATSAPP_API_TOKEN == "your_whatsapp_token":
        print("❌ ERROR: You must update app/core/config.py with your REAL WhatsApp credentials first!")
        return

    if TEST_PHONE_NUMBER == "REPLACE_WITH_YOUR_NUMBER":
        print("⚠️  WARNING: You need to edit verify_whatsapp.py and set TEST_PHONE_NUMBER to your real number.")
        return

    # --- TEST 1: System Credentials ---
    print("1. Testing System Credentials (Default)...")
    try:
        # Sending a simple 'hello_world' template which is available by default in WABA
        response = await whatsapp_service.send_template_message(
            to_phone=TEST_PHONE_NUMBER,
            template_name="hello_world",
            language_code="en_US"
        )
        print("   PASSED: Message sent successfully!")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   FAILED: {e}")
    print("-" * 30)

    # --- TEST 2: Merchant Credentials ---
    print("2. Testing Merchant Credentials (Mock)...")
    
    # Mock Merchant Object
    class MockMerchant:
        whatsapp_api_token = settings.WHATSAPP_API_TOKEN # Using same valid token for test
        whatsapp_phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    
    try:
        response = await whatsapp_service.send_template_message(
            to_phone=TEST_PHONE_NUMBER,
            template_name="hello_world",
            language_code="en_US",
            merchant=MockMerchant()
        )
        print("   PASSED: Merchant message sent successfully!")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   FAILED: {e}")
    print("-" * 30)
    
    print("\nVerification Complete!")

if __name__ == "__main__":
    asyncio.run(test_whatsapp_sending())
