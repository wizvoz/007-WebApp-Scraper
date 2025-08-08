#
# FILENAME: test_v7.0.py
# AUTHOR:   Simon & Dora
# VERSION:  7.0
#
# DESCRIPTION:
# A minimal diagnostic script to test if navigating to a specific
# chat URL causes an immediate browser crash after a manual login.
#

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

## ------------------- CONFIGURATION ------------------- ##
#
# TODO: Paste ONE of the URLs that has been failing here.
#
TARGET_URL = "https://gemini.google.com/app/990538a96b777b26"

## ----------------------------------------------------- ##

def main():
    """
    Main function for the navigation stability test.
    """
    driver = None
    try:
        print("[INFO] Test v7.0 starting...")
        
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)

        driver.get("https://accounts.google.com/")
        print("\n[ACTION REQUIRED] Please log in to your Google Account.")
        input(">>> After logging in, press Enter here to continue...")

        print(f"\n[INFO] Login complete. Attempting to navigate to target URL...")
        print(f"URL: {TARGET_URL}")
        
        # This is the critical test.
        driver.get(TARGET_URL)
        
        print("\n[SUCCESS] Navigation complete. The browser appears stable.")
        print("         The script will now wait for 60 seconds for observation.")
        
        time.sleep(60)
        
        print("[INFO] 60-second wait is over. The browser did not crash.")

    except Exception as e:
        print("\n[FAILURE] An error occurred. The browser may have crashed.")
        print(f"Error details: {e}")
        
    finally:
        if driver:
            driver.quit()
        print("[INFO] Script finished.")

if __name__ == "__main__":
    main()