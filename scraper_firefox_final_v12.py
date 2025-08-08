#
# FILENAME: scraper_firefox_final_v12.py
# AUTHOR:   Simon & Dora
# VERSION:  12.0
#
# DESCRIPTION:
# The definitive scraper, tuned specifically for the Firefox HTML structure.
# Uses an existing Firefox profile for automatic login, reads from JSON,
# is interactive, and uses gentle scrolling.
#

import time
import os
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## ------------------- CONFIGURATION ------------------- ##
#
# TODO: Ensure this path to your Firefox profile is correct.
#
FIREFOX_PROFILE_PATH = r"C:\Users\Simon\AppData\Roaming\Mozilla\Firefox\Profiles\21mwqfkq.default-release"

# The name of the JSON file containing the list of chats.
JSON_SOURCE_FILE = "chats.json"

# --- NEW: Selectors confirmed for Firefox ---
# We now look for the custom tags <user-query> and <model-response>.
# A comma in a CSS selector means "OR".
MESSAGE_CONTAINER_SELECTOR = "user-query, model-response"
# The class for the <p> tags inside a user query.
PROMPT_SELECTOR = ".query-text-line"
# The class for the main text body of a model response.
RESPONSE_SELECTOR = ".model-response-text"

OUTPUT_DIR = "scraped_conversations_final"

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
        print(f"[FATAL ERROR] The source file was not found: '{filename}'")
        return []
    except json.JSONDecodeError:
        print(f"[FATAL ERROR] The file '{filename}' is not a valid JSON file.")
        return []

def main():
    """Main function to run the scraper."""
    print("[INFO] Final Scraper v12.0 (Firefox Tuned) starting...")
    
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
        print("[INFO] Launching Firefox with your profile...")
        options = Options()
        options.profile = FIREFOX_PROFILE_PATH
        driver = webdriver.Firefox(options=options)
        print("[SUCCESS] Firefox launched successfully.")

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for chat in chats_to_process:
            chat_id = chat.get('id', 'N/A')
            chat_title = chat.get('title', 'Untitled')
            chat_url = chat.get('url', 'URL_MISSING')
            
            print(f"\n{'='*20} Processing Chat #{chat_id} {'='*20}")
            print(f"TITLE: {chat_title}")
            
            try:
                driver.get(chat_url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR))
                )

                body = driver.find_element(By.TAG_NAME, 'body')
                for _ in range(40):
                    body.send_keys(Keys.PAGE_DOWN); time.sleep(0.5)
                
                sanitized_title = sanitize_filename(chat_title)[:150]
                filename = os.path.join(OUTPUT_DIR, f"{chat_id:03d}_{sanitized_title}.txt")
                
                full_conversation = f"ID: {chat_id}\nURL: {chat_url}\nTITLE: {chat_title}\n\n---\n\n"
                
                # --- NEW: Logic to handle <user-query> and <model-response> tags ---
                message_containers = driver.find_elements(By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)
                for container in message_containers:
                    if container.tag_name == 'user-query':
                        # Find all text lines in the prompt and join them together.
                        prompt_lines = container.find_elements(By.CSS_SELECTOR, PROMPT_SELECTOR)
                        prompt_text = "\n".join([line.text for line in prompt_lines])
                        full_conversation += f"## PROMPT ##\n\n{prompt_text}\n\n---\n\n"
                    elif container.tag_name == 'model-response':
                        try:
                            response = container.find_element(By.CSS_SELECTOR, RESPONSE_SELECTOR)
                            full_conversation += f"## RESPONSE ##\n\n{response.text}\n\n---\n\n"
                        except: pass # In case a model-response container is found but the text isn't

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_conversation)
                print(f"[SUCCESS] Saved conversation to '{filename}'")

            except Exception as e:
                print(f"[ERROR] Failed to scrape chat #{chat_id}. Error: {e}")
                # Log error and continue to the next chat
            
            print(f"[INFO] Waiting for {delay_seconds} seconds...")
            time.sleep(delay_seconds)
            
    except Exception as e:
        print(f"[FATAL ERROR] An unexpected error occurred: {e}")
    
    finally:
        if driver:
            driver.quit()
        print("\n--- Scraping complete. ---")

if __name__ == "__main__":
    main()