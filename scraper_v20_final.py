#
# FILENAME: scraper_v20_final.py
# AUTHOR:   Simon & Dora
# VERSION:  20.0
#
# DESCRIPTION:
# The definitive scraper. Implements the user-suggested strategy of
# scraping content in chunks while scrolling up the page to handle
# dynamic content loading in the most robust way possible.
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

# Selectors confirmed for Firefox
SCROLLABLE_ELEMENT_SELECTOR = "infinite-scroller"
MESSAGE_CONTAINER_SELECTOR = "user-query, model-response"
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"

# Versioned output directory
OUTPUT_DIR = "scraped_conversations_v20"

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

def parse_id_string(id_string, max_id):
    """Parses a string like '1, 5, 10-15' into a list of integers."""
    ids = set()
    parts = id_string.split(',')
    for part in parts:
        part = part.strip()
        if not part: continue
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if start > end: start, end = end, start
                for i in range(start, end + 1):
                    if 1 <= i <= max_id:
                        ids.add(i)
            except ValueError:
                print(f"[WARNING] Invalid range '{part}' ignored.")
        else:
            try:
                num = int(part)
                if 1 <= num <= max_id:
                    ids.add(num)
            except ValueError:
                print(f"[WARNING] Invalid number '{part}' ignored.")
    return sorted(list(ids))

def main():
    """Main function to run the scraper."""
    print(f"[INFO] Final Scraper {__file__} starting...")
    
    all_chats = parse_json_file(JSON_SOURCE_FILE)
    if not all_chats: return

    try:
        id_str = input(f"> Which of the {len(all_chats)} chats would you like to scrape? (e.g., '1-5, 8, 12'): ")
        if not id_str:
            print("[INFO] No selection made. Exiting.")
            return
        
        target_ids = parse_id_string(id_str, len(all_chats))
        if not target_ids:
            print("[ERROR] No valid chat IDs selected. Exiting.")
            return

        delay_str = input(f"> How many seconds to wait between chats? (e.g., 5): ")
        delay_seconds = int(delay_str) if delay_str else 5
    except ValueError:
        print("[FATAL ERROR] Invalid input. Please enter numbers only."); return

    # Filter the main list to only the chats we want to process
    chats_to_process = [chat for chat in all_chats if chat.get('id') in target_ids]
    print(f"\n[INFO] Preparing to scrape {len(chats_to_process)} selected chats with a {delay_seconds}-second delay.")

    driver = None
    try:
        print("[INFO] Launching Firefox with your profile...")
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
                
                # --- NEW: "Scrape-as-you-scroll-up" logic ---
                print("[INFO] Scraping chat from bottom to top...", end=''); sys.stdout.flush()
                scraped_chunks = []
                scraped_ids = set()

                while True:
                    new_messages_found = False
                    messages = driver.find_elements(By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)
                    
                    for message in messages:
                        message_id = message.get_attribute('id')
                        if message_id and message_id not in scraped_ids:
                            new_messages_found = True
                            scraped_ids.add(message_id)
                            chunk = {'tag': message.tag_name, 'text': message.text}
                            scraped_chunks.append(chunk)

                    if not new_messages_found:
                        # No new messages found after scrolling, we must be at the top
                        break
                    
                    # Scroll up to find more
                    scroll_area.send_keys(Keys.PAGE_UP)
                    print(".", end=''); sys.stdout.flush()
                    time.sleep(2) # Give time for content to load

                print("\n[INFO] Reached the top. Assembling conversation...")
                scraped_chunks.reverse() # Reverse to get correct chronological order

                # --- Assemble and Save ---
                sanitized_title = sanitize_filename(chat_title)[:150]
                filename = os.path.join(OUTPUT_DIR, f"{chat_id:03d}_{sanitized_title}.txt")
                
                full_conversation = f"ID: {chat_id}\nURL: {chat_url}\nTITLE: {chat_title}\n\n---\n\n"
                
                for chunk in scraped_chunks:
                    if chunk['tag'] == 'user-query':
                        full_conversation += f"## PROMPT ##\n\n{chunk['text']}\n\n---\n\n"
                    elif chunk['tag'] == 'model-response':
                        full_conversation += f"## RESPONSE ##\n\n{chunk['text']}\n\n---\n\n"

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_conversation)
                print(f"[SUCCESS] Saved conversation to '{filename}'")

            except Exception as e:
                print(f"\n[ERROR] Failed to scrape chat #{chat_id}. Error: {e}")
            
            time.sleep(delay_seconds) # Simple sleep is fine here
            
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
    
    finally:
        if driver:
            driver.quit()
        print("\n--- Scraping complete. ---")

if __name__ == "__main__":
    main()