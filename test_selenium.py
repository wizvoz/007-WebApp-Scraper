#
# FILENAME: test_selenium.py
# AUTHOR:   Simon & Dora
# VERSION:  7.0
#
# DESCRIPTION:
# Adds anti-detection options to make the browser appear more human
# and allow Google login.
#

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

## ------------------- CONFIGURATION ------------------- ##
#
TARGET_URL = "https://gemini.google.com/app"

## ----------------------------------------------------- ##

def main():
    """
    Main function to run the browser automation test with manual login.
    """
    print("[DEBUG] Script starting...")
    print("[DEBUG] Launching an anti-detection browser instance...")

    # --- New code to make the browser look more human ---
    options = Options()
    # This removes the "Chrome is being controlled by automated test software" banner
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    # This disables a feature that allows websites to detect automation
    options.add_argument("--disable-blink-features=AutomationControlled")
    # ----------------------------------------------------

    # This launches a browser with our new anti-detection options.
    driver = webdriver.Chrome(options=options)

    driver.get("https://accounts.google.com/")
    
    print("\n" + "="*50)
    print("ACTION REQUIRED: Please log in to your Google Account.")
    print("="*50 + "\n")

    input(">>> After you are logged in, press Enter here to continue...")

    print("\n[DEBUG] Login complete. Resuming script...")
    print(f"[DEBUG] Navigating to target: {TARGET_URL}")

    driver.get(TARGET_URL)

    print("[DEBUG] Page loaded. Waiting for 20 seconds...")
    time.sleep(20)

    driver.quit()
    print("[DEBUG] Browser closed. Script finished.")


if __name__ == "__main__":
    main()