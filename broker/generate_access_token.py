# -*- coding: utf-8 -*-
"""
Zerodha KiteConnect
Manual 2FA + Automatic request_token & access_token
(Selenium 4 + Chrome)
"""

from kiteconnect import KiteConnect
from selenium import webdriver     
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse, parse_qs
from utils import ConfigJson, get_logger

import os


BASE_DIR = "/home/raju/MAIN_DIRECTORY/zerodha"
os.chdir(BASE_DIR)

config = ConfigJson("config/config.json")
logger = get_logger("Generate_access_token")

def autologin():
    # --------------------------------
    # 1. Read API credentials
    # --------------------------------
    api_key = config.get("api_key")
    api_secret = config.get("api_secret")

    kite = KiteConnect(api_key=api_key)

    # --------------------------------
    # Chrome setup (Selenium Manager)
    # --------------------------------
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # optional
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 300)  # up to 5 minutes for manual login

    # --------------------------------
    # Open Zerodha login page
    # --------------------------------
    driver.get(kite.login_url())

    logger.info("Please login MANUALLY (User ID + Password + 2FA)")
    logger.info("Complete Google Authenticator / PIN")
    logger.info("Do NOT close the browser")

    # --------------------------------
    # Wait for redirect with request_token
    # --------------------------------
    wait.until(lambda d: "request_token=" in d.current_url)

    # --------------------------------
    # 2. Extract request_token
    # --------------------------------
    parsed = urlparse(driver.current_url)
    request_token = parse_qs(parsed.query)["request_token"][0]

    config.set("request_token", request_token)    

    logger.info("request_token captured")

    driver.quit()

    # --------------------------------
    # 3. Generate access_token
    # --------------------------------
    data = kite.generate_session(request_token, api_secret=api_secret)
    kite.set_access_token(data["access_token"])

    config.set("access_token", data["access_token"])
    config.save()

    logger.info("access_token generated and saved")

    return kite


# Run
if "__main__" == "__main__":
    autologin()
