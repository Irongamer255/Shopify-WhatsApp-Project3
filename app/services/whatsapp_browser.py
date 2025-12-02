from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os
import logging

logger = logging.getLogger(__name__)

class SeleniumWhatsApp:
    def __init__(self, user_id: int, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless=new")
        
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Persist user data to keep login session
        current_dir = os.getcwd()
        # Use user-specific directory
        user_data_dir = os.path.join(current_dir, "chrome_data", str(user_id))
        self.options.add_argument(f"--user-data-dir={user_data_dir}")
        
        self.driver = None

    def start(self):
        logger.info("Starting Selenium WebDriver...")
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.driver.get("https://web.whatsapp.com")
            logger.info("WhatsApp Web opened.")
            
            # Wait for main page to load (check for side panel)
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )
                logger.info("WhatsApp Web loaded successfully (Session active).")
            except Exception:
                logger.warning("Could not detect active session. QR Code scan might be needed.")
                
        except Exception as e:
            logger.error(f"Failed to start Selenium: {e}")
            if self.driver:
                self.driver.quit()
            raise e

    def send_message(self, phone, message):
        if not self.driver:
            raise Exception("Driver not started. Call start() first.")
            
        try:
            logger.info(f"Sending message to {phone}...")
            
            # 1. Open chat directly
            # Encode message for URL
            from urllib.parse import quote
            encoded_message = quote(message)
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
            self.driver.get(url)
            
            # 2. Wait for send button (The arrow icon)
            # Note: Selectors change often. Using a generic approach or aria-label is safer.
            # Currently, the send button usually has data-icon='send' or aria-label='Send'
            send_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='send']"))
            )
            
            # 3. Click send
            send_button.click()
            logger.info("Send button clicked.")
            
            # 4. Wait a bit for message to actually leave
            time.sleep(3) 
            
            logger.info("Message sent successfully via Selenium.")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message via Selenium: {e}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed.")

    def link_device(self):
        """
        Opens a visible browser for the user to scan the QR code.
        Waits for login success or timeout.
        """
        logger.info("Starting Selenium for device linking...")
        try:
            # Force headless=False for linking
            self.options.arguments.remove("--headless=new") if "--headless=new" in self.options.arguments else None
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.driver.get("https://web.whatsapp.com")
            logger.info("WhatsApp Web opened for linking.")
            
            # Wait for user to scan QR code (check for side panel)
            # Giving 60 seconds for the user to scan
            try:
                WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, "side"))
                )
                logger.info("Device linked successfully!")
                return True
            except Exception:
                logger.warning("Linking timed out or failed.")
                return False
            finally:
                # Close the browser after linking (session is saved)
                self.close()
                
        except Exception as e:
            logger.error(f"Failed to link device: {e}")
            if self.driver:
                self.driver.quit()
            return False
