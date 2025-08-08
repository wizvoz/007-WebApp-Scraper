#
# FILENAME: list_chats.py
# AUTHOR:   Simon & Dora
# VERSION:  1.0
#
# DESCRIPTION:
# A simple utility to read the chats.json file and print a
# numbered list of all chat titles.
#

import json

## ------------------- CONFIGURATION ------------------- ##
JSON_SOURCE_FILE = "chats.json"
## ----------------------------------------------------- ##

def main():
    """Reads the JSON file and prints the list of chats."""
    print(f"[INFO] Reading chats from '{JSON_SOURCE_FILE}'...")
    try:
        with open(JSON_SOURCE_FILE, 'r', encoding='utf-8') as f:
            chats = json.load(f)
        
        if not chats:
            print("[ERROR] No chats found in the file.")
            return
            
        print("-" * 50)
        # Loop through all chats and print their ID and title
        for chat in chats:
            chat_id = chat.get('id', 'N/A')
            chat_title = chat.get('title', 'Untitled')
            print(f"{chat_id}: {chat_title}")
        print("-" * 50)
        print(f"[SUCCESS] Listed {len(chats)} total chats.")

    except FileNotFoundError:
        print(f"[FATAL ERROR] The source file was not found: '{JSON_SOURCE_FILE}'")
    except json.JSONDecodeError:
        print(f"[FATAL ERROR] The file '{JSON_SOURCE_FILE}' is not a valid JSON file.")

if __name__ == "__main__":
    main()