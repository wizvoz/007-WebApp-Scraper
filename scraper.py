#
# FILENAME: scraper.py
# AUTHOR:   Simon & Dora
# VERSION:  8.0
#
# DESCRIPTION:
# A robust scraper that restarts the browser for each URL and uses a
# gentle "Page Down" scrolling method to prevent browser crashes.
#

import time
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # <-- New import for Page Down key
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## ------------------- CONFIGURATION ------------------- ##
#
# TODO: Paste the URLs you want to scrape here.
#
URL_LIST = [
    "https://gemini.google.com/app/PASTE_A_PREVIOUSLY_FAILING_URL_HERE",
]

# Confirmed selectors
MESSAGE_CONTAINER_SELECTOR = ".message-content" 
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"

OUTPUT_DIR = "scraped_conversations"
DELAY_BETWEEN_URLS_SECONDS = 2 

## ----------------------------------------------------- ##

def sanitize_filename(name):
    """Removes characters that are invalid for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def main():
    """Main function to run the scraper."""
    print("[INFO] Scraper v8.0 starting...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[INFO] Conversations will be saved to '{OUTPUT_DIR}' folder.")

    for i, url in enumerate(URL_LIST):
        print(f"\n{'='*20} Processing URL {i+1}/{len(URL_LIST)} {'='*20}")
        print(f"URL: {url}")
        
        driver = None
        try:
            options = Options()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Chrome(options=options)

            driver.get("https://accounts.google.com/")
            print("\n[ACTION REQUIRED] Please log in to your Google Account.")
            input(">>> After logging in, press Enter here to continue...")
            print("\n[INFO] Login complete. Proceeding to scrape...")

            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR))
            )
            print("[DEBUG] Page loaded.")

            # --- New, gentler scrolling logic ---
            print("[DEBUG] Gently scrolling down by simulating Page Down key...")
            body = driver.find_element(By.TAG_NAME, 'body')
            # Scroll down a fixed number of times to load content.
            # Increase this number if your chats are extremely long.
            scroll_attempts = 40 
            for _ in range(scroll_attempts):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5) # A brief pause to allow content to load
            print("[DEBUG] Finished scrolling.")
            # ------------------------------------

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
            print(f"[ERROR] Failed to process {url}. Error: {e}")
            error_filename = os.path.join(OUTPUT_DIR, f"ERROR_URL_{i+1:03d}.txt")
            with open(error_filename, 'w', encoding='utf-8') as f:
                f.write(f"Failed to process URL: {url}\n\nError:\n{e}")
        
        finally:
            if driver:
                driver.quit()
            print("[INFO] Browser closed. Moving to next URL.")

        time.sleep(DELAY_BETWEEN_URLS_SECONDS)
        
    print("\n--- Scraping complete. ---")

if __name__ == "__main__":
    main()