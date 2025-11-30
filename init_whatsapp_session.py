from app.services.whatsapp_browser import SeleniumWhatsApp
import time
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

def init_session():
    print("🚀 Starting WhatsApp Session Initialization...")
    print("This will open a Chrome browser. Please scan the QR code with your phone.")
    print("The session will be saved to ./chrome_data")
    
    # Start in HEADED mode (visible) so user can see QR code
    bot = SeleniumWhatsApp(headless=False)
    
    try:
        bot.start()
        print("\n✅ Browser opened!")
        print("👉 Please scan the QR code now.")
        print("Waiting for 60 seconds (or press Ctrl+C to stop)...")
        
        # Keep browser open for user to scan
        time.sleep(60)
        
        print("\n⏳ Time's up! Closing browser.")
        print("If you scanned the code, the session is now saved.")
        
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        bot.close()

if __name__ == "__main__":
    init_session()
