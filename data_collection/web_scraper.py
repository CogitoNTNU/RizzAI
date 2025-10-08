import html
import json
import os
import re
import time
from collections.abc import Callable
from pathlib import Path

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.webelement import WebElement


load_dotenv(dotenv_path="data_collection/.env")


URL = os.getenv("SCRAPE_URL", "NOT-SET")
PROFILE_FOLDER = os.getenv(
    "PROFILE_FOLDER", "your-profile-folder"
)  # Replace with your Firefox profile folder name
WIN_USERNAME = os.getenv("WIN_USERNAME", "your-windows-username")
LAST_ID_PATH = Path("data_collection/profiles/.last_id")


def read_last_id() -> int:
    """Read the last used user ID from the .last_id file."""
    if LAST_ID_PATH.exists():
        with open(LAST_ID_PATH, encoding="utf-8") as f:
            return int(f.read().strip())
    else:
        return -1  # Default value if the file does not exist


def write_last_id(last_id: int) -> None:
    """Write the last used user ID to the .last_id file."""
    with open(LAST_ID_PATH, "w", encoding="utf-8") as f:
        f.write(str(last_id))


# Get the last used user ID from the .last_id file
last_user_id: int = read_last_id()

options = Options()

# Verify the profile folder path
profile_path = (
    Path("C:\\Users")
    / WIN_USERNAME
    / "AppData"
    / "Roaming"
    / "Mozilla"
    / "Firefox"
    / "Profiles"
    / PROFILE_FOLDER
)
if not profile_path.exists():
    raise Exception(
        f"Specified profile folder '{profile_path}' does not exist. Please check the PROFILE_FOLDER and WIN_USERNAME environment variables."
    )

options.add_argument("-profile")
options.add_argument(str(profile_path))

driver = webdriver.Firefox(service=Service(), options=options)


def get_current_person_section() -> WebElement:
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
        raise Exception("Could not find the person's photos section") from e


def get_photo_url_from_section(section: WebElement, photo_index: int) -> str:
    """Get the photo URL from the given section and photo index."""
    try:
        # Find the div with the specific aria-label for the photo index
        photo_div = section.find_element(
            By.XPATH, f'.//div[@aria-label="Profile Photo {photo_index}"]'
        )
        photo_div_html = photo_div.get_attribute("outerHTML")

        if photo_div_html is None:
            raise Exception(f"No outerHTML found for photo index {photo_index}.")

        # Extract URL from style attribute
        match = re.search(r'url\("?([^"\)]+)"?\)', photo_div_html)
        if match:
            url = match.group(1)
            return html.unescape(url)
        else:
            raise Exception(
                f"No URL found in the style attribute for photo index {photo_index}."
            )
    except Exception as e:
        raise Exception(f"Could not find photo div for index {photo_index}") from e


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
            url = url.strip('"')  # Remove any enclosing quotes

            photo_urls.append(url)
            photo_index += 1

            # Try to click the next button
            next_button = section.find_element(
                By.XPATH, './/button[@aria-label="Next Photo"]'
            )

            # Check whether the button is disabled
            if not next_button.is_enabled():
                break  # Exit the loop if the button is disabled

            next_button.click()  # Click to go to the next photo
            time.sleep(0.5)  # Small delay to allow the photo to load

        return photo_urls

    except Exception as e:
        raise Exception("Could not find photo elements") from e


def open_more_details() -> None:
    """Use key ARROW_UP to open more details."""
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.ARROW_UP).perform()


def close_more_details() -> None:
    """Use key ARROW_DOWN to close more details."""
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.ARROW_DOWN).perform()


def _give_like() -> None:
    """Like by pressing the right arrow key."""
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.ARROW_RIGHT).perform()


def _give_nonono() -> None:
    """Dislike by pressing the left arrow key."""
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.ARROW_LEFT).perform()


def get_more_details_section(name: str) -> WebElement:
    try:
        return driver.find_element(
            By.XPATH,
            f"//h2[text()='{name}']",
        )

    except Exception as e:
        raise Exception(f"Could not find more details section: {name}") from e


def get_about_me_text() -> str | None:
    """Get the 'About Me' text from the profile."""
    try:
        # go_into_more_details()

        # Get about by finding h2 with text "About Me"
        about_me_section = get_more_details_section("About me")

        # Get uncle of about_me_element, so next div
        about_me_parent = about_me_section.find_element(By.XPATH, "..")

        # Get the next sibling div which contains the actual text
        about_me_div_sibling = about_me_parent.find_element(
            By.XPATH, "following-sibling::div"
        )
        return about_me_div_sibling.text

    except Exception as e:
        raise Exception("Could not find 'About Me' section") from e


