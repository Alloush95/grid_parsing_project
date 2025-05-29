# File: grid_parser_project/step1_data_collection.py
# Purpose: Step 1 - Automate screenshot capture and UI element annotation

from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from datetime import datetime
import time, os, json
import pandas as pd

# Custom helper functions and configuration constants
from utils.driver_setup import setup_selenium_driver
from utils.helpers import dismiss_cookies, categorize_ui_type
from config import (
    SCREENSHOT_DIR_STEP1,
    JSON_SUBDIR_STEP1, JSON_SUBDIR_STEP7,JSON_SUBDIR_STEP5,
    CSV_SUBDIR_STEP1, CSV_SUBDIR_STEP7, CSV_SUBDIR_STEP5,
    UI_DATA_DIR
)


def capture_ui_screenshots(urls, headless=False, screenshot_dir=SCREENSHOT_DIR_STEP1):
    """
    Launch browser, visit each URL, capture screenshot, extract UI components,
    and save annotations in JSON and CSV formats. Also records the step for downstream processing.
    """

    # Local step detection helper
    def detect_step_from_path(path: str) -> str:
        path = path.lower()
        if "step7" in path:
            return "step7"
        elif "step5" in path:
            return "step5"
        return "step1"

    # Setup Selenium WebDriver
    driver = setup_selenium_driver(headless=headless)
    device_label = "Desktop"
    w, h = 1920, 1080
    driver.set_window_size(w, h)

    screenshot_count = 0
    os.makedirs(screenshot_dir, exist_ok=True)

    # Detect which step we're in based on the directory
    step = detect_step_from_path(screenshot_dir)

    # Select the right output directories based on the step
    json_subdir = {
        "step1": JSON_SUBDIR_STEP1,
        "step5": JSON_SUBDIR_STEP5,
        "step7": JSON_SUBDIR_STEP7
    }.get(step, JSON_SUBDIR_STEP1)

    csv_subdir = {
        "step1": CSV_SUBDIR_STEP1,
        "step5": CSV_SUBDIR_STEP5,
        "step7": CSV_SUBDIR_STEP7
    }.get(step, CSV_SUBDIR_STEP1)

    os.makedirs(json_subdir, exist_ok=True)
    os.makedirs(csv_subdir, exist_ok=True)

    for url in urls:
        try:
            driver.get(url)
            time.sleep(3)

            # Detect and skip Cloudflare protection pages
            if "unusual traffic" in driver.page_source.lower():
                print(f"Cloudflare block detected for {url}. Skipping.")
                continue

            # Attempt to dismiss cookie banners
            for _ in range(2):
                dismiss_cookies(driver)
                time.sleep(3)

            # Generate screenshot filename and path
            domain = urlparse(url).netloc.replace("www.", "").replace(".", "_")
            shot_name = f"{domain}_{device_label.lower()}.png"
            shot_path = os.path.join(screenshot_dir, shot_name)
            driver.save_screenshot(shot_path)

            # Initialize metadata and UI component list
            ui_data = {
                "URL": url,
                "Step": step,
                "Viewport": device_label,
                "Screenshot": os.path.basename(shot_path),
                "Resolution": f"{w}x{h}",
                "CaptureTime": datetime.utcnow().isoformat(),
                "Category": categorize_ui_type(url),
                "UI Components": []
            }

            # Extract UI components via XPath
            elements = driver.find_elements(By.XPATH, "//button | //input | //a | //img | //div")
            for elem in elements:
                try:
                    loc = elem.location
                    sz = elem.size
                    ui_data["UI Components"].append({
                        "Tag": elem.tag_name,
                        "Text": (elem.text or "N/A").strip(),
                        "Role": elem.get_attribute("role") or "",
                        "AriaLabel": elem.get_attribute("aria-label") or "",
                        "Class": elem.get_attribute("class") or "",
                        "InnerHTML": elem.get_attribute("innerHTML") or "",
                        "X": loc["x"],
                        "Y": loc["y"],
                        "Width": sz["width"],
                        "Height": sz["height"],
                        "Timestamp": datetime.utcnow().isoformat()
                    })
                except:
                    continue  # Skip elements that cause issues

            # Save JSON
            json_path = os.path.join(json_subdir, f"{domain}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(ui_data, jf, indent=4)

            # Save CSV
            csv_path = os.path.join(csv_subdir, f"{domain}.csv")
            pd.DataFrame(ui_data["UI Components"]).to_csv(csv_path, index=False)

            screenshot_count += 1
            print(f"Captured {url} -> {shot_path}")

        except Exception as ex:
            print(f"Failed to capture {url}: {ex}")

    # Merge all CSVs into one file for convenience
    merged_csv_path = os.path.join(UI_DATA_DIR, "merged_ui_data.csv")
    all_csvs = [os.path.join(csv_subdir, f) for f in os.listdir(csv_subdir)
                if f.endswith(".csv") and not f.startswith("merged")]
    if all_csvs:
        merged_df = pd.concat((pd.read_csv(f) for f in all_csvs), ignore_index=True)
        merged_df.to_csv(merged_csv_path, index=False)
        print(f"Merged dataset saved to: {merged_csv_path}")
    else:
        print("No CSV files found to merge.")

    driver.quit()
    print(f"Step {step}: Data Collection & Annotation - COMPLETED! ({screenshot_count} screenshots captured)")
