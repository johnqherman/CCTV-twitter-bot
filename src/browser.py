from selenium import webdriver

import settings as s


def initialize_browser() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(s.BROWSER_TIMEOUT)
    return browser
