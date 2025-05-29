import undetected_chromedriver as uc

def setup_selenium_driver(headless=True):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # ✅ Pin the version to match your installed Chrome (135)
    driver = uc.Chrome(version_main=135, options=options)
    return driver
