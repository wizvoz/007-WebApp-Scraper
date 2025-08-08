#
# FILENAME: scraper_v9_attach.py
# AUTHOR:   Simon & Dora
# VERSION:  9.1
#
# DESCRIPTION:
# Connects to an already-running Chrome instance and scrapes one
# specific, known URL for testing purposes.
#

import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## ------------------- CONFIGURATION ------------------- ##
#
# Using the specific URL for this test.
#
URL_LIST = [
    "https://gemini.google.com/app/990538a96b777b26"
]

# Confirmed selectors
MESSAGE_CONTAINER_SELECTOR = ".message-content" 
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"

OUTPUT_DIR = "scraped_conversations_v9"
DELAY_BETWEEN_URLS_SECONDS = 5

## ----------------------------------------------------- ##

def sanitize_filename(name):
    """Removes characters that are invalid for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def main():
    """Main function to run the scraper."""
    print("[INFO] Scraper v9.1 (Attach Mode Test) starting...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[INFO] Conversations will be saved to '{OUTPUT_DIR}' folder.")

    driver = None
    try:
        # --- Connect to the existing browser ---
        print("[INFO] Attempting to connect to browser on port 9222...")
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=options)
        print("[SUCCESS] Successfully connected to existing browser.")

        # --- Main Scraping Loop ---
        for i, url in enumerate(URL_LIST):
            print(f"\n--- Scraping URL {i+1}/{len(URL_LIST)} ---")
            print(f"URL: {url}")
            
            try:
                driver.get(url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR))
                )
                print("[DEBUG] Page loaded.")

                print("[DEBUG] Gently scrolling down...")
                body = driver.find_element(By.TAG_NAME, 'body')
                for _ in range(40):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(0.5)
                print("[DEBUG] Finished scrolling.")

                title = sanitize_filename(driver.title)[:150]
                filename = os.path.join(OUTPUT_DIR, f"{i+1:03d}_{title}.txt")
                
                full_conversation = f"URL: {url}\nTITLE: {driver.title}\n\n---\n\n"
                
                message_containers = driver.find_elements(By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)
                for container in message_containers:
                    try:
                        prompt = container.find_element(By.CSS_SELECTOR, PROMPT_SELECTOR)
                        full_conversation += f"## PROMPT ##\n\n{prompt.text}\n\n---\n\n"
                        continue
                    except: pass
                    
                    try:
                        response = container.find_element(By.CSS_SELECTOR, RESPONSE_SELECTOR)
                        full_conversation += f"## RESPONSE ##\n\n{response.text}\n\n---\n\n"
                    except: pass

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_conversation)
                print(f"[SUCCESS] Saved conversation to '{filename}'")

            except Exception as e:
                print(f"[ERROR] Failed to scrape {url}. Error: {e}")
            
            print(f"[INFO] Waiting for {DELAY_BETWEEN_URLS_SECONDS} seconds...")
            time.sleep(DELAY_BETWEEN_URLS_SECONDS)
            
    except Exception as e:
        print(f"[FATAL ERROR] Could not connect to the browser. Is it running in debugging mode?")
        print(f"Error details: {e}")
    
    finally:
        if driver:
            driver.quit()
        print("\n--- Script finished. ---")

if __name__ == "__main__":
    main()