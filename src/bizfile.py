import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By

# ============ CONFIGURATION ============
SCRAPERAPI_KEY = "YOUR_SCRAPERAPI_KEY"  # <-- REPLACE WITH YOUR KEY
COMPANY_CSV = "output/owners_split_classified.csv"  # Change path if needed
RESULTS_CSV = "output/bizfile_results.csv"
SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"
SEARCH_WAIT = 3    # Seconds to wait after each search
SLEEP_RANGE = (8, 15)  # Sleep randomly between searches

# ============ LOAD COMPANIES ============
df = pd.read_csv(COMPANY_CSV)
company_rows = df[df["Owner Type"] == "company"].copy()
company_names = company_rows["Owner Name"].dropna().unique()

# ============ SELENIUM SETUP ============
def setup_driver():
    PROXY = "scraperapi.proxy:8001"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server=http://{PROXY}')
    # ScraperAPI proxy authentication (key as username)
    chrome_options.add_argument(f'--proxy-auth={SCRAPERAPI_KEY}:')
    chrome_options.add_argument("--window-size=1200,800")
    # Optional: User agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

# ============ SEARCH FUNCTION ============
def search_bizfile(company_name, driver):
    try:
        driver.get(SEARCH_URL)
        time.sleep(SEARCH_WAIT)
        # Find input box and enter company name
        input_box = driver.find_element(By.CSS_SELECTOR, "input#businessSearch")
        input_box.clear()
        input_box.send_keys(company_name)
        # Find and click the search button
        search_btn = driver.find_element(By.CSS_SELECTOR, "button#search")
        search_btn.click()
        time.sleep(SEARCH_WAIT + 2)

        # Example: grab the name of first result (you can expand on this)
        try:
            result_elem = driver.find_element(By.CSS_SELECTOR, ".resultItem .businessName")
            result_text = result_elem.text
            return {"company": company_name, "result": result_text, "status": "OK"}
        except Exception as e:
            return {"company": company_name, "result": "", "status": "No result"}

    except Exception as e:
        return {"company": company_name, "result": "", "status": f"Error: {e}"}

# ============ MAIN LOOP ============
def main():
    results = []
    driver = setup_driver()
    for i, company in enumerate(company_names):
        print(f"🔎 [{i+1}/{len(company_names)}] Searching: {company}")
        info = search_bizfile(company, driver)
        print(f"    → {info['status']}: {info['result']}")
        results.append(info)
        # Random sleep to mimic human and avoid anti-bot
        time.sleep(random.uniform(*SLEEP_RANGE))
    driver.quit()
    # Save results
    pd.DataFrame(results).to_csv(RESULTS_CSV, index=False)
    print(f"\n✅ Done! Results saved to {RESULTS_CSV}")

if __name__ == "__main__":
    main()
