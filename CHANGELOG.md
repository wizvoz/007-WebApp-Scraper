# Scraper Project Changelog

## v26.0 (Master Version)
- Finalized architecture to use a master script that is renamed for each versioned run (e.g., `scraper_v26.py`).
- The script automatically detects its version from its filename.
- It reads configuration from a version-matched input folder (e.g., `input_v26/config.json`).
- It saves results to a version-matched output folder (e.g., `output_v26/`).
- This creates a fully organized, reproducible, and non-interactive workflow.

## v19.0 - v25.0
- Introduced and refined the definitive "Hybrid" workflow, the first stable, working version.
- Script pauses to allow for manual user scroll-up, bypassing the final automation block after extensive testing of automated scrolling proved it unfeasible.
- Added a text-cleanup function to remove excess whitespace from the saved files.
- Performed focused diagnostics on scrolling, confirming the Gemini app does not respond to simulated scroll-up events.

## v10.0 - v18.0
- **Switched to Firefox.** This was the major breakthrough that solved the persistent browser crashing issues seen with Chrome.
- Proved that loading an existing Firefox profile was stable, removing the need for manual logins.
- Identified and confirmed the correct CSS selectors for Firefox.
- Developed the "gentle scroll" (`Page Down`) and "scroll to top" (`Home` key) methods.

## v1.0 - v9.0
- Initial exploration using JavaScript snippets, successfully extracting titles and URLs into a JSON file.
- First Python/Selenium versions using Chrome. Identified critical roadblocks with Chrome profile loading (crashes), attaching to running instances (instability), and Google's bot detection.
- Developed anti-detection flags that allowed manual logins to succeed in a clean profile.

## v28.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 12:03
- Executed hybrid Firefox scraper using this configuration.


## v29.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 12:41
- Executed hybrid Firefox scraper using this configuration.


## v29.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 12:42
- Executed hybrid Firefox scraper using this configuration.


## v30.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 13:01
- Executed hybrid Chrome scraper (undetected) using this configuration.


## v30.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 13:03
- Executed hybrid Chrome scraper (undetected) using this configuration.


## v31.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 13:36
- Executed hybrid Firefox scraper using this configuration.


## v35.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 15:33
- Executed hybrid Firefox scraper using this configuration.


## v36.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 16:07
- Executed hybrid Firefox scraper using this configuration.


## v37.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 16:27
- Executed hybrid Firefox scraper using this configuration.


## v38.0 - (2025-08-10)
- User Note: Scraping run on 2025-08-10 16:58
- Executed hybrid Firefox scraper using this configuration.
