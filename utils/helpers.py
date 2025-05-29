import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def dismiss_cookies(driver):
    time.sleep(5)  # Let page settle
    
    # Handle iframes first
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for iframe in iframes:
        try:
            driver.switch_to.frame(iframe)
            # _dismiss_cookie_buttons(driver)
            driver.switch_to.default_content()
        except:
            driver.switch_to.default_content()
            continue

    # Dismiss visible buttons
    _dismiss_cookie_buttons(driver)

    # Handle specific cases (e.g., BBC, Amazon, Guardian)
    _dismiss_modals(driver)

#     # Try to remove lingering banners via JavaScript
    driver.execute_script("""
        document.querySelectorAll('[id*=cookie], [class*=cookie], [role=dialog], [aria-label*="cookie"], [id*=consent], [class*=consent]')
        .forEach(el => el.remove());
    """)
    print("[JS] Cleaned up residual cookie banners.")

def _dismiss_cookie_buttons(driver):
    # Common multilingual buttons
    button_texts = [
        "Accept", "Accept All", "I agree", "OK", "Got it", "Allow all",
        "Decline", "Reject", "Reject All", "Deny", "Avvisa", "Stäng",
        "Alle ablehnen", "Alle akzeptieren", "Tout refuser", "Tout accepter"
    ]
    
#     # Build XPath variations
    xpaths = [f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{txt.lower()}')]" for txt in button_texts]
    xpaths += [
        "//div[contains(@id, 'cookie')]//button",
        "//div[contains(@class, 'cookie')]//button"
    ]
    
    for xp in xpaths:
        elems = driver.find_elements(By.XPATH, xp)
        for btn in elems:
            try:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"Clicked cookie button: {btn.text.strip()}")
                    time.sleep(1)  # Let modal disappear
                    return
            except:
                continue

def _dismiss_modals(driver):
    modal_xpaths = [
        "//button[contains(text(), 'Continue')]",
        "//button[contains(text(), 'Got it')]",
        "//button[contains(text(), 'Agree')]",
        "//button[contains(text(), 'OK')]",
        "//div[contains(@class, 'modal')]//button",
        "//button[contains(text(), 'I do not agree')]",
        "//button[contains(text(), 'No, thank you')]",
        "//button[contains(text(), 'No')]",
        "//button[contains(text(), 'Dismiss')]",
        "//button[contains(text(), 'Close')]",
        "//button[contains(text(), 'Cancel')]",
        "//button[contains(text(), 'X')]",
        "//button[contains(text(), 'Exit')]",
        "//button[contains(text(), 'Skip')]",
        "//button[contains(text(), 'Later')]",
        "//button[contains(text(), 'Not now')]",
        "//button[contains(text(), 'Maybe later')]",
        "//button[contains(text(), 'Not interested')]",
        "//button[contains(text(), 'No thanks')]",
        "//button[contains(text(), 'No, thanks')]",
        "//button[contains(text(), 'Acceptera')]",  # Spanish
        "//button[contains(text(), 'Acceptera Alla')]",  # Swedish
        "//button[contains(text(), 'Acceptera alla cookies')]",  # Swedish
        "//button[contains(text(), 'Tillåt alla cookies')]",  # Swedish
        "//button[contains(text(), 'STÄNG & ACCEPTERA')]",  # Swedish
        "//button[contains(text(), 'Stäng & avvisa')]",  # Swedish
        "//button[contains(text(), 'Stäng & neka')]",  # Swedish
        "//button[contains(text(), 'Stäng & avvisa alla')]",  # Swedish
        "//button[contains(text(), 'Stäng & neka alla')]",  # Swedish
        "//button[contains(text(), 'Stäng & avvisa alla cookies')]",  # Swedish
        "//button[contains(text(), 'Neka')]",  # Swedish
        "//button[contains(text(), 'Stäng & avvisa alla cookies')]",  # Swedish
        "//button[contains(text(), 'Stäng & godkänn')]",  # Swedish
        "//button[contains(text(), 'Godkänn alla')]",  # Swedish
        "//button[contains(text(), 'Stäng & acceptera alla')]",  # Swedish
        "//button[contains(text(), 'Stäng & tillåt alla')]",  # Swedish
        "//button[contains(text(), 'Stäng & tillåt alla cookies')]",  # Swedish
        "//button[contains(text(), 'Si, amo las ofertas ')]",  # Spanish
        "//button[contains(text(), 'Sí, me gusta')]",  # Spanish
        "//button[contains(text(), 'Sí, me gusta recibir ofertas')]",  # Spanish
        "//button[contains(text(), 'Sí, me gusta recibir ofertas y promociones')]",  # Spanish
        "//button[contains(text(), 'Sí, me gusta recibir ofertas y promociones de')]",  # Spanish
        
    
    ]

    # Step 1: Try explicit waits for any matching modal button
    for xp in modal_xpaths:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            elems = driver.find_elements(By.XPATH, xp)
            for btn in elems:
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    print(f"Modal dismissed with: {btn.text.strip()}")
                    time.sleep(1)
                    return
        except:
            continue

    # Step 2: Fallback: try to remove the modal using JS
    driver.execute_script("""
        document.querySelectorAll(
            'div[role=dialog], div[class*=modal], div[class*=popup], div[class*=overlay], div[class*=notice], div[aria-modal=true]'
        ).forEach(el => el.remove());
    """)
    print("[JS] Removed modal overlays.")
  



def categorize_ui_type(url):
    low = url.lower()
    if "amazon" in low or "ebay" in low:
        return "Marketplace"
    elif "bestbuy" in low or "newegg" in low:
        return "Electronics"
    elif "zara" in low or "hm" in low:
        return "Fashion"
    elif "tesco" in low or "carrefour" in low:
        return "Supermarket"
    elif "apple" in low or "samsung" in low:
        return "Tech Store"
    else:
        return "General E-Commerce"
    