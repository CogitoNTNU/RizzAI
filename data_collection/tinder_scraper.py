import html
import json
import os
import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement


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


def get_current_person_section() -> WebElement | None:
    """Get section where aria-label is '(NAME)'s photos'."""
    try:
        # Find all sections and filter for the one with the correct aria-label
        sections = driver.find_elements(
            By.XPATH, '//section[contains(@aria-label, "\'s photos")]'
        )

        # Find the section where aria-hidden is false
        for section in sections:
            grandpa = section.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
            aria_hidden = grandpa.get_attribute("aria-hidden")
            if aria_hidden == "false":
                return section

        # If no section found, raise an error
        raise Exception("No visible person's photos section found.")

    except Exception as e:
        print("Could not find the person's photos section:", e)
        return None


def get_photo_url_from_section(section: WebElement, photo_index: int) -> str | None:
    """Get the photo URL from the given section and photo index."""
    try:
        # Find the div with the specific aria-label for the photo index
        photo_div = section.find_element(
            By.XPATH, f'.//div[@aria-label="Profile Photo {photo_index}"]'
        )
        photo_div_html = photo_div.get_attribute("outerHTML")

        # Extract URL from style attribute
        match = re.search(r'url\("?([^"\)]+)"?\)', photo_div_html)
        if match:
            url = match.group(1)
            return html.unescape(url)
        else:
            print(f"No URL found in the style attribute for photo index {photo_index}.")
            return None
    except Exception as e:
        print(f"Could not find photo div for index {photo_index}:", e)
        return None


def get_all_them_photos() -> list[str]:
    """Get all photo elements in the current person's section."""
    section = get_current_person_section()
    if section is None:
        print("No current person section found.")
        return []

    try:
        photo_index = 1
        photo_urls = []

        while True:
            url = get_photo_url_from_section(section, photo_index)
            photo_urls.append((photo_index, url))
            photo_index += 1

            print(f"Found photo URL at index {photo_index}: {url}")

            # Try to click the next button
            next_button = section.find_element(
                By.XPATH, './/button[@aria-label="Next Photo"]'
            )

            # Check whether the button is disabled
            if not next_button.is_enabled():
                break  # Exit the loop if the button is disabled

            next_button.click()  # Click to go to the next photo
            time.sleep(0.1)  # Small delay to allow the photo to load

        return photo_urls

    except Exception as e:
        print("Could not find photo elements:", e)
        return []


def go_into_more_details():
    """Click on the 'Open Profile' button to see more details."""
    try:
        # Find the span with "Open Profile"
        span_open_profile = driver.find_element(
            By.XPATH, "//span[text()='Open Profile']"
        )
        button_open_profile = span_open_profile.find_element(By.XPATH, "..")
        # Click to open the full profile
        button_open_profile.click()
        time.sleep(0.5)  # Wait for the profile to open
    except Exception as e:
        print("Could not find or click 'Open Profile' button:", e)


def get_more_details_section(name: str) -> WebElement | None:
    try:
        return driver.find_element(
            By.XPATH,
            f"//h2[text()='{name}']",
        )

    except Exception as e:
        print("Could not find more details section:", e)
        return None


def get_about_me_text() -> str | None:
    """Get the 'About Me' text from the profile."""
    try:
        # go_into_more_details()

        # Get about by finding h2 with text "About Me"
        about_me_section = get_more_details_section("About me")

        if about_me_section is None:
            print("No 'About me' section found.")
            return None

        # Get uncle of about_me_element, so next div
        about_me_parent = about_me_section.find_element(By.XPATH, "..")

        # Get the next sibling div which contains the actual text
        about_me_div_sibling = about_me_parent.find_element(
            By.XPATH, "following-sibling::div"
        )
        return about_me_div_sibling.text

    except Exception as e:
        print("Could not find 'About Me' section:", e)
        return None


def get_sibling(element: WebElement) -> WebElement | None:
    """Get the next sibling of the given element."""
    try:
        return element.find_element(By.XPATH, "following-sibling::*")
    except Exception as e:
        print("Could not find sibling element:", e)
        return None


