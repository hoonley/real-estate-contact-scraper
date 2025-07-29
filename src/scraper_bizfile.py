import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---- CONFIG ----
INPUT_CSV = "output/sample_output4.csv"
OWNER_TYPE_COLUMN = "Owner Type"
OWNER_NAME_COLUMN = "Owner Name"
SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"
PAUSE_BETWEEN_SEARCHES = (5, 10)  # seconds

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1200,800")
    # options.add_argument("--headless=new")  # Uncomment to run headless
    return webdriver.Chrome(options=options)

def open_and_search(driver, company_name):
    driver.get(SEARCH_URL)
    time.sleep(3)  # Wait for page to load

    # Input company name
    search_input = driver.find_element(By.CSS_SELECTOR, 'input.search-input')
    search_input.clear()
    search_input.send_keys(company_name)
    time.sleep(1)

    # Click search button
    search_btn = driver.find_element(By.CSS_SELECTOR, 'button.search-button')
    driver.execute_script("arguments[0].click();", search_btn)
    print(f"🔍 Searched: {company_name}")
    time.sleep(4)  # Wait for results to load

def click_exact_company(driver, company_name):
    import re
    time.sleep(2)
    rows = driver.find_elements(By.CSS_SELECTOR, 'div.interactive-cell-button')
    found = False
    # Normalize company name (remove extra spaces, lowercase)
    target = company_name.strip().lower()
    for row in rows:
        try:
            cell = row.find_element(By.CSS_SELECTOR, 'span.cell')
            text = cell.text.strip().lower()
            # Match ignoring entity number, just company name at start
            text_no_number = re.sub(r"\s*\([0-9]+\)", "", text)
            if text_no_number == target or text.startswith(target):
                print(f"✅ Clicking match: {cell.text}")
                driver.execute_script("arguments[0].click();", row)
                found = True
                break
        except Exception:
            continue
    if not found:
        print(f"❌ No close match found for '{company_name}'.")
    return found

def click_view_history(driver, timeout=10):
    try:
        wait = WebDriverWait(driver, timeout)
        btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[aria-label="View History"]')))
        for idx, b in enumerate(btns):
            print(f"Button {idx} HTML:", b.get_attribute('outerHTML'))
        btns = [b for b in btns if b.is_displayed() and b.is_enabled()]
        if not btns:
            print("❌ No visible View History button found.")
            return False
        driver.execute_script("arguments[0].click();", btns[0])
        print("🕑 Clicked View History.")
        time.sleep(2)
        return True
    except Exception as e:
        print("❌ Could not click View History:", e)
        return False




def main():
    df = pd.read_csv(INPUT_CSV)
    companies = df[df[OWNER_TYPE_COLUMN].str.lower() == "company"][OWNER_NAME_COLUMN].dropna().unique()

    driver = setup_driver()

    for idx, company in enumerate(companies):
        print(f"\n===[{idx+1}/{len(companies)}] {company}===")
        open_and_search(driver, company)
        match_found = click_exact_company(driver, company)
        # TODO: Scrape info from detail page if needed!

        # Pause between searches
        sleep_for = random.uniform(*PAUSE_BETWEEN_SEARCHES)
        print(f"Sleeping {sleep_for:.1f}s before next search...")
        time.sleep(sleep_for)

    driver.quit()
    print("✅ Done with all companies.")

if __name__ == "__main__":
    main()
