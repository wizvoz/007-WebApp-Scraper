#
# FILENAME: scraper_v34_final.py
# AUTHOR:   Simon & Dora
# VERSION:  34.0 (Definitive Hybrid Version with Bug Fix)
#
# DESCRIPTION:
# The definitive scraper. This version restores a missing helper function
# from v33 and represents the complete, working code.
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
FIREFOX_PROFILE_PATH = r"C:\Users\SimonC\AppData\Roaming\Mozilla\Firefox\Profiles\dc04l8pf.default-release"
JSON_SOURCE_FILE = "chats.json"

# --- Selectors confirmed for Firefox ---
SCROLLABLE_ELEMENT_SELECTOR = ".chat-container"
MESSAGE_CONTAINER_SELECTOR = "user-query, model-response"
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"

# Versioned output directory
OUTPUT_DIR = "output_v34"

## ----------------------------------------------------- ##

def sanitize_filename(name):
    """Removes characters that are invalid for Windows filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def clean_text(text):
    """Strips leading/trailing whitespace and collapses multiple newlines."""
    if not text: return ""
    stripped_text = text.strip()
    return re.sub(r'\n{3,}', '\n\n', stripped_text)

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
            except ValueError: print(f"[WARNING] Invalid range '{part}' ignored.")
        else:
            try:
                num = int(part)
                if 1 <= num <= max_id:
                    ids.add(num)
            except ValueError: print(f"[WARNING] Invalid number '{part}' ignored.")
    return sorted(list(ids))

def visual_countdown(seconds):
    """Displays a simple countdown timer in the terminal."""
    for i in range(seconds, 0, -1):
        print(f"[INFO] Waiting for {i} second(s)...", end='\r'); sys.stdout.flush()
        time.sleep(1)
    print(" " * 40, end='\r')
    
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

def main():
    """Main function to run the scraper."""
    print(f"[INFO] Final Scraper {__file__} starting...")
    
    all_chats = parse_json_file(JSON_SOURCE_FILE)
    if not all_chats: return

    try:
        id_str = input(f"> Which of the {len(all_chats)} chats would you like to scrape? (e.g., '1-5, 8, 12'): ")
        if not id_str:
            print("[INFO] No selection made. Exiting."); return
        
        target_ids = parse_id_string(id_str, len(all_chats))
        if not target_ids:
            print("[ERROR] No valid chat IDs selected. Exiting."); return

        delay_str = input(f"> How many seconds to wait between chats? (e.g., 3): ")
        delay_seconds = int(delay_str) if delay_str else 3
    except ValueError:
        print("[FATAL ERROR] Invalid input. Please enter numbers only."); return

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
                
                print("\n" + "="*50)
                print("ACTION REQUIRED: Manually scroll to the TOP of the conversation")
                print("                 in the Firefox window to load the full history.")
                print("="*50 + "\n")
                input(">>> Once at the top, press Enter here to continue scraping...")
                time.sleep(2)
                
                print("[INFO] Beginning scrape...")
                
                sanitized_title = sanitize_filename(chat_title)[:150]
                filename = os.path.join(OUTPUT_DIR, f"{chat_id:03d}_{sanitized_title}.txt")
                
                full_conversation = f"ID: {chat_id}\nURL: {chat_url}\nTITLE: {chat_title}\n\n---\n\n"
                
                message_containers = driver.find_elements(By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)
                for container in message_containers:
                    if container.tag_name == 'user-query':
                        prompt_lines = container.find_elements(By.CSS_SELECTOR, PROMPT_SELECTOR)
                        prompt_text = "\n".join([line.text for line in prompt_lines if line.text.strip()])
                        full_conversation += f"## PROMPT ##\n\n{clean_text(prompt_text)}\n\n---\n\n"
                    elif container.tag_name == 'model-response':
                        try:
                            response = container.find_element(By.CSS_SELECTOR, RESPONSE_SELECTOR)
                            full_conversation += f"## RESPONSE ##\n\n{clean_text(response.text)}\n\n---\n\n"
                        except: pass

                with open(filename, 'w', encoding='utf-8') as f: f.write(full_conversation)
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