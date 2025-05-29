# File: grid_parser_project/step3_computer_vision.py
# Purpose: Step 3 - Computer Vision Integration (OpenCV preprocessing, OCR, YOLO conversion)

import os, json
import cv2
import pandas as pd
import numpy as np
import pytesseract
from urllib.parse import urlparse
from ultralytics import YOLO
# Ensure you have the correct paths in your config file
from config import (
    JSON_SUBDIR_STEP1, PROCESSED_IMG_DIR, YOLO_ANN_DIR,
    SCREENSHOT_DIR_STEP1, SCREENSHOT_DIR_STEP7,
    YOLO_PRETRAINED_WEIGHTS, YOLO_DATA_PATH,
    YOLO_TRAIN_NAME, YOLO_TRAIN_PROJECT
)

# function to preprocess images using OpenCV    
def preprocess_image_cv(input_path, output_path):
    img = cv2.imread(input_path)
    if img is None:
        print(f"Could not load: {input_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_path = os.path.join(PROCESSED_IMG_DIR, "gray_" + os.path.basename(input_path))
    cv2.imwrite(gray_path, gray)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    blur_path = os.path.join(PROCESSED_IMG_DIR, "blur_" + os.path.basename(input_path))
    cv2.imwrite(blur_path, blur)

    thresh = cv2.adaptiveThreshold(blur, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    thresh_path = os.path.join(PROCESSED_IMG_DIR, "thresh_" + os.path.basename(input_path))
    cv2.imwrite(thresh_path, thresh)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imwrite(output_path, img)
    print(f"Final processed image saved: {output_path}")

# function to convert JSON annotations to YOLO format
def convert_json_to_yolo(json_file, output_dir, image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image for YOLO size: {image_path}")
        return
    img_h, img_w = img.shape[:2]

    with open(json_file, "r") as f:
        data = json.load(f)

    comps = data.get("UI Components", [])
    if not comps:
        return

    shot_name = os.path.basename(data["Screenshot"])
    txt_name = shot_name.replace(".png", ".txt")
    out_txt = os.path.join(output_dir, txt_name)

    label_map = {"button": 0, "input": 1, "a": 2, "img": 3}

    with open(out_txt, "w") as tf:
        for c in comps:
            tag_l = c["Tag"].lower()
            lid = label_map.get(tag_l, 4)
            x, y = c["X"], c["Y"]
            w, h = c["Width"], c["Height"]

            x_c = (x + w / 2) / img_w
            y_c = (y + h / 2) / img_h
            norm_w = w / img_w
            norm_h = h / img_h

            tf.write(f"{lid} {x_c} {y_c} {norm_w} {norm_h}\n")

    print(f"YOLO annotation saved: {out_txt}")

def extract_ocr_data(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return pd.DataFrame()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_data(gray, output_type=pytesseract.Output.DATAFRAME).dropna(subset=["text"])

def draw_ocr_matches(image_path, components, output_path):
    img = cv2.imread(image_path)
    for comp in components:
        if comp.get("OCR_Text"):
            x, y = comp["X"], comp["Y"]
            w, h = comp["Width"], comp["Height"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(img, comp["OCR_Text"][:15], (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.imwrite(output_path, img)
    print(f"OCR overlay saved to: {output_path}")

# Main function to process Step 3 
def process_step3(json_dir=JSON_SUBDIR_STEP1, screenshot_dir=SCREENSHOT_DIR_STEP1):
    jfiles = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    if not jfiles:
        print("No JSON for Step 3.")
        return

    for jf in jfiles:
        fp = os.path.join(json_dir, jf)
        with open(fp, "r") as f:
            data = json.load(f)

        base_shot = os.path.basename(data.get("Screenshot", ""))
        correct_shot_path = os.path.join(screenshot_dir, base_shot)
        if not os.path.isfile(correct_shot_path):
            print(f"Missing screenshot: {correct_shot_path}")
            continue

        out_processed = os.path.join(PROCESSED_IMG_DIR, f"processed_{base_shot}")
        preprocess_image_cv(correct_shot_path, out_processed)

        convert_json_to_yolo(fp, YOLO_ANN_DIR, correct_shot_path)

        ocr_df = extract_ocr_data(correct_shot_path)
        components = data.get("UI Components", [])
        PADDING = 5

        label_map = {"button": 0, "input": 1, "a": 2, "img": 3}

        for comp in components:
            tag_l = comp["Tag"].lower()
            comp["YOLO_Class"] = label_map.get(tag_l, 4)

            if comp["Width"] > 1000 and comp["Height"] > 800:
                comp["Component_Type"] = "Container"
            else:
                comp["Component_Type"] = "Element"

            x1, y1 = comp["X"] - PADDING, comp["Y"] - PADDING
            x2 = comp["X"] + comp["Width"] + PADDING
            y2 = comp["Y"] + comp["Height"] + PADDING

            matched_texts = ocr_df[
                (ocr_df["left"] >= x1) & (ocr_df["left"] + ocr_df["width"] <= x2) &
                (ocr_df["top"] >= y1) & (ocr_df["top"] + ocr_df["height"] <= y2)
            ]["text"].tolist()

            comp["OCR_Text"] = " ".join(matched_texts).strip() if matched_texts else ""

        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        ocr_overlay_path = os.path.join(PROCESSED_IMG_DIR, f"ocr_overlay_{base_shot}")
        draw_ocr_matches(correct_shot_path, components, ocr_overlay_path)

    print("Step 3: Computer Vision Techniques (with OCR-to-component mapping) - COMPLETED!")

def train_yolo_model():
    if not os.path.isfile(YOLO_DATA_PATH):
        print(f"YOLO dataset config not found: {YOLO_DATA_PATH}")
        return

    print("Starting YOLO training...")
    model = YOLO(YOLO_PRETRAINED_WEIGHTS)

    results = model.train(
        data=YOLO_DATA_PATH,
        epochs=50,
        imgsz=640,
        batch=16,
        name=YOLO_TRAIN_NAME,
        project=YOLO_TRAIN_PROJECT
    )

    val_m = model.val()
    print("YOLO training completed. Validation metrics:", val_m)
