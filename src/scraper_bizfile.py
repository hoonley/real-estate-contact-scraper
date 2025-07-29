import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COMPANY_CSV = "output/sample_output4.csv"
RESULTS_CSV = "output/bizfile_selenium_results.csv"
SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"
PAUSE_AFTER_SEARCH = (12, 22)

def setup_driver():
    options = Options()
    options.add_argument("--window-size=1200,900")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

def search_bizfile(company_name, driver):
    wait = WebDriverWait(driver, 20)
    try:
        driver.get(SEARCH_URL)
        # Wait for input, fill in the company name
        input_box = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='Search by name or file number']")
            )
        )
        input_box.clear()
        input_box.send_keys(company_name)
        
        # Wait for and click the search button!
        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.search-button[aria-label='Execute search']")
            )
        )
        search_btn.click()

        time.sleep(5)
        try:
            result_elem = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".result-row .business-name")))
            result_text = result_elem.text
        except Exception:
            result_text = "No results or selector needs update"
        return {"Company": company_name, "Result": result_text, "Status": "OK"}
    except Exception as e:
        return {"Company": company_name, "Result": "", "Status": f"Error: {e}"}


def main():
    df = pd.read_csv(COMPANY_CSV)
    company_rows = df[df["Owner Type"].str.lower() == "company"].copy()
    company_names = company_rows["Owner Name"].dropna().unique()

    results = []
    driver = setup_driver()

    for i, company in enumerate(company_names):
        print(f"\n[{i+1}/{len(company_names)}] Searching: {company}")
        info = search_bizfile(company, driver)
        print(f"    → {info['Status']}: {info['Result']}")
        results.append(info)
        pause = random.uniform(*PAUSE_AFTER_SEARCH)
        print(f"    ⏳ Waiting {pause:.1f}s before next search...")
        time.sleep(pause)

    driver.quit()
    pd.DataFrame(results).to_csv(RESULTS_CSV, index=False)
    print(f"\n✅ Done! Results saved to {RESULTS_CSV}")

if __name__ == "__main__":
    main()
