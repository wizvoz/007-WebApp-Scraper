#
# FILENAME: scraper_v18.py
# AUTHOR:   Simon & Dora
# VERSION:  18.0
#
# DESCRIPTION:
# The definitive scraper. Uses a "Page Up" loop to force-load the
# beginning of long conversations. This is the final version.
#

import time
import os
import re
import json
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## ------------------- CONFIGURATION ------------------- ##
#
FIREFOX_PROFILE_PATH = r"C:\Users\Simon\AppData\Roaming\Mozilla\Firefox\Profiles\21mwqfkq.default-release"
JSON_SOURCE_FILE = "chats.json"

# --- Selectors confirmed for Firefox ---
SCROLLABLE_ELEMENT_SELECTOR = "infinite-scroller"
MESSAGE_CONTAINER_SELECTOR = "user-query, model-response"
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"

# Versioned output directory
OUTPUT_DIR = "scraped_conversations_v18"

## ----------------------------------------------------- ##

def sanitize_filename(name):
    """Removes characters that are invalid for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def parse_json_file(filename):
    """Reads the list of chats from the specified JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[INFO] Successfully loaded {len(data)} chats from '{filename}'.")
        return data
    except FileNotFoundError:
        print(f"[FATAL ERROR] The source file '{filename}' was not found."); return []
    except json.JSONDecodeError:
        print(f"[FATAL ERROR] The file '{filename}' is not a valid JSON file."); return []

def visual_countdown(seconds):
    """Displays a simple countdown timer in the terminal."""
    for i in range(seconds, 0, -1):
        print(f"[INFO] Waiting for {i} second(s)...", end='\r'); sys.stdout.flush()
        time.sleep(1)
    print(" " * 40, end='\r')

def main():
    """Main function to run the scraper."""
    print(f"[INFO] Final Scraper {__file__} starting...")
    
    all_chats = parse_json_file(JSON_SOURCE_FILE)
    if not all_chats: return

    try:
        num_str = input(f"> How many of the {len(all_chats)} chats would you like to scrape? (Press Enter for all): ")
        num_to_scrape = int(num_str) if num_str else len(all_chats)
        delay_str = input(f"> How many seconds to wait between chats? (e.g., 5): ")
        delay_seconds = int(delay_str) if delay_str else 5
    except ValueError:
        print("[FATAL ERROR] Invalid input. Please enter numbers only."); return

    chats_to_process = all_chats[:num_to_scrape]
    print(f"\n[INFO] Preparing to scrape {len(chats_to_process)} chats with a {delay_seconds}-second delay.")

    driver = None
    try:
        print("[INFO] Launching Firefox with your profile... (This can take some time)")
        options = Options()
        options.profile = FIREFOX_PROFILE_PATH
        driver = webdriver.Firefox(options=options)
        print("[SUCCESS] Firefox launched successfully.")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for chat in chats_to_process:
            chat_id, chat_title, chat_url = chat.get('id', 'N/A'), chat.get('title', 'Untitled'), chat.get('url', 'URL_MISSING')
            
            print(f"\n{'='*20} Processing Chat #{chat_id} {'='*20}")
            print(f"TITLE: {chat_title}")
            
            try:
                driver.get(chat_url)
                print("[INFO] Waiting for page to load...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SCROLLABLE_ELEMENT_SELECTOR))
                )

                scroll_area = driver.find_element(By.CSS_SELECTOR, SCROLLABLE_ELEMENT_SELECTOR)
                
                # --- NEW: "Page Up" scroll loop to get the beginning ---
                print("[INFO] Scrolling UP to load full history...", end=''); sys.stdout.flush()
                scroll_attempts = 40 
                for _ in range(scroll_attempts):
                    scroll_area.send_keys(Keys.PAGE_UP)
                    print(".", end=''); sys.stdout.flush()
                    time.sleep(0.5)
                print("\n[INFO] Finished scrolling up.")
                # ---

                print("[INFO] Scrolling DOWN to ensure all content is loaded...", end=''); sys.stdout.flush()
                for _ in range(scroll_attempts):
                    scroll_area.send_keys(Keys.PAGE_DOWN)
                    print(".", end=''); sys.stdout.flush()
                    time.sleep(0.5)
                print("\n[INFO] Finished scrolling down.")

                sanitized_title = sanitize_filename(chat_title)[:150]
                filename = os.path.join(OUTPUT_DIR, f"{chat_id:03d}_{sanitized_title}.txt")
                
                full_conversation = f"ID: {chat_id}\nURL: {chat_url}\nTITLE: {chat_title}\n\n---\n\n"
                
                message_containers = driver.find_elements(By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)
                for container in message_containers:
                    if container.tag_name == 'user-query':
                        prompt_lines = container.find_elements(By.CSS_SELECTOR, PROMPT_SELECTOR)
                        prompt_text = "\n".join([line.text for line in prompt_lines])
                        full_conversation += f"## PROMPT ##\n\n{prompt_text}\n\n---\n\n"
                    elif container.tag_name == 'model-response':
                        try:
                            response = container.find_element(By.CSS_SELECTOR, RESPONSE_SELECTOR)
                            full_conversation += f"## RESPONSE ##\n\n{response.text}\n\n---\n\n"
                        except: pass

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_conversation)
                print(f"[SUCCESS] Saved conversation to '{filename}'")

            except Exception as e:
                print(f"\n[ERROR] Failed to scrape chat #{chat_id}. Error: {e}")
            
            visual_countdown(delay_seconds)
            
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
    
    finally:
        if driver:
            driver.quit()
        print("\n--- Scraping complete. ---")

if __name__ == "__main__":
    main()