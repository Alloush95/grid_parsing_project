# File: grid_parser_project/step2_grid_parsing.py
# Purpose: Step 2 - Grid-Based Parsing & Metric Evaluation (multi-resolution + compression)

import os, json, math, cv2
import pandas as pd
from urllib.parse import urlparse
from config import (
    JSON_SUBDIR_STEP1,
    GRID_OUTPUT_DIR_STEP1, GRID_OUTPUT_DIR_STEP5, GRID_OUTPUT_DIR_STEP7,
    SCREENSHOT_DIR_STEP1, SCREENSHOT_DIR_STEP5, SCREENSHOT_DIR_STEP7,
    UI_DATA_DIR
)

# ----------------------
# Utility: Detect which step we're processing based on file path
# ----------------------
def detect_step(input_path: str) -> str:
    path = input_path.lower()
    if "step7" in path:
        return "step7"
    elif "step5" in path:
        return "step5"
    elif "step6" in path:
        return "step6"
    return "step1"

# ----------------------
# Map UI elements to grid cells
# ----------------------
def map_ui_to_grid(ui_components, rows=8, cols=8, screen_w=1920, screen_h=1080):
    cell_w = screen_w // cols
    cell_h = screen_h // rows
    for comp in ui_components:
        comp["Grid_Row"] = comp["Y"] // cell_h
        comp["Grid_Col"] = comp["X"] // cell_w
    return ui_components

def validate_grid_assignments(ui_components, rows=8, cols=8, screen_w=1920, screen_h=1080):
    if not ui_components:
        return 0.0
    correct = 0
    cell_w = screen_w // cols
    cell_h = screen_h // rows
    for comp in ui_components:
        assigned_r = comp.get("Grid_Row", -1)
        assigned_c = comp.get("Grid_Col", -1)
        real_r = comp["Y"] // cell_h
        real_c = comp["X"] // cell_w
        if assigned_r == real_r and assigned_c == real_c:
            correct += 1
    return correct / len(ui_components)

# ----------------------
# Overlay grid on screenshot
# ----------------------
def overlay_grid_on_screenshot(input_path, output_path, screenshot_dir, rows=8, cols=8):
    filename_only = os.path.basename(input_path)
    correct_input_path = os.path.join(screenshot_dir, filename_only)

    img = cv2.imread(correct_input_path)
    if img is None:
        print(f"Could not load for overlay: {correct_input_path}")
        return
    h, w, _ = img.shape
    cell_w = w // cols
    cell_h = h // rows

    for i in range(1, cols):
        x = i * cell_w
        cv2.line(img, (x, 0), (x, h), (0, 255, 0), 2)
    for j in range(1, rows):
        y = j * cell_h
        cv2.line(img, (0, y), (w, y), (0, 255, 0), 2)

    cv2.imwrite(output_path, img)
    print(f"Grid overlay: {output_path}")


# ----------------------
# Additional evaluation metrics
# ----------------------
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

# ----------------------
# Evaluate grid parsing variants
# ----------------------
def evaluate_grid_variants(grid_sizes=[4, 8, 16], screen_w=1920, screen_h=1080, json_dir=JSON_SUBDIR_STEP1, screenshot_dir=SCREENSHOT_DIR_STEP1):
    results = []
    jfiles = [f for f in os.listdir(json_dir) if f.endswith(".json")]

    for jf in jfiles:
        with open(os.path.join(json_dir, jf), "r", encoding="utf-8") as f:
            data = json.load(f)

        comps = data["UI Components"]
        screenshot_filename = os.path.basename(data["Screenshot"])
        shot_path = os.path.join(screenshot_dir, screenshot_filename)

        domain = urlparse(data["URL"]).netloc.replace("www.", "").replace(".", "_")

        for size in grid_sizes:
            comps_grid = map_ui_to_grid(comps.copy(), size, size, screen_w, screen_h)
            accuracy = validate_grid_assignments(comps_grid, size, size, screen_w, screen_h)
            density = len(comps_grid) / (screen_w * screen_h)
            entropy = compute_entropy(comps_grid)
            cr_bbox = sum(c["Width"] * c["Height"] for c in comps_grid) / (screen_w * screen_h)
            cr_file, png_size, jpg_size = compute_compression_ratios(shot_path)

            results.append({
                "Domain": domain,
                "Grid_Size": f"{size}x{size}",
                "Num_Components": len(comps_grid),
                "Hit_Rate": round(accuracy * 100, 2),
                "Density": round(density, 6),
                "Entropy": round(entropy, 4),
                "CR_BBox": round(cr_bbox, 4),
                "CR_File": round(cr_file, 4) if cr_file is not None else "N/A",
                "Screenshot_Size(Bytes)": png_size,
                "Compressed_JPG_Size(Bytes)": jpg_size
            })

    df = pd.DataFrame(results)
    out_csv = os.path.join(UI_DATA_DIR, "grid_parsing_metrics.csv")
    df.to_csv(out_csv, index=False)
    print(f"Grid parsing metrics saved to: {out_csv}")


# ----------------------
# Main step runner
# ----------------------
def process_ui_data_step2(json_dir=JSON_SUBDIR_STEP1, screenshot_dir=SCREENSHOT_DIR_STEP1):
    jfiles = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    if not jfiles:
        print("No JSON for Step 2.")
        return

    for jf in jfiles:
        fp = os.path.join(json_dir, jf)
        print(f"Now trying to load: {jf}")
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["UI Components"] = map_ui_to_grid(data["UI Components"], rows=8, cols=8)
        frac = validate_grid_assignments(data["UI Components"], rows=8, cols=8)
        print(f"Grid Consistency for {jf}: {frac*100:.2f}%")

        with open(fp, "w", encoding="utf-8") as outf:
            json.dump(data, outf, indent=4)

        csv_path = fp.replace(".json", "_grid.csv")
        pd.DataFrame(data["UI Components"]).to_csv(csv_path, index=False)

        domain = urlparse(data["URL"]).netloc.replace("www.", "").replace(".", "_")

        # Fix screenshot path & step name
        screenshot_filename = os.path.basename(data["Screenshot"])
        input_path = os.path.join(screenshot_dir, screenshot_filename)
        step_prefix = os.path.basename(screenshot_dir).lower()  # e.g., "step7"

        grid_dir_map = {
            "step1": GRID_OUTPUT_DIR_STEP1,
            "step5": GRID_OUTPUT_DIR_STEP5,
            "step7": GRID_OUTPUT_DIR_STEP7
        }
        grid_dir = grid_dir_map.get(step_prefix, GRID_OUTPUT_DIR_STEP1)
        grid_out = os.path.join(grid_dir, f"{step_prefix}_{domain}_grid.png")

        overlay_grid_on_screenshot(input_path, grid_out, screenshot_dir)

    evaluate_grid_variants(grid_sizes=[4, 8, 16], json_dir=json_dir, screenshot_dir=screenshot_dir)
    print("Step 2: Grid-Based Parsing - COMPLETED!")
