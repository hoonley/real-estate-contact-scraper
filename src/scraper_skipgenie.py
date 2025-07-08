import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    # options.add_argument("--headless=new")  # Uncomment if you want headless mode
    driver = webdriver.Chrome(options=options)
    return driver

def split_name(owner_name):
    # Assumes "LAST FIRST" format
    parts = owner_name.strip().split()
    if len(parts) >= 2:
        last = parts[0]
        first = " ".join(parts[1:])
    elif len(parts) == 1:
        last = parts[0]
        first = ""
    else:
        last = first = ""
    return first, last

def search_skip_genie(first_name, last_name, street_address, zip_code, driver):
    driver.get("https://web.skipgenie.com/user/search")
    time.sleep(2)

    # Fill First Name
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='First Name']").send_keys(first_name)
    # Fill Last Name
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Last Name']").send_keys(last_name)
    # Fill Street Address
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Street Address']").send_keys(street_address)
    # Fill Zip/Postal Code
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Zip/Postal Code']").send_keys(zip_code)
    # Click "Get Info"
    driver.find_element(By.CSS_SELECTOR, ".pu_btn_user_search").click()

    # Wait for the confirmation popup and click "YES, EXECUTE SEARCH"
    try:
        yes_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'YES, EXECUTE SEARCH')]"))
        )
        yes_button.click()
        print("✅ Clicked YES, EXECUTE SEARCH")
    except Exception as e:
        print("❌ Confirmation button not found or not clickable:", e)
        return ""

    # Wait for results to load
    time.sleep(4)

    try:
        results_div = driver.find_element(By.CSS_SELECTOR, ".results-container")
        results_text = results_div.text
    except NoSuchElementException:
        results_text = ""
    return results_text

def main():
    input_path = "output/owners_split_classified.csv"  # Adjust if your file is elsewhere
    output_path = "output/skip_genie_results.csv"

    df = pd.read_csv(input_path)
    individuals_df = df[df["Owner Type"] == "individual"].copy()

    driver = setup_driver()
    input("\n🔑 Log in to Skip Genie in the browser, navigate to the search page, then press Enter here to begin...")

    results = []

    for idx, row in tqdm(individuals_df.iterrows(), total=len(individuals_df)):
        owner_name = row["Owner Name"]
        street_address = row.get("Address", "")
        zip_code = str(row.get("ZIP Code", ""))

        first_name, last_name = split_name(owner_name)
        if not first_name or not last_name:
            print(f"⏭️ Skipping {owner_name}: couldn't parse name.")
            continue

        print(f"🔎 Searching: {first_name} {last_name} | {street_address} | {zip_code}")
        try:
            result_text = search_skip_genie(
                first_name, last_name, street_address, zip_code, driver
            )
            results.append({
                "Owner Name": owner_name,
                "First Name": first_name,
                "Last Name": last_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Skip Genie Result": result_text
            })
        except Exception as e:
            print(f"❌ Error searching for {owner_name}: {e}")
            results.append({
                "Owner Name": owner_name,
                "First Name": first_name,
                "Last Name": last_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Skip Genie Result": f"ERROR: {e}"
            })

        # Optional: Save every 20 records for crash protection
        if idx % 20 == 0 and idx != 0:
            pd.DataFrame(results).to_csv(output_path, index=False)
            print(f"💾 Progress saved ({idx} records)")

        time.sleep(random.uniform(10, 15))  # random pause

    driver.quit()
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"\n✅ Done! Saved as: {output_path}")

if __name__ == "__main__":
    main()
