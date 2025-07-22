import pandas as pd
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

# ===== CONFIG =====
SCRAPERAPI_KEY = "063ec9ed7a89a258b8781370c63d951e"
COMPANY_CSV = "output/sample_output4.csv"
RESULTS_CSV = "output/bizfile_results.csv"
SEARCH_URL = "https://bizfileonline.sos.ca.gov/search/business"
SEARCH_WAIT = 3
SLEEP_RANGE = (8, 15)

# ===== DATA LOAD =====
df = pd.read_csv(COMPANY_CSV)
company_rows = df[df["Owner Type"] == "company"].copy()
company_names = company_rows["Owner Name"].dropna().unique()

# ===== SCRAPERAPI HTTP FALLBACK =====
def scraperapi_search(company_name):
    from urllib.parse import quote_plus
    search_url = f"https://bizfileonline.sos.ca.gov/search/business?SearchType=CORP&SearchCriteria={quote_plus(company_name)}"
    payload = {
        'api_key': SCRAPERAPI_KEY,
        'url': search_url,
        'render': 'true'
    }
    try:
        response = requests.get('https://api.scraperapi.com/', params=payload, timeout=60)
        return response.text
    except Exception as e:
        return f"ScraperAPI failed: {e}"

# ===== SELENIUM SETUP =====
def setup_driver():
    # WARNING: ScraperAPI's proxy is for HTTP requests, not really meant for browser/Selenium traffic.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    # You may want to comment out proxy unless using your own proxy server.
    # chrome_options.add_argument('--proxy-server=http://scraperapi.proxy:8001')
    return webdriver.Chrome(options=chrome_options)

# ===== MAIN SEARCH FUNCTION =====
def search_bizfile(company_name, driver):
    # Try Selenium first
    try:
        driver.get(SEARCH_URL)
        time.sleep(SEARCH_WAIT)
        input_box = driver.find_element(By.CSS_SELECTOR, "input#businessSearch")
        input_box.clear()
        input_box.send_keys(company_name)
        search_btn = driver.find_element(By.CSS_SELECTOR, "button#search")
        search_btn.click()
        time.sleep(SEARCH_WAIT + 2)
        try:
            result_elem = driver.find_element(By.CSS_SELECTOR, ".resultItem .businessName")
            result_text = result_elem.text
            return {"company": company_name, "result": result_text, "status": "OK", "method": "selenium"}
        except Exception:
            return {"company": company_name, "result": "", "status": "No result (Selenium)", "method": "selenium"}
    except Exception as e:
        # Selenium failed, fallback to ScraperAPI HTTP request
        html = scraperapi_search(company_name)
        return {"company": company_name, "result": html[:200], "status": f"Selenium Error: {e}", "method": "scraperapi"}

# ===== MAIN LOOP =====
def main():
    results = []
    driver = setup_driver()
    try:
        for i, company in enumerate(company_names):
            print(f"🔎 [{i+1}/{len(company_names)}] Searching: {company}")
            info = search_bizfile(company, driver)
            print(f"    → {info['status']} (via {info['method']})")
            results.append(info)
            time.sleep(random.uniform(*SLEEP_RANGE))
    finally:
        driver.quit()
        pd.DataFrame(results).to_csv(RESULTS_CSV, index=False)
        print(f"\n✅ Done! Results saved to {RESULTS_CSV}")

if __name__ == "__main__":
    main()
