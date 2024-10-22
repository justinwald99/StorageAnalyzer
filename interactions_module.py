# interactions_module.py
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


def ebay_interaction(driver: WebDriver):
    try:
        # Find the search box and perform a search for "laptop"
        search_box = driver.find_element(value="gh-ac")
        search_box.send_keys("laptop")
        search_button = driver.find_element(value="gh-btn")
        search_button.click()
        time.sleep(1)

        # Locate the first laptop item using CSS selector
        first_laptop = driver.find_element(By.CSS_SELECTOR, "#srp-river-results ul.srp-results > li.s-item")
        first_laptop.find_element(By.CLASS_NAME, "s-item__link").click()
        driver.switch_to.window(driver.window_handles[1])

        print("Performed custom interaction on eBay: searched for 'laptop'.")
    except Exception as e:
        print(f"Error interacting with eBay: {str(e)}")