def get_essentials() -> list[str]:
    """Get essential details like how far, where they live, job, school."""
    try:
        essentials_div = get_more_details_section("Essentials")

        if essentials_div is None:
            print("No 'Essentials' section found.")
            return []

        essentials_div_parent = essentials_div.find_element(By.XPATH, "..")
        essentials_div_sibling = get_sibling(essentials_div_parent)

        if essentials_div_sibling is None:
            print("No sibling found for 'Essentials' div.")
            return []

        essentials = essentials_div_sibling.text.split("\n")
        return essentials

    except Exception as e:
        print("Could not find essential details:", e)
        return []


# Update the scrape_tinder function to find photos based on the specified criteria
def scrape_tinder():
    data = []

    # Find the section containing NAME's photos
    try:
        photos_section = driver.find_element(
            By.XPATH, '//div[@aria-label="Profile Photo 1"]'
        )

        # Get the URL from the style attribute
        photos_section_html = photos_section.get_attribute("outerHTML")
        assert photos_section_html is not None, (
            "Could not retrieve outerHTML of the photos section."
        )

        photo_urls = re.findall(r'url\("?([^"\)]+)"?\)', photos_section_html)
        for url in photo_urls:
            decoded_url = html.unescape(url)
            data.append({"image_url": decoded_url})

        # for photo in photo_elements:
        #     # Extract the background image URL from the style attribute
        #     style = photo.get_attribute("style")
        #     if style:
        #         match = re.search(r"url\\(\\?\"(.*?)\\?\"\\)", style)
        #         if match:
        #             image_url = match.group(1)
        #             data.append({"image_url": image_url})
    except Exception as e:
        print("Could not find photos section or profile images:", e)

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


# def download_images(urls: list[str], id: int):
#     """Download images from the given URLs and save them locally."""
#     save_path = "


# Run the scraper
scrape_tinder()

# Always quit the driver
driver.quit()


section = get_current_person_section()
# Get div with Profile Photo 1
photo_div = section.find_element(By.XPATH, ".//div[@aria-label='Profile Photo 1']")
photo_div_html = photo_div.get_attribute("outerHTML")
print(photo_div_html)
# Extract URL from style attribute
photo_urls = re.findall(r'url\("?([^"\)]+)"?\)', photo_div_html)
print(photo_urls)
for url in photo_urls:
    decoded_url = html.unescape(url)
    print(decoded_url)

print(decoded_url)


print(section.get_attribute("outerHTML"))

# Print the aria-label attribute
print(section.get_attribute("aria-label"))

# Print whole section HTML into a file
with open("section_about.html", "w", encoding="utf-8") as f:
    f.write(section.get_attribute("outerHTML"))

photo_index = 2

# Click on the next photo button
next_button = section.find_element(By.XPATH, './/button[@aria-label="Next Photo"]')

next_button.click()
print(f"Clicked to photo index {photo_index}")

photo_index = 1
url = get_photo_url_from_section(section, 1)
# print(f"Photo URL at index {photo_index}: {url}")

url = get_photo_url_from_section(section, 2)
url

urls = get_all_them_photos()

print("All photo URLs:", urls)
urls


about_me_lol = get_about_me_text()
about_me_lol


# Get the HTML of the site
with open("page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)


# Get uncle of the section
grandpa = section.find_element(By.XPATH, "..").find_element(By.XPATH, "..")

# In grandpa, find "Open Profile" button
span_open_profile = grandpa.find_element(By.XPATH, ".//span[text()='Open Profile']/..")
span_open_profile.click()

# Get about by finding h2 with text "About Me"
about_me_element = driver.find_element(
    # By.XPATH, "//*[contains(text(), 'About me')]/following-sibling::*"
    By.XPATH,
    "//h2[text()='About me']",
)
# Get uncle of about_me_element, so next div
about_me_parent = about_me_element.find_element(By.XPATH, "..")

# Get the next sibling div which contains the actual text
about_me_div_sibling = about_me_parent.find_element(By.XPATH, "following-sibling::div")
about_me_div_sibling.text

# Show children of about_me_div
for child in about_me_div.find_elements(By.XPATH, "./*"):
    # Just print the tag name and text
    print("Child:", child.tag_name, child.text)


about_me_text = about_me_element.text

about_me_text
