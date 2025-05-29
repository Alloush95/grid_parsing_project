# File: grid_parser_project/step5_prototype.py
# Purpose: Step 5 - Integrate full pipeline and run end-to-end on test URLs

# Import each modular step of the pipeline
from step1_data_collection import capture_ui_screenshots
from step2_grid_parsing import process_ui_data_step2
from step3_computer_vision import process_step3
from step4_metrics_evaluation import step4_evaluation
from step6_ai_integration import step6_ai_integration

# Config paths for proper output routing
from config import (
    
    TEST_URLS_STEP5,
    JSON_SUBDIR_STEP5,
    LOG_DIR_STEP5,
    INTERACTION_SHOT_DIR_STEP5,
    SCREENSHOT_DIR_STEP5
)

def step5_prototype_development(test_urls=TEST_URLS_STEP5, headless=True):
    """
    Runs the entire parsing and evaluation pipeline on a set of test URLs.
    This includes: data collection, grid-based parsing, CV annotation,
    interaction simulation, and metric evaluation.

    Args:
        test_urls (list): URLs to process.
        headless (bool): Whether to run browser in headless mode.
    """
    print("\n=== STEP 5: Prototype Development ===")

    # Step 1: Capture screenshots and extract UI element metadata
    capture_ui_screenshots(test_urls, headless=False, screenshot_dir=SCREENSHOT_DIR_STEP5)


    # Step 2: Apply grid parsing and assign components to spatial cells
    process_ui_data_step2(json_dir=JSON_SUBDIR_STEP5, screenshot_dir=SCREENSHOT_DIR_STEP5)

    # Step 3: Apply OpenCV, Tesseract OCR, and YOLO-compatible annotations
    process_step3(json_dir=JSON_SUBDIR_STEP5, screenshot_dir=SCREENSHOT_DIR_STEP5)

    # Step 4: Compute parsing metrics (Hit rate, Density, Entropy, CRs)
    step4_evaluation(
        json_dir=JSON_SUBDIR_STEP5,
        csv_filename="evaluation_results_step5.csv",
        screenshot_dir=SCREENSHOT_DIR_STEP5
    )

    # Step 6: Simulate interaction (clicks & inputs) and log output
    step6_ai_integration(
        test_urls=test_urls,
        headless=False,
        log_dir=LOG_DIR_STEP5,
        json_dir=JSON_SUBDIR_STEP5,
        screenshot_dir=INTERACTION_SHOT_DIR_STEP5,
    )

   
    print("Step 5 complete.")

