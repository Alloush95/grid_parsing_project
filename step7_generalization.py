# File: grid_parser_project/step7_generalization.py
# Purpose: Step 7 - Test framework generalization on non-e-commerce sites (e.g., blogs, media-heavy UIs)

# Reuse existing pipeline modules
from step1_data_collection import capture_ui_screenshots
from step2_grid_parsing import process_ui_data_step2
from step3_computer_vision import process_step3
from step4_metrics_evaluation import step4_evaluation
from step6_ai_integration import step6_ai_integration

# Import correct directories for Step 7
from config import (
    SCREENSHOT_DIR_STEP7, JSON_SUBDIR_STEP7,
    LOG_DIR_STEP7, INTERACTION_SHOT_DIR_STEP7
)

def step7_generalization_and_adaptability(test_urls, headless=True):
    """
    Executes the full parsing pipeline on general or media-focused websites
    (e.g., news, blogs) to test layout adaptability and framework robustness.

    Args:
        test_urls (list): Media-heavy or blog-style URLs to process.
        headless (bool): Whether to run browser in headless mode.
    """
    print("\n=== STEP 7: Generalization & Adaptability ===")

    # Step 1 (repurposed): Capture screenshots + UI JSONs
    capture_ui_screenshots(test_urls, headless=False, screenshot_dir=SCREENSHOT_DIR_STEP7)

    # Step 2: Grid-based parsing with overlays and metrics
    process_ui_data_step2(json_dir=JSON_SUBDIR_STEP7, screenshot_dir=SCREENSHOT_DIR_STEP7)

    # Step 3: Preprocessing, OCR, and YOLO annotation
    process_step3(json_dir=JSON_SUBDIR_STEP7, screenshot_dir=SCREENSHOT_DIR_STEP7)

    # Step 4: Evaluate layout metrics from parsed JSONs
    step4_evaluation(json_dir=JSON_SUBDIR_STEP7, csv_filename="evaluation_results_step7.csv")

    # Step 6: Interaction simulation (clicks/inputs) — uses JSONs from Step 7
    step6_ai_integration(
        test_urls,
        headless=False,
        fallback_to_coordinates=True,
        json_dir=JSON_SUBDIR_STEP7,
        log_dir=LOG_DIR_STEP7,
        screenshot_dir=INTERACTION_SHOT_DIR_STEP7
    )

    # Wrap-up
    print("""
Review 'evaluation_results_step7.csv' for these new sites.
Compare metrics with e-commerce sites to assess adaptability.
""")
    print("Step 7 complete.")
