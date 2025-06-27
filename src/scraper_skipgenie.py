import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    # Uncomment the next line for headless (no-browser) mode:
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

def search_skip_genie(first_name, last_name, street_address, zip_code, driver):
    # Open the Skip Genie dashboard or search page
    driver.get("https://app.skipgenie.com/dashboard")
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
    zip_input.send_keys(zip_code)

    # Click "Get Info"
    get_info_btn = driver.find_element(By.CSS_SELECTOR, ".pu_btn_user_search")
    driver.execute_script("arguments[0].click();", get_info_btn)

    # Wait for results to load (increase time if needed)
    time.sleep(4)

    # Try to get the results text - adjust selector as needed!
    try:
        # You may need to update this selector for your real results
        results_div = driver.find_element(By.CSS_SELECTOR, ".results-container")
        results_text = results_div.text
    except NoSuchElementException:
        results_text = "No results found or selector needs update."

    return results_text

def split_name(owner_name):
    # Naive split: First is first word, last is last word
    parts = owner_name.strip().split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, last

def main():
    # Load processed CSV with all rows split/classified
    df = pd.read_csv("output/owners_split_classified.csv")
    individuals_df = df[df["Owner Type"] == "individual"].copy()

    driver = setup_driver()

    # Pause for manual login (if not using cookies/session automation)
    input("\n🔑 Log in to Skip Genie in the opened browser. When you're on the dashboard/search page, press ENTER here...")

    results = []
    for idx, row in individuals_df.iterrows():
        owner_name = row["Owner Name"]
        street_address = row.get("Address", "")
        zip_code = str(row.get("ZIP Code", ""))  # Make sure zip is string

        first_name, last_name = split_name(owner_name)

        print(f"🔎 Searching: {first_name} {last_name} | {street_address} | {zip_code}")
        try:
            result_text = search_skip_genie(
                first_name, last_name, street_address, zip_code, driver
            )
            results.append({
                "Owner Name": owner_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Skip Genie Result": result_text
            })
        except Exception as e:
            print(f"❌ Error searching for {owner_name}: {e}")
            results.append({
                "Owner Name": owner_name,
                "Street Address": street_address,
                "ZIP Code": zip_code,
                "Skip Genie Result": f"ERROR: {e}"
            })

    driver.quit()

    # Save all results
    output_file = "output/skip_genie_results.csv"
    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"\n✅ Done! Results saved to {output_file}")

if __name__ == "__main__":
    main()
