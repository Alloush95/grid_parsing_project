import os
import pytesseract

# --------------------
# ROOT PROJECT DIRECTORY
# --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # path to grid_parser_project/
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR))  # adjust if needed

# --------------------
# URL GROUPS
# --------------------
E_COMMERCE_WEBSITES = ["https://www.amazon.se", "https://www.walmart.com"]

TEST_URLS_STEP5 = [ "https://www.abebooks.co.uk","https://www.accessorize.com",

                    ]

BLOG_MEDIA_URLS = [ "https://www.usatoday.com", "https://www.theatlantic.com"]
    
# --------------------
# DIRECTORIES (nested inside the project folder)
# --------------------
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots")  # legacy / default path

# ✅ Separate screenshot folders per step
SCREENSHOT_DIR_STEP1 = os.path.join(SCREENSHOT_DIR, "step1")
SCREENSHOT_DIR_STEP5 = os.path.join(SCREENSHOT_DIR, "step5")
SCREENSHOT_DIR_STEP7 = os.path.join(SCREENSHOT_DIR, "step7")

UI_DATA_DIR = os.path.join(PROJECT_ROOT, "ui_data")
GRID_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "screenshots_with_grid")

# ✅ Step-specific grid overlay folders
GRID_OUTPUT_DIR_STEP1 = os.path.join(GRID_OUTPUT_DIR, "step1")
GRID_OUTPUT_DIR_STEP5 = os.path.join(GRID_OUTPUT_DIR, "step5")
GRID_OUTPUT_DIR_STEP7 = os.path.join(GRID_OUTPUT_DIR, "step7")

PROCESSED_IMG_DIR = os.path.join(PROJECT_ROOT, "processed_screenshots")
YOLO_ANN_DIR = os.path.join(PROJECT_ROOT, "yolo_annotations")

# ✅ Final: only step-specific JSON and CSV directories
JSON_SUBDIR_STEP1 = os.path.join(UI_DATA_DIR, "json_data", "step1")
JSON_SUBDIR_STEP5 = os.path.join(UI_DATA_DIR, "json_data", "step5")
JSON_SUBDIR_STEP7 = os.path.join(UI_DATA_DIR, "json_data", "step7")


CSV_SUBDIR_STEP1 = os.path.join(UI_DATA_DIR, "csv_data", "step1")
CSV_SUBDIR_STEP5 = os.path.join(UI_DATA_DIR, "csv_data", "step5")
BEST_GRID_JSON_DIR_STEP5 = os.path.join(UI_DATA_DIR, "json_data", "step5_best_grid")

CSV_SUBDIR_STEP7 = os.path.join(UI_DATA_DIR, "csv_data", "step7")


# ✅ Logs and interaction screenshots (shared + step-specific)
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_DIR_STEP1 = os.path.join(LOG_DIR, "step1")
LOG_DIR_STEP5 = os.path.join(LOG_DIR, "step5")
LOG_DIR_STEP6 = os.path.join(LOG_DIR, "step6")  # ✅ Added for Step 6
LOG_DIR_STEP7 = os.path.join(LOG_DIR, "step7")


# ✅ Interaction screenshots (shared + step-specific)
INTERACTION_SHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots_with_interaction")
INTERACTION_SHOT_DIR_STEP1 = os.path.join(INTERACTION_SHOT_DIR, "step1")
INTERACTION_SHOT_DIR_STEP5 = os.path.join(INTERACTION_SHOT_DIR, "step5")
INTERACTION_SHOT_DIR_STEP6 = os.path.join(INTERACTION_SHOT_DIR, "step6")
INTERACTION_SHOT_DIR_STEP7 = os.path.join(INTERACTION_SHOT_DIR, "step7")

PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")

# --------------------
# YOLO CONFIG
# --------------------
YOLO_PRETRAINED_WEIGHTS = "yolov8s.pt"
YOLO_DATA_PATH = "ui_dataset.yaml"
YOLO_TRAIN_PROJECT = "yolo_training"
YOLO_TRAIN_NAME = "ui_element_detection"

# --------------------
# TESSERACT CONFIG
# --------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# --------------------
# ENSURE ALL DIRECTORIES EXIST
# --------------------
for directory in [
    SCREENSHOT_DIR, SCREENSHOT_DIR_STEP1, SCREENSHOT_DIR_STEP7, SCREENSHOT_DIR_STEP5,
    UI_DATA_DIR,
    JSON_SUBDIR_STEP1, JSON_SUBDIR_STEP7, JSON_SUBDIR_STEP5,
    CSV_SUBDIR_STEP1, CSV_SUBDIR_STEP7, CSV_SUBDIR_STEP5,
    GRID_OUTPUT_DIR, GRID_OUTPUT_DIR_STEP1, GRID_OUTPUT_DIR_STEP7, GRID_OUTPUT_DIR_STEP5,
    PROCESSED_IMG_DIR, YOLO_ANN_DIR,
    LOG_DIR, LOG_DIR_STEP1, LOG_DIR_STEP6, LOG_DIR_STEP7, LOG_DIR_STEP5,
    INTERACTION_SHOT_DIR, INTERACTION_SHOT_DIR_STEP1, INTERACTION_SHOT_DIR_STEP6, INTERACTION_SHOT_DIR_STEP7,
    PLOTS_DIR
]:
    os.makedirs(directory, exist_ok=True)
