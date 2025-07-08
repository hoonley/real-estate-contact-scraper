import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm  # Progress bar

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    # Uncomment for headless (background) mode:
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver

def search_skip_genie(first_name, last_name, street_address, zip_code, driver):
    # Open the Skip Genie dashboard/search page
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
    zip_input.send_keys(zip_code)

    # Click "Get Info"
    get_info_btn = driver.find_element(By.CSS_SELECTOR, ".pu_btn_user_search")
    driver.execute_script("arguments[0].click();", get_info_btn)

    # Wait for results to load
    time.sleep(4)

    try:
        results_div = driver.find_element(By.CSS_SELECTOR, ".results-container")
        results_text = results_div.text
    except NoSuchElementException:
        results_text = "No results found or selector needs update."
        # Save the page source for debugging
        with open("output/last_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    return results_text

def split_name(owner_name):
    # Naive split: First is first word, last is last word
    parts = owner_name.strip().split()
    first = parts[0] if parts else ""
    last = parts[-1] if len(parts) > 1 else ""
    return first, last

def main():
    df = pd.read_csv("output/owners_split_classified.csv")
    individuals_df = df[df["Owner Type"] == "individual"].copy()

    driver = setup_driver()

    # Pause for manual login
    input("\n🔑 Log in to Skip Genie in the opened browser. When you're ready, press ENTER here...")

    results = []
    output_file = "output/skip_genie_results.csv"

    for idx, row in tqdm(individuals_df.iterrows(), total=len(individuals_df)):
        owner_name = row["Owner Name"]
        street_address = row.get("Address", "")
        zip_code = str(row.get("ZIP Code", ""))

        first_name, last_name = split_name(owner_name)

        if not first_name or not last_name:
            print(f"⏭️ Skipping '{owner_name}' due to missing first or last name.")
            continue

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

        # Save every 20 searches as a checkpoint
        if idx % 20 == 0 and idx != 0:
            pd.DataFrame(results).to_csv(output_file, index=False)
            print(f"💾 Progress saved after {idx} searches.")

        # Random pause 10-15 seconds for rate limiters
        time.sleep(random.uniform(10, 15))

    driver.quit()

    # Final save
    pd.DataFrame(results).to_csv(output_file, index=False)
    print(f"\n✅ Done! Results saved to {output_file}")

if __name__ == "__main__":
    main()
