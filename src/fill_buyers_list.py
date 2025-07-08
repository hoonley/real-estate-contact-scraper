import pandas as pd
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_phone_numbers(results_text):
    phones = []
    lines = results_text.splitlines()
    capture = False
    for line in lines:
        if "Possible Phone Numbers" in line:
            capture = True
            continue
        if capture:
            if not line.strip() or "Address History" in line or ":" in line:
                break
            found = re.findall(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", line)
            phones.extend(found)
    return ", ".join(phones)

def split_name(owner_name):
    # Assumes "LAST FIRST" format, e.g. "SMITH JOHN" -> First: JOHN, Last: SMITH
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

    # Fill fields
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='First Name']").send_keys(first_name)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Last Name']").send_keys(last_name)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Street Address']").send_keys(street_address)
    driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Zip/Postal Code']").send_keys(zip_code)
    driver.find_element(By.CSS_SELECTOR, ".pu_btn_user_search").click()

    # Wait for results
    time.sleep(4)

    try:
        results_div = driver.find_element(By.CSS_SELECTOR, ".results-container")
        results_text = results_div.text
    except NoSuchElementException:
        results_text = ""
    return results_text

def main():
    template_path = "input/Buyers List output.xlsx"
    csv_path = "output/owners_split_classified.csv"
    out_path = "output/Buyers List filled.xlsx"
    
    template = pd.read_excel(template_path)
    csv_data = pd.read_csv(csv_path)
    individuals = csv_data[csv_data["Owner Type"] == "individual"]

    columns = template.columns
    output_rows = []

    driver = setup_driver()
    input("\n🔑 Log in to Skip Genie, navigate to the search page, then press Enter to start...")

    for idx, row in tqdm(individuals.iterrows(), total=len(individuals)):
        lender_name = row.get("Lender Name", "")
        owner_name = row.get("Owner Name", "")
        street_address = row.get("Address", "")
        zip_code = str(row.get("ZIP Code", ""))

        first_name, last_name = split_name(owner_name)
        if not first_name or not last_name:
            print(f"⏭️ Skipping {owner_name}: couldn't parse name.")
            continue

        print(f"🔎 {first_name} {last_name} - {street_address} {zip_code}")
        results_text = search_skip_genie(first_name, last_name, street_address, zip_code, driver)
        phone_numbers = extract_phone_numbers(results_text)

        # Fill out only the required columns, leave others blank
        new_row = {col: "" for col in columns}
        new_row["Company Name"] = lender_name
        new_row["First Name"] = first_name
        new_row["Last Name"] = last_name
        new_row["Phone Number"] = phone_numbers

        output_rows.append(new_row)

        # Random wait (anti-bot/rate-limiting)
        time.sleep(random.uniform(10, 15))

        # Optional: Save every 20 records for crash protection
        if idx % 20 == 0 and idx != 0:
            pd.DataFrame(output_rows, columns=columns).to_excel(out_path, index=False)
            print(f"💾 Progress saved ({idx} records)")

    driver.quit()
    pd.DataFrame(output_rows, columns=columns).to_excel(out_path, index=False)
    print(f"\n✅ Done! Saved as: {out_path}")

if __name__ == "__main__":
    main()
