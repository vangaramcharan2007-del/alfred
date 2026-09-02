import time
import os
import logging
from typing import Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    webdriver = None

logger = logging.getLogger("jarvisx.whatsapp_bridge")

class WhatsAppSeleniumBridge:
    """True Level 4 WhatsApp Bridge using Selenium browser automation."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "WhatsAppSeleniumBridge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.driver = None
        self.is_logged_in = False

    def initialize(self):
        if not webdriver:
            print("[-] Selenium not installed. Run: pip install selenium webdriver-manager")
            return

        print("[*] Initializing WhatsApp Web Bridge (Hacker Way)...")
        options = webdriver.ChromeOptions()
        
        # Keep user profile so you don't have to scan QR every time
        profile_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data", "WhatsAppBot")
        options.add_argument(f"user-data-dir={profile_path}")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.driver.get("https://web.whatsapp.com")
            print("[*] WhatsApp Web launched. Please scan the QR code if this is your first time...")
            
            # Wait up to 60 seconds for the user to scan the QR code and chat list to load
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-tab="3"]'))
            )
            self.is_logged_in = True
            print("[+] WhatsApp Web successfully linked and active!")
        except Exception as e:
            print(f"[-] WhatsApp Web initialization failed or timed out: {e}")
            if self.driver:
                self.driver.quit()
                self.driver = None

    def send_message(self, contact_name: str, message: str) -> bool:
        if not self.is_logged_in or not self.driver:
            print("[-] Cannot send WhatsApp message. Bridge is not logged in.")
            return False
            
        try:
            # 1. Search for the contact
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-tab="3"]'))
            )
            search_box.clear()
            search_box.send_keys(contact_name)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)
            
            # 2. Type and send the message
            msg_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@data-tab="10"]'))
            )
            msg_box.click()
            time.sleep(1)
            
            # Use JS execCommand to safely inject text into the React contenteditable
            self.driver.execute_script("document.execCommand('insertText', false, arguments[0]);", message)
            time.sleep(1)
            
            # Click the explicit send button
            send_button = self.driver.find_element(By.XPATH, '//button[@aria-label="Send" or .//span[@data-icon="send"]]')
            send_button.click()
            
            print(f"[+] Successfully sent autonomous message to {contact_name}")
            return True
        except Exception as e:
            print(f"[-] Failed to send message to {contact_name}: {e}")
            return False
