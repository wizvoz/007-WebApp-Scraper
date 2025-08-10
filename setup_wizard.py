#
# FILENAME: setup_wizard.py
# AUTHOR:   Simon & Dora
# VERSION:  3.0 (Module with Auto-Versioning)
#
# DESCRIPTION:
# A dedicated module to handle the interactive setup of new,
# versioned scraping runs. Automatically detects and suggests
# the next version number.
#

import os
import re
import json
from datetime import datetime

CHANGELOG_FILE = "CHANGELOG.md"

def get_latest_version_in_dir():
    """Scans the current directory for input_vXX folders and finds the highest version number."""
    latest_version = 0
    pattern = re.compile(r'^input_v(\d+)$')
    for item in os.listdir('.'):
        if os.path.isdir(item):
            match = pattern.match(item)
            if match:
                version = int(match.group(1))
                if version > latest_version:
                    latest_version = version
    return latest_version

def run_setup_wizard():
    """Interactively sets up a new versioned run."""
    print("--- Scraper Setup Wizard ---")
    try:
        latest_version = get_latest_version_in_dir()
        suggested_version = latest_version + 1
        
        prompt = f"> Enter the version number for this new run (suggested: {suggested_version}): "
        version_str = input(prompt).strip()
        
        if not version_str: # User pressed Enter to accept the suggestion
            version = suggested_version
        elif version_str.isdigit():
            version = int(version_str)
        else:
            print("[FATAL ERROR] Version must be a number.")
            return

        input_dir = f"input_v{version}"
        output_dir = f"output_v{version}"
        config_file = os.path.join(input_dir, "config.json")

        if os.path.exists(input_dir) or os.path.exists(output_dir):
            print(f"[FATAL ERROR] Run v{version} already exists. Please choose a new version number.")
            return

        suggested_title = f"Scraping run on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        print(f"Suggested title: {suggested_title}")
        user_input_title = input("> Press ENTER to accept, or type your own title: ").strip()
        final_title = user_input_title if user_input_title else suggested_title

        print(f"\n[INFO] Creating directory: {input_dir}")
        os.makedirs(input_dir, exist_ok=True)
        print(f"[INFO] Creating directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

        previous_config_file = os.path.join(f"input_v{version - 1}", "config.json")
        if os.path.exists(previous_config_file):
            print(f"[INFO] Copying configuration from previous version (v{version - 1})...")
            with open(previous_config_file, 'r', encoding='utf-8') as f_old:
                config_data = json.load(f_old)
            with open(config_file, 'w', encoding='utf-8') as f_new:
                json.dump(config_data, f_new, indent=2)
        else:
            print(f"[INFO] No previous config found. Creating default config file...")
            default_config = {"chat_ids_to_scrape": "1-10", "delay_seconds": 5}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
        
        print(f"[INFO] Updating '{CHANGELOG_FILE}'...")
        with open(CHANGELOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## v{version}.0 - ({datetime.now().strftime('%Y-%m-%d')})\n")
            f.write(f"- User Note: {final_title}\n")
            f.write(f"- Executed hybrid Firefox scraper using this configuration.\n")

        print("\n" + "="*50)
        print(f"✅ Setup for run v{version} is complete.")
        print("ACTION REQUIRED: Please edit the configuration file:")
        print(os.path.abspath(config_file))
        print("\nWhen you are ready, run the scraper again with the version number:")
        print(f"python scraper_master.py {version}")
        print("="*50 + "\n")
        
        input(">>> Press Enter to acknowledge and return to the command prompt...")

    except Exception as e:
        print(f"[FATAL ERROR] Setup failed: {e}")