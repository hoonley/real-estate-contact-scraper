import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# ========== CONFIGURATION ==========
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

def click_yes_execute_search(driver):
    """
    Clicks the 'YES, EXECUTE SEARCH' button in the confirmation modal.
    """
    try:
        # Wait for the confirmation dialog to appear
        wait = WebDriverWait(driver, 10)
        
        # Try the exact selectors for the green "YES, EXECUTE SEARCH" button
        possible_selectors = [
            # Target the green button specifically
            "//button[contains(text(), 'YES, EXECUTE SEARCH')]",
            "//button[contains(text(), 'YES')]",
            "//button[contains(text(), 'EXECUTE SEARCH')]",
            
            # CSS selectors for the green button
            "button:contains('YES, EXECUTE SEARCH')",
            "button:contains('YES')",
            
            # Generic modal button approaches
            ".modal button:last-child",
            ".modal-footer button:nth-child(2)",  # Second button (usually "Yes")
            "[role='dialog'] button:last-child",
            
            # Look for buttons in the modal/dialog
            ".swal2-actions button:last-child",
            ".modal-content button:last-child"
        ]
        
        button_found = False
        for selector in possible_selectors:
            try:
                if selector.startswith("//"):
                    # XPath selector
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    # CSS selector  
                    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                
                print(f"✅ Found confirmation button with selector: {selector}")
                # Use JavaScript click for maximum reliability
                driver.execute_script("arguments[0].click();", button)
                button_found = True
                break
                
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not button_found:
            print("⚠️ Trying fallback approach - looking for all modal buttons...")
            try:
                # Find all buttons in the modal and click the one with "YES" or "EXECUTE"
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    button_text = btn.text.upper()
                    if any(word in button_text for word in ["YES", "EXECUTE", "SEARCH"]):
                        if btn.is_displayed() and btn.is_enabled():
                            print(f"✅ Found button with text: '{btn.text}'")
                            driver.execute_script("arguments[0].click();", btn)
                            button_found = True
                            break
            except Exception as e:
                print(f"❌ Fallback method failed: {e}")
        
        if not button_found:
            print("⚠️ Final attempt - using coordinate-based approach...")
            try:
                # As a last resort, find any visible button and check its position
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in buttons:
                    if btn.is_displayed() and "YES" in btn.text.upper():
                        # Scroll to button and click
                        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", btn)
                        button_found = True
                        print("✅ Clicked button using final fallback")
                        break
            except Exception as e:
                print(f"❌ Final fallback failed: {e}")
        
        if button_found:
            time.sleep(3)  # Wait longer for search to process
            print("🔍 Search executed successfully")
        else:
            print("❌ Could not find or click confirmation button")
            # Print all visible buttons for debugging
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print("🔍 Available buttons:")
                for i, btn in enumerate(buttons):
                    if btn.is_displayed():
                        print(f"  {i}: '{btn.text}' - Class: {btn.get_attribute('class')}")
            except:
                pass
            
    except Exception as e:
        print(f"❌ Error in click_yes_execute_search: {e}")

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

def find_and_fill_input(driver, field_name, value, possible_selectors):
    """Helper function to try multiple selectors for form fields"""
    if not value:
        return False
        
    for selector in possible_selectors:
        try:
            if selector.startswith("//"):
                element = driver.find_element(By.XPATH, selector)
            else:
                element = driver.find_element(By.CSS_SELECTOR, selector)
            
            element.clear()
            time.sleep(0.5)
            element.send_keys(str(value))
            print(f"✅ Filled {field_name}: {value}")
            return True
        except Exception as e:
            continue
    
    print(f"❌ Could not find {field_name} field")
    return False

def search_skip_genie(first_name, last_name, street_address, zip_code, driver):
    # Go to Skip Genie search page (already logged in)
    driver.get("https://web.skipgenie.com/user/search")
    time.sleep(3)

    # First Name - try multiple selectors
    first_name_selectors = [
        "input[placeholder*='First Name']",
        "input[placeholder*='first name']",
        "input[name*='first']",
        "input[id*='first']",
        "#firstName",
        "#first_name",
        "//input[contains(@placeholder, 'First')]",
        "//input[contains(@name, 'first')]"
    ]
    find_and_fill_input(driver, "First Name", first_name, first_name_selectors)

    # Last Name - try multiple selectors  
    last_name_selectors = [
        "input[placeholder*='Last Name']",
        "input[placeholder*='last name']", 
        "input[name*='last']",
        "input[id*='last']",
        "#lastName",
        "#last_name",
        "//input[contains(@placeholder, 'Last')]",
        "//input[contains(@name, 'last')]"
    ]
    find_and_fill_input(driver, "Last Name", last_name, last_name_selectors)

    # Street Address - try multiple selectors
    address_selectors = [
        "input[placeholder*='Street Address']",
        "input[placeholder*='Address']",
        "input[placeholder*='street']",
        "input[name*='address']",
        "input[id*='address']",
        "#address",
        "#street",
        "//input[contains(@placeholder, 'Address')]",
        "//input[contains(@placeholder, 'Street')]"
    ]
    find_and_fill_input(driver, "Street Address", street_address, address_selectors)

    # ZIP Code - try multiple selectors
    zip_selectors = [
        "input[placeholder*='Zip/Postal Code']",
        "input[placeholder*='ZIP']",
        "input[placeholder*='zip']", 
        "input[placeholder*='Postal']",
        "input[name*='zip']",
        "input[id*='zip']",
        "#zipCode",
        "#zip",
        "//input[contains(@placeholder, 'Zip')]",
        "//input[contains(@placeholder, 'ZIP')]"
    ]
    find_and_fill_input(driver, "ZIP Code", zip_code, zip_selectors)

    time.sleep(1)

    # Click "Get Info" button - try multiple selectors
    get_info_selectors = [
        ".pu_btn_user_search",
        "button[type='submit']",
        "input[type='submit']",
        "button:contains('Get Info')",
        "button:contains('Search')",
        ".search-btn",
        ".btn-search",
        "//button[contains(text(), 'Get Info')]",
        "//button[contains(text(), 'Search')]",
        "//input[@value='Get Info']"
    ]
    
    button_clicked = False
    for selector in get_info_selectors:
        try:
            if selector.startswith("//"):
                button = driver.find_element(By.XPATH, selector)
            else:
                button = driver.find_element(By.CSS_SELECTOR, selector)
            
            driver.execute_script("arguments[0].click();", button)
            print("✅ Clicked search button")
            button_clicked = True
            break
        except Exception as e:
            continue
    
    if not button_clicked:
        print("❌ Could not find search button")
        return []

    # Wait for confirmation popup, then click "Yes, Execute Search"
    print("⏳ Waiting for confirmation popup...")
    time.sleep(3)
    
    # Debug: Let's see what's on the page
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔍 Found {len(buttons)} buttons on page:")
        for i, btn in enumerate(buttons[:10]):  # Show first 10 buttons
            if btn.is_displayed():
                print(f"  {i}: '{btn.text.strip()}' - Visible: {btn.is_displayed()} - Enabled: {btn.is_enabled()}")
    except Exception as e:
        print(f"Debug failed: {e}")
    
    click_yes_execute_search(driver)

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
    input("\n🔐 Log in to Skip Genie in the browser, navigate to the search page, then press Enter here to begin...")

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