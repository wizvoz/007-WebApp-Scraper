#
# FILENAME: scraper_engine.py
# AUTHOR:   Simon & Dora
# VERSION:  4.0 (Module - Fully Automated Scroll)
#
# DESCRIPTION:
# The definitive core scraping engine. Assumes user is already logged in
# to Firefox and uses an automated, intelligent scroll-up loop.
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

## ------------------- STATIC CONFIGURATION ------------------- ##
#
FIREFOX_PROFILE_PATH = r"C:\Users\SimonC\AppData\Roaming\Mozilla\Firefox\Profiles\dc04l8pf.default-release"
MASTER_CHAT_LIST_FILE = "chats.json"

# Selectors confirmed for Firefox
SCROLLABLE_ELEMENT_SELECTOR = ".chat-container"
MESSAGE_CONTAINER_SELECTOR = "user-query, model-response"
PROMPT_SELECTOR = ".query-text-line"
RESPONSE_SELECTOR = ".model-response-text"
## ----------------------------------------------------------- ##

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

def run_scraper(version):
    """Executes the scraping process for a given version."""
    INPUT_DIR = f"input_v{version}"
    OUTPUT_DIR = f"output_v{version}"
    CONFIG_FILE = os.path.join(INPUT_DIR, "config.json")
    
    print(f"[INFO] Scraper v{version} starting...")

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f: config = json.load(f)
        all_chats = json.load(open(MASTER_CHAT_LIST_FILE, 'r', encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[FATAL ERROR] Could not load input files. Error: {e}"); return
        
    target_ids = parse_id_string(config.get("chat_ids_to_scrape", ""), len(all_chats))
    delay_seconds = config.get("delay_seconds", 5)
    
    if not target_ids:
        print("[ERROR] No valid chat IDs specified in config.json. Exiting."); return

    chats_to_process = [chat for chat in all_chats if chat.get('id') in target_ids]
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
            chat_id, chat_title, chat_url = chat.get('id', 'N/A'), chat.get('title', 'Untitled'), chat.get('url', 'URL_MISSING')
            
            print(f"\n{'='*20} Processing Chat #{chat_id} {'='*20}")
            print(f"TITLE: {chat_title}")
            
            try:
                driver.get(chat_url)
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, MESSAGE_CONTAINER_SELECTOR)))
                
                scroll_area = driver.find_element(By.CSS_SELECTOR, SCROLLABLE_ELEMENT_SELECTOR)
                
                # --- Automated Smart Scroll-Up Loop ---
                print("[INFO] Beginning smart scroll-up...", end=''); sys.stdout.flush()
                last_height = -1
                attempts = 0
                max_loops = 15 # Safety break
                while attempts < max_loops:
                    last_height = driver.execute_script("return arguments[0].scrollHeight;", scroll_area)
                    for _ in range(20): # Burst of Page Ups
                        scroll_area.send_keys(Keys.PAGE_UP)
                        time.sleep(0.1)
                    time.sleep(3) # Pause for content to load
                    current_height = driver.execute_script("return arguments[0].scrollHeight;", scroll_area)
                    if current_height == last_height:
                        print("\n[INFO] Top of conversation reached."); break
                    print(".", end=''); sys.stdout.flush()
                    attempts += 1
                
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