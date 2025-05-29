import os, time, json
from datetime import datetime
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from utils.driver_setup import setup_selenium_driver
from utils.helpers import dismiss_cookies
from config import (
    JSON_SUBDIR_STEP1, LOG_DIR_STEP6, LOG_DIR_STEP7,
    INTERACTION_SHOT_DIR_STEP6, INTERACTION_SHOT_DIR_STEP7
)
import pandas as pd

def log_interaction(comp, interaction_type, method, coords, success, error=None):
    return {
        "interaction_type": interaction_type,
        "target_text": comp.get("Text", ""),
        "ocr_text": comp.get("OCR_Text", ""),
        "method": method,
        "coordinates": coords,
        "class": comp.get("Class", ""),
        "role": comp.get("Role", ""),
        "tag": comp.get("Tag", ""),
        "width": comp.get("Width", 0),
        "height": comp.get("Height", 0),
        "success": success,
        "error": error,
        "timestamp": datetime.utcnow().isoformat()
    }

def step6_ai_integration(
    test_urls,
    headless=True,
    fallback_to_coordinates=True,
    json_dir=JSON_SUBDIR_STEP1,
    log_dir=None,
    screenshot_dir=None
):
    print("\n=== STEP 6: AI Integration (Smart Clicking + Logging + Screenshots) ===")

    if log_dir is None:
        log_dir = LOG_DIR_STEP6 if json_dir == JSON_SUBDIR_STEP1 else LOG_DIR_STEP7
    if screenshot_dir is None:
        screenshot_dir = INTERACTION_SHOT_DIR_STEP6 if json_dir == JSON_SUBDIR_STEP1 else INTERACTION_SHOT_DIR_STEP7

    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)

    driver = setup_selenium_driver(headless=headless)
    driver.set_window_size(1920, 1080)

    for url in test_urls:
        print(f"\n[AI TEST] Visiting {url}")
        driver.get(url)
        time.sleep(3)
        dismiss_cookies(driver)
        time.sleep(1)

        domain_name = urlparse(url).netloc.replace("www.", "").replace(".", "_")
        json_path = os.path.join(json_dir, f"{domain_name}.json")
        interaction_log = []

        if not os.path.isfile(json_path):
            print(f"No JSON for {domain_name}. Skipping.")
            continue

        with open(json_path, "r") as jf:
            data = json.load(jf)
        ui_comps = data.get("UI Components", [])

        seen_coords = set()

        button_like = []
        for comp in ui_comps:
            class_attr = comp.get("Class", "").lower()
            role_attr = comp.get("Role", "").lower()
            if "button" in (class_attr + role_attr) or "btn" in class_attr:
                center = (round(comp["X"] + comp["Width"] / 2), round(comp["Y"] + comp["Height"] / 2))
                if center not in seen_coords:
                    seen_coords.add(center)
                    button_like.append(comp)

        print(f"  Found {len(button_like)} unique button-like elements in JSON for {url}")
        clicked_count = 0
        initial_url = driver.current_url

        for i, comp in enumerate(button_like):
            success = False
            class_attr = comp.get("Class", "").lower()
            text_attr = comp.get("Text", "N/A").lower()
            interaction_type = "click"

            if class_attr:
                class_tokens = class_attr.split()
                if class_tokens:
                    first_class = class_tokens[0]
                    xpath_str = f"//*[@class='{first_class}']"
                    try:
                        found_elems = driver.find_elements(By.XPATH, xpath_str)
                        for elem in found_elems:
                            if elem.is_displayed() and elem.is_enabled():
                                before_html = driver.page_source
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                driver.execute_script("arguments[0].style.outline='3px solid red'", elem)
                                time.sleep(1)
                                elem.click()
                                time.sleep(2)
                                after_html = driver.page_source
                                success = before_html != after_html
                                if success:
                                    screenshot_path = os.path.join(screenshot_dir, f"{domain_name}_after_click_{i}.png")
                                    driver.save_screenshot(screenshot_path)
                                    clicked_count += 1
                                interaction_log.append(
                                    log_interaction(comp, interaction_type, "class",
                                                    [comp["X"] + comp["Width"] / 2, comp["Y"] + comp["Height"] / 2],
                                                    success)
                                )
                                break
                    except Exception as e:
                        interaction_log.append(
                            log_interaction(comp, interaction_type, "class",
                                            [comp["X"] + comp["Width"] / 2, comp["Y"] + comp["Height"] / 2],
                                            False, str(e))
                        )

            if fallback_to_coordinates and not success:
                x_center = comp["X"] + comp["Width"] / 2
                y_center = comp["Y"] + comp["Height"] / 2
                scroll_js = f"window.scrollTo({max(0, x_center-200)}, {max(0, y_center-200)});"
                driver.execute_script(scroll_js)
                highlight_js = f"""
                    var div = document.createElement('div');
                    div.style.position = 'absolute';
                    div.style.left = '{x_center - 50}px';
                    div.style.top = '{y_center - 25}px';
                    div.style.width = '100px';
                    div.style.height = '50px';
                    div.style.border = '3px solid red';
                    div.style.zIndex = '9999';
                    div.style.pointerEvents = 'none';
                    document.body.appendChild(div);
                    setTimeout(() => div.remove(), 1500);
                """
                driver.execute_script(highlight_js)
                time.sleep(1)
                try:
                    before_html = driver.page_source
                    ActionChains(driver).move_by_offset(x_center, y_center).click().perform()
                    ActionChains(driver).move_by_offset(-x_center, -y_center).perform()
                    time.sleep(1)
                    after_html = driver.page_source

                    success = before_html != after_html
                    if success:
                        screenshot_path = os.path.join(screenshot_dir, f"{domain_name}_after_coord_click_{i}.png")
                        driver.save_screenshot(screenshot_path)
                        clicked_count += 1

                    interaction_log.append(
                        log_interaction(comp, interaction_type, "coordinates", [x_center, y_center], success)
                    )

                except Exception as e:
                    interaction_log.append(
                        log_interaction(comp, interaction_type, "coordinates", [x_center, y_center], False, str(e))
                    )

        print(f"  [AI TEST] Clicked {clicked_count}/{len(button_like)} recognized 'button-like' elements.")

        # Deduplicate input fields the same way
        input_fields = []
        seen_input_coords = set()
        for field in ui_comps:
            if field["Tag"].lower() in ["input", "textarea"]:
                center = (round(field["X"] + field["Width"] / 2), round(field["Y"] + field["Height"] / 2))
                if center not in seen_input_coords:
                    seen_input_coords.add(center)
                    input_fields.append(field)

        print(f"  Found {len(input_fields)} unique input fields to simulate.")

        for j, field in enumerate(input_fields):
            try:
                x_center = field["X"] + field["Width"] / 2
                y_center = field["Y"] + field["Height"] / 2
                scroll_js = f"window.scrollTo({max(0, x_center-200)}, {max(0, y_center-200)});"
                driver.execute_script(scroll_js)
                highlight_js = f"""
                    var div = document.createElement('div');
                    div.style.position = 'absolute';
                    div.style.left = '{x_center - 50}px';
                    div.style.top = '{y_center - 15}px';
                    div.style.width = '100px';
                    div.style.height = '30px';
                    div.style.border = '3px solid red';
                    div.style.zIndex = '9999';
                    div.style.pointerEvents = 'none';
                    document.body.appendChild(div);
                    setTimeout(() => div.remove(), 1500);
                """
                driver.execute_script(highlight_js)
                time.sleep(1)
                ActionChains(driver).move_by_offset(x_center, y_center).click().perform()
                ActionChains(driver).move_by_offset(-x_center, -y_center).perform()
                time.sleep(0.5)
                driver.switch_to.active_element.send_keys("test input")

                screenshot_path = os.path.join(screenshot_dir, f"{domain_name}_after_input_{j}.png")
                driver.save_screenshot(screenshot_path)

                interaction_log.append(
                    log_interaction(field, "input", "coordinates", [x_center, y_center], True)
                )
                print(f"Input field filled at (X={x_center:.1f}, Y={y_center:.1f})")

            except Exception as e:
                interaction_log.append(
                    log_interaction(field, "input", "coordinates", [x_center, y_center], False, str(e))
                )

        # Save interaction logs
        with open(os.path.join(log_dir, f"{domain_name}_interactions.json"), "w", encoding="utf-8") as logf:
            json.dump(interaction_log, logf, indent=4, ensure_ascii=False)

        summary_csv = os.path.join(log_dir, f"{domain_name}_summary.csv")
        pd.DataFrame(interaction_log).to_csv(summary_csv, index=False)

    driver.quit()
    print("Step 6 complete.")