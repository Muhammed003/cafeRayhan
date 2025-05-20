import locale
import re
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Import Options


def login_and_fetch_data(username, password):
    driver_path = "/usr/local/bin/chromedriver"  # Zamenite na put do vašeg WebDriver-a
    service = Service(driver_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://lk.salyk.kg/login")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "login"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        login_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-1ff36h2")))
        driver.get("https://lk.salyk.kg/analytics/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "css-1b9m9t1")))

        revenue_element = driver.find_element(By.XPATH,
                                              "//div[@class='css-1b9m9t1 eojddgo2']//span[contains(text(), 'Выручка')]/following-sibling::span")
        return  revenue_element.text

    except Exception as e:
        print(f"Error: {e}")
        return f"Ошибка: {e}"

    finally:
        driver.quit()
