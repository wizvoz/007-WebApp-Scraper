#
# FILENAME: test_firefox_v10.py
# AUTHOR:   Simon & Dora
# VERSION:  10.0
#
# DESCRIPTION:
# A test script to see if Firefox can be launched with an existing
# user profile without crashing.
#

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

## ------------------- CONFIGURATION ------------------- ##
#
# TODO: Replace this with the actual path to your Firefox profile folder.
# The 'r' before the string is important - leave it there.
#
FIREFOX_PROFILE_PATH = r"C:\Users\Simon\AppData\Roaming\Mozilla\Firefox\Profiles\21mwqfkq.default-release"

# A known, simple URL for testing.
TARGET_URL = "https://gemini.google.com/app/990538a96b777b26"

## ----------------------------------------------------- ##

def main():
    """
    Main function for the Firefox stability test.
    """
    driver = None
    print("[INFO] Firefox Test v10.0 starting...")
    print(f"[INFO] Attempting to load profile: {FIREFOX_PROFILE_PATH}")
    
    try:
        options = Options()
        options.profile = FIREFOX_PROFILE_PATH
        
        driver = webdriver.Firefox(options=options)
        print("[SUCCESS] Firefox launched successfully with the specified profile.")
        
        print(f"[INFO] Navigating to: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        print("[INFO] Navigation complete. Waiting for 30 seconds for observation...")
        time.sleep(30)
        
        print("[INFO] Test complete. Browser appears stable.")

    except Exception as e:
        print("\n[FAILURE] An error occurred during the test.")
        print(f"Error details: {e}")
        
    finally:
        if driver:
            driver.quit()
        print("[INFO] Script finished.")


if __name__ == "__main__":
    main()