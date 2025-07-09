import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pyautogui

# ========== CONFIGURATION ==========
CONFIRM_BTN_X = 1302   # update if your button moves!
CONFIRM_BTN_Y = 900    # update this to the lower Y you measured!
PAUSE_BETWEEN_SEARCHES = (10, 15)  # seconds, random between searches

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    # Uncomment for headless:
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    # Open Skip Genie search page immediately
    driver.get("https://web.skipgenie.com/user/search")
    return driver


def split_name(owner_name):
    # Naive split: First word = first name, last word = last name
    parts = owner_name.strip().split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, last

def click_yes_execute_search():
    """Clicks the 'Yes, Execute Search' button using pyautogui."""
    time.sleep(1.5)  # Small pause to let the dialog load
    pyautogui.moveTo(CONFIRM_BTN_X, CONFIRM_BTN_Y, duration=0.2)
    pyautogui.click()
    time.sleep(1)  # Pause to let search process

def get_phone_numbers_from_skipgenie(driver):
    """
    Returns a list of phone numbers (text) under the 'Possible Phone Numbers' section.
    """
    phone_numbers = []
    try:
        # Locate the 'Possible Phone Numbers' h5
        h5 = driver.find_element(By.XPATH, "//h5[contains(text(), 'Possible Phone Numbers')]")
        parent_div = h5.find_element(By.XPATH, "./..")
        phone_divs = parent_div.find_elements(By.CLASS_NAME, "mb-3")
        for div in phone_divs:
            try:
                # Extract the <p> text, split by lines
                p = div.find_element(By.TAG_NAME, "p")
                lines = p.text.strip().splitlines()
                if lines:
                    # Format: "(612) 408-3611 (Wireless)"
                    number = lines[0].strip()
                    phone_type = lines[1].strip() if len(lines) > 1 else ""
                    phone_numbers.append(f"{number} {phone_type}".strip())
            except Exception as inner:
                continue
    except Exception as e:
        print("⚠️ Could not extract phone numbers:", e)
    return phone_numbers

def search_skip_genie(first_name, last_name, street_address, zip_code, driver):
    # Go to Skip Genie search page (already logged in)
    driver.get("https://web.skipgenie.com/user/search")
    time.sleep(2)

    # Fill First Name
    first_name_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='First Name']")
    first_name_input.clear()
    first_name_input.send_keys(first_name)

    # Fill Last Name
    last_name_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Last Name']")
    last_name_input.clear()
    last_name_input.send_keys(last_name)

    # Fill Street Address
    street_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Street Address']")
    street_input.clear()
    street_input.send_keys(street_address)

    # Fill Zip/Postal Code
    zip_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Zip/Postal Code']")
    zip_input.clear()
    zip_input.send_keys(str(zip_code))

    # Click "Get Info"
    get_info_btn = driver.find_element(By.CSS_SELECTOR, ".pu_btn_user_search")
    driver.execute_script("arguments[0].click();", get_info_btn)

    # Wait for confirmation popup, then click "Yes, Execute Search"
    time.sleep(2)
    click_yes_execute_search()

    # Wait for results to load (increase if your internet is slow)
    time.sleep(4)
    phone_numbers = get_phone_numbers_from_skipgenie(driver)
    return phone_numbers

def main():
    # Load your processed CSV with all rows split/classified
    df = pd.read_csv("output/owners_split_classified.csv")
    individuals_df = df[df["Owner Type"] == "individual"].copy()

    driver = setup_driver()

    # Pause for manual login (let user log in securely)
    input("\n🔑 Log in to Skip Genie in the browser, navigate to the search page, then press Enter here to begin...")

    results = []
    for idx, row in individuals_df.iterrows():
        owner_name = row["Owner Name"]
        street_address = row.get("Address", "")
        zip_code = str(row.get("ZIP Code", ""))  # Make sure zip is string

        # --- Reverse name if necessary! (last name, first name) ---
        last_name, first_name = split_name(owner_name)
        # If your input is already "First Last", use:
        # first_name, last_name = split_name(owner_name)

        print(f"🔎  Searching: {first_name} {last_name} | {street_address} | {zip_code}")

        try:
            phone_numbers = search_skip_genie(
                first_name, last_name, street_address, zip_code, driver
            )
            results.append({
                "Owner Name": owner_name,
                "First Name": first_name,
                "Last Name": last_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Phone Numbers": ", ".join(phone_numbers)
            })
        except Exception as e:
            print(f"❌ Error searching for {owner_name}: {e}")
            results.append({
                "Owner Name": owner_name,
                "First Name": first_name,
                "Last Name": last_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Phone Numbers": ""
            })
        # Pause between each search (rate limiting)
        time.sleep(random.uniform(*PAUSE_BETWEEN_SEARCHES))

    driver.quit()

    # Save all results
    output_file = "output/skip_genie_results.csv"
    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"\n✅ Done! Saved as: {output_file}")

if __name__ == "__main__":
    main()