def get_sibling(element: WebElement) -> WebElement:
    """Get the next sibling of the given element."""
    try:
        return element.find_element(By.XPATH, "following-sibling::*")
    except Exception as e:
        raise Exception("Could not find sibling element") from e


def get_essentials() -> list[str]:
    """Get essential details like how far, where they live, job, school."""
    try:
        essentials_div = get_more_details_section("Essentials")

        essentials_div_parent = essentials_div.find_element(By.XPATH, "..")
        essentials_div_sibling = get_sibling(essentials_div_parent)

        essentials = essentials_div_sibling.text.split("\n")
        return essentials

    except Exception as e:
        raise Exception("Could not find 'Essentials' section") from e


def get_basics() -> dict[str, str]:
    """Get basic details like height, family plans, drinking, smoking."""
    try:
        basics_div = get_more_details_section("Basics")

        basics_div_parent = basics_div.find_element(By.XPATH, "..")
        basics_div_sibling = get_sibling(basics_div_parent)

        basics = basics_div_sibling.text.split("\n")

        # Pair keys and values from the basics list
        return {basics[i]: basics[i + 1] for i in range(0, len(basics) - 1, 2)}

    except Exception as e:
        raise Exception("Could not find Basics section") from e


def get_lifestyle() -> dict[str, str]:
    """Get lifestyle details like exercise, diet, pets."""
    try:
        lifestyle_div = get_more_details_section("Lifestyle")

        if lifestyle_div is None:
            print("No 'Lifestyle' section found.")
            return {}

        lifestyle_div_parent = lifestyle_div.find_element(By.XPATH, "..")
        lifestyle_div_sibling = get_sibling(lifestyle_div_parent)

        lifestyle = lifestyle_div_sibling.text.split("\n")

        # Pair keys and values from the lifestyle list
        return {lifestyle[i]: lifestyle[i + 1] for i in range(0, len(lifestyle) - 1, 2)}

    except Exception as e:
        raise Exception("Could not find 'Lifestyle' section") from e


def get_interests() -> list[str]:
    """Get interests like hiking, reading, traveling."""
    try:
        interests_div = get_more_details_section("Interests")

        interests_div_parent = interests_div.find_element(By.XPATH, "..")
        interests_div_sibling = get_sibling(interests_div_parent)

        interests = interests_div_sibling.text.split("\n")
        return interests

    except Exception as e:
        raise Exception("Could not find 'Interests' section") from e


def get_anthem() -> str | None:
    """Get anthem if available."""
    try:
        anthem_div = get_more_details_section("My anthem")

        anthem_div_parent = anthem_div.find_element(By.XPATH, "..")
        anthem_div_sibling = get_sibling(anthem_div_parent)

        # name, author = anthem_div_sibling.text.split("\n")
        # return f"{name} by {author}"
        return ", ".join(anthem_div_sibling.text.split("\n"))

    except Exception as e:
        raise Exception("Could not find anthem section") from e


def scrape_one_gyatt_or_potential_partner() -> None:
    """Scrape data for one potential partner."""
    section = get_current_person_section()

    name_aria = section.get_attribute("aria-label")
    if name_aria is None:
        raise Exception("No aria-label found for the current person section.")

    name_match = re.match(r"^(.*?)'s photos$", name_aria)
    if not name_match:
        raise Exception("Could not extract name from aria-label.")

    name = name_match.group(1)
    print("*" * 20)
    print(f"Scraping data for a potential partner: {name}")
    print("-" * 20)

    # Get all photo URLs
    photo_urls = get_all_them_photos()

    # Download photos
    new_last_user_id = read_last_id() + 1
    write_last_id(new_last_user_id)

    download_images(photo_urls, new_last_user_id)

    # Open more details to access About Me and Essentials
    open_more_details()
    time.sleep(0.7)  # Wait for the details to load

    about_me: str | None = None
    try:
        about_me = get_about_me_text()
    except Exception:
        print("Could not get 'About Me' text.")

    essentials: list[str] = []
    try:
        essentials = get_essentials()
    except Exception:
        print("Could not get 'Essentials' details.")

    basics: dict[str, str] = {}
    try:
        basics = get_basics()
    except Exception:
        print("Could not get 'Basics' details.")

    lifestyle: dict[str, str] = {}
    try:
        lifestyle = get_lifestyle()
    except Exception:
        print("Could not get 'Lifestyle' details.")

    interests: list[str] = []
    try:
        interests = get_interests()
    except Exception:
        print("Could not get 'Interests' details.")

    anthem: str | None = None
    try:
        anthem = get_anthem()
    except Exception:
        print("Could not get 'Anthem' details.")

    # Close more details
    close_more_details()
    time.sleep(0.7)  # Small delay to allow the UI to update

    # Compile data
    data = {
        "name": name,
        "about_me": about_me,
        "essentials": essentials,
        "basics": basics,
        "lifestyle": lifestyle,
        "interests": interests,
        "anthem": anthem,
    }

    # Save data to JSON
    output_path = Path("data_collection/profiles/")
    output_path.mkdir(parents=True, exist_ok=True)
    json_file_path = output_path / "text_data.json"

    # If the file does not exist, create it with an empty dict
    if not json_file_path.exists():
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump({}, f)

    # Write the new data into the JSON file
    # TODO: Make it more efficient by not loading the whole file every time
    # Such as using a database (SQLite, etc.)
    with open(json_file_path, "r+", encoding="utf-8") as f:
        all_data = json.load(f)
        all_data[new_last_user_id] = data
        f.seek(0)
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        f.truncate()

    print(f"Data for {name} saved to {json_file_path}")
    print("*" * 20)


