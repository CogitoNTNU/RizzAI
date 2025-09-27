import json
import os
import re

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


load_dotenv(dotenv_path="DataCollection/.env")


PROFILE_FOLDER = os.getenv(
    "PROFILE_FOLDER", "your-profile-folder"
)  # Replace with your Firefox profile folder name
WIN_USERNAME = os.getenv("WIN_USERNAME")


options = Options()

# Verify the profile folder path
profile_path = f"C:\\Users\\{WIN_USERNAME}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{PROFILE_FOLDER}"
if not os.path.exists(profile_path):
    raise Exception(
        f"Specified profile folder '{profile_path}' does not exist. Please check the PROFILE_FOLDER and WIN_USERNAME environment variables."
    )

options.add_argument("-profile")
options.add_argument(profile_path)
driver = webdriver.Firefox(service=Service(), options=options)

driver.maximize_window()

# Set constants
timeout = 40
URL = "https://tinder.com/app/recs"


# Navigate to Tinder
print("Navigating to Tinder...")
driver.get(URL)

# Wait for user to log in manually (or automate login if possible)
print("Please log in to Tinder manually. You have 60 seconds.")
input("Press Enter after logging in...")


# Scrape images and "About Me" text
def scrape_tinder():
    data = []

    # Find all elements with background images
    image_elements = driver.find_elements(
        By.XPATH, "//*[contains(@style, 'background-image')]"
    )
    for element in image_elements:
        style = element.get_attribute("style")
        if style:  # Ensure style is not None
            match = re.search(r'url\\(\\?"(.*?)\\?"\\)', style)
            if match:
                image_url = match.group(1)
                data.append({"image_url": image_url})

    # Find "About Me" section
    try:
        about_me_element = driver.find_element(
            By.XPATH, "//*[contains(text(), 'About Me')]/following-sibling::*"
        )
        about_me_text = about_me_element.text
        data.append({"about_me": about_me_text})
    except Exception as e:
        print("Could not find 'About Me' section:", e)

    # Save data to JSON
    with open("tinder_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("Data saved to tinder_data.json")


# Run the scraper
scrape_tinder()

# Always quit the driver
driver.quit()
