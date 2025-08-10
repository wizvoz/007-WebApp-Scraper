#
# FILENAME: scraper_master.py
# AUTHOR:   Simon & Dora
# VERSION:  2.0 (Master)
#
# DESCRIPTION:
# The main entry point for the scraper application. It determines
# whether to run the setup wizard or the scraper engine based on
# command-line arguments.
#

import sys
from setup_wizard import run_setup_wizard
from scraper_engine import run_scraper

def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        version_arg = sys.argv[1]
        if version_arg.isdigit():
            run_scraper(version_arg)
        else:
            print(f"[FATAL ERROR] Argument '{version_arg}' is not a valid version number.")
    else:
        run_setup_wizard()

if __name__ == "__main__":
    main()