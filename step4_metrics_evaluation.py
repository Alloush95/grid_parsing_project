# File: grid_parser_project/step4_metrics_evaluation.py
# Purpose: Step 4 - Evaluate layout parsing using multi-resolution grid metrics

import os, json, math, cv2
import pandas as pd
from urllib.parse import urlparse
from config import (
    JSON_SUBDIR_STEP1,
    UI_DATA_DIR,
    SCREENSHOT_DIR_STEP1,
    SCREENSHOT_DIR_STEP5,
    SCREENSHOT_DIR_STEP7
)

# --- Entropy (Shannon) Calculation ---
def compute_entropy(ui_components):
    if not ui_components:
        return 0.0
    tag_freq = {}
    for comp in ui_components:
        tag = comp["Tag"].lower()
        tag_freq[tag] = tag_freq.get(tag, 0) + 1
    total = sum(tag_freq.values())
    entropy = -sum((freq / total) * math.log2(freq / total) for freq in tag_freq.values())
    return entropy

# --- File-based Compression Ratio (CR_file) ---
def compute_compression_ratios(png_path):
    jpg_path = png_path.replace(".png", ".jpg")
    try:
        img = cv2.imread(png_path)
        if img is None:
            return None, None, None
        cv2.imwrite(jpg_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        png_size = os.path.getsize(png_path)
        jpg_size = os.path.getsize(jpg_path)
        cr_file = 1 - (jpg_size / png_size) if png_size else 0
        os.remove(jpg_path)
        return cr_file, png_size, jpg_size
    except:
        return None, None, None

# --- Main Metrics Computation Per Grid Size ---
def calculate_layout_metrics(data, rows=8, cols=8, screenshot_dir=SCREENSHOT_DIR_STEP1):
    comps = data.get("UI Components", [])
    if not comps:
        return {
            "grid_consistency": 0,
            "hit_rate": 0,
            "density": 0,
            "variability": 0,
            "tag_variety": 0,
            "compression_ratio": 0,
            "entropy": 0,
            "cr_file": None,
            "png_size": None,
            "jpg_size": None,
            "P_Score": 0
        }

    total = len(comps)
    scr_w, scr_h = 1920, 1080
    cell_w = scr_w // cols
    cell_h = scr_h // rows

    exact_hits, fuzzy_hits = 0, 0

    for c in comps:
        assigned_r = c.get("Grid_Row", 0)
        assigned_c = c.get("Grid_Col", 0)
        real_r = c["Y"] // cell_h
        real_c = c["X"] // cell_w
        if assigned_r == real_r and assigned_c == real_c:
            exact_hits += 1
        if abs(assigned_r - real_r) <= 1 and abs(assigned_c - real_c) <= 1:
            fuzzy_hits += 1

    grid_consistency = exact_hits / total
    hit_rate = fuzzy_hits / total
    screen_area = scr_w * scr_h
    density = total / screen_area if screen_area else 0
    entropy_val = compute_entropy(comps)
    distinct_tags = set(c["Tag"] for c in comps)
    tag_variety = len(distinct_tags) / total if total else 0
    sum_area = sum(c["Width"] * c["Height"] for c in comps)
    comp_ratio = sum_area / screen_area if screen_area else 0

    # Get file compression ratio (CR_file)
    shot_file = os.path.basename(data["Screenshot"])
    correct_shot_path = os.path.join(screenshot_dir, shot_file)
    print(f"Using screenshot: {correct_shot_path}")

    cr_file, png_size, jpg_size = compute_compression_ratios(correct_shot_path)

    # Define the weights
    alpha = 0.3
    beta = 0.2
    gamma = 0.2
    delta = 0.15
    epsilon = 0.15

    # Apply the formula for P_Score
    P_Score = (alpha * hit_rate) + (beta * (1 - density)) + (gamma * entropy_val) + (delta * comp_ratio) + (epsilon * (cr_file if cr_file else 0))

    return {
        "grid_consistency": grid_consistency,
        "hit_rate": hit_rate,
        "density": density,
        "variability": entropy_val,
        "tag_variety": tag_variety,
        "compression_ratio": comp_ratio,
        "entropy": entropy_val,
        "cr_file": cr_file,
        "png_size": png_size,
        "jpg_size": jpg_size,
        "P_Score": P_Score
    }

# --- Main Step 4 Pipeline ---
def step4_evaluation(json_dir=JSON_SUBDIR_STEP1, csv_filename="evaluation_results_step1.csv", screenshot_dir=None):
    """
    Step 4: Evaluates all JSON entries using multiple grid resolutions.
    Computes all layout metrics and saves results to CSV for analysis.

    Args:
        json_dir (str): Path to the directory containing JSON files.
        csv_filename (str): Name of the output CSV file to save.
        screenshot_dir (str or None): Path to screenshot directory. If None, inferred from json_dir.
    """
    jfiles = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    if not jfiles:
        print("No JSON for Step 4.")
        return

    # 🔍 Auto-select screenshot directory if not explicitly passed
    if screenshot_dir is None:
        if "step7" in json_dir.lower() or "step7" in csv_filename.lower():
            screenshot_dir = SCREENSHOT_DIR_STEP7
        elif "step5" in json_dir.lower() or "step5" in csv_filename.lower():
            screenshot_dir = SCREENSHOT_DIR_STEP5
        else:
            screenshot_dir = SCREENSHOT_DIR_STEP1

    results = []
    grid_sizes = [4, 8, 16]

    for jf in jfiles:
        fp = os.path.join(json_dir, jf)
        with open(fp, "r") as f:
            data = json.load(f)

        dom = urlparse(data["URL"]).netloc.replace("www.", "").replace(".", "_")

        for grid in grid_sizes:
            mets = calculate_layout_metrics(data, rows=grid, cols=grid, screenshot_dir=screenshot_dir)

            row = {
                "JSON_File": jf,
                "Domain": dom,
                "Grid_Size": f"{grid}x{grid}",
                "Grid_Consistency(%)": f"{mets['grid_consistency']*100}",
                "Hit_Rate(%)": f"{mets['hit_rate']*100}",
                "Density": f"{mets['density']}",
                "Variability": f"{mets['variability']}",
                "Compression_Ratio": f"{mets['compression_ratio']}",
                "Entropy": f"{mets['entropy']}",
                "CR_File": f"{mets['cr_file']}" if mets['cr_file'] is not None else "N/A",
                "Screenshot_Size(Bytes)": mets["png_size"],
                "Compressed_JPG_Size(Bytes)": mets["jpg_size"],
                "P_Score": f"{mets['P_Score']}"
            }

            results.append(row)

    df = pd.DataFrame(results)
    out_csv = os.path.join(UI_DATA_DIR, csv_filename)
    df.to_csv(out_csv, index=False)
    print(f"Step 4 results saved to {out_csv}")