class IntRef:
    """A simple wrapper for an integer to allow mutation within nested functions."""

    def __init__(self, value: int = 0) -> None:
        self.value = value


# Update the function to find photos based on the specified criteria
def scrape_website(
    profiles_to_scrape: IntRef | None = None,
    like_strategy: Callable[[], None] = _give_nonono,
) -> None:
    """Main function to scrape the website.

    Args:
        profiles_to_scrape (IntWrapper | None): Number of profiles to scrape. If None, scrape indefinitely.
        like_strategy (Callable[[], None]): Function to call for liking or disliking a profile.
    """
    while profiles_to_scrape is None or profiles_to_scrape.value > 0:
        scrape_one_gyatt_or_potential_partner()

        like_strategy()

        # Small delay to allow the next profile to load
        time.sleep(0.8)

        if profiles_to_scrape is not None:
            profiles_to_scrape.value -= 1


def download_images(urls: list[str], id: int):
    """Download images from the given URLs and save them locally."""
    save_path = Path(f"data_collection/profiles/images/{id}")
    save_path.mkdir(parents=True, exist_ok=True)

    for idx, url in enumerate(urls):
        if url is None:
            continue
        try:
            image_data = requests.get(url).content
            with open(save_path / f"image_{idx}.jpg", "wb") as img_file:
                img_file.write(image_data)
            # print(f"Downloaded image {idx} from {url}")
        except Exception as e:
            print(f"Failed to download image from {url}: {e}")


class LikeStrategy:
    """Class to encapsulate like strategies."""

    @staticmethod
    def like() -> None:
        """NOTE: Sadly, we can't like them all.

        It's limited to 50-100 likes per 12 hours.
        But with click nope all the time, we can get duplicates.
        One option would be to uniquely store them using embeddings of the images
        and then check if we already have them, but that's a bit too much work for now.
        """
        _give_like()

    @staticmethod
    def nonono() -> None:
        _give_nonono()

    @staticmethod
    def coinflip(probability: float = 0.5) -> None:
        import random

        if random.random() < probability:
            _give_like()
        else:
            _give_nonono()


def main() -> None:
    """Main entry point for the scraper."""
    driver.maximize_window()
    driver.get(URL)

    input("Press Enter to start scraping...")

    profiles_to_scrape = IntRef(50)

    total_profiles = profiles_to_scrape.value
    want_more = True
    while want_more:
        try:
            scrape_website(
                profiles_to_scrape=profiles_to_scrape, like_strategy=LikeStrategy.like
            )
        except KeyboardInterrupt:
            print("Scraping interrupted by user.")
        except Exception as e:
            print(f"An error occurred: {e}")

        profiles_scraped = total_profiles - profiles_to_scrape.value
        print(f"Scraped {profiles_scraped}/{total_profiles} profiles.")

        want_more = (
            input("Do you want to scrape more profiles? (y/n): ").strip().lower() == "y"
        )

        if want_more and profiles_to_scrape.value == 0:
            try:
                additional = int(input("How many more profiles to scrape? ").strip())
                profiles_to_scrape.value += additional
                total_profiles += additional
            except ValueError:
                print("Invalid number.")

    print("Scraping completed.")

    # Always quit the driver
    driver.quit()


if __name__ == "__main__":
    main()
