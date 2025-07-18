# Real Estate Owner Contact Enrichment Scraper

Python automation suite for **real estate contact enrichment and lead list creation**.  
This tool processes spreadsheets of property records, classifies owner type, scrapes business registries for officer names, and automates phone number lookup via Skip Genie and other sources. Outputs a buyer-ready Excel or CSV file.

---

##  Project Overview

**Input:**  
CSV/Excel file containing, at minimum:
- **Lender Name**
- **Owner Name(s)**
- **Property Address, City, Zip Code**

**Output:**  
Formatted Excel (or CSV) file with columns for:
- **Company Name** (if applicable)
- **First Name / Last Name** (if individual)
- **Phone Numbers** (all found)
- **Mailing Address** (if found)
- **Previous Flip Address** (if included in input)
- **Email Address** (if found)

---

##  Workflow Steps

1. **Data Import and Preparation**
   - Reads raw owner/property info from CSV (recommended for input compatibility).
   - Classifies each row as "company" or "individual" using business keywords (case-insensitive) and exclusion of “TRUST”/“trust” endings.
   - Splits multi-owner entries (with `/`) into separate rows.
   - For companies, flags for further officer name extraction.

2. **Company/Individual Parsing**
   - For companies: prepares for later search on [bizfileonline.sos.ca.gov](https://bizfileonline.sos.ca.gov/search/business) to extract officer/manager names.
   - For individuals: splits owner name into first and last names (with support for reversed formats as needed).

3. **Automated Contact Lookup**
   - For every individual:
     - Opens Skip Genie search page using Selenium.
     - Auto-fills owner name, address, and zip code.
     - Uses PyAutoGUI to click confirmation (“Yes, Execute Search”) for popups.
     - Scrapes all “Possible Phone Numbers” (and types) from the results page, storing them in a single column (comma-separated).
     - *(Future: Includes logic for other sources, e.g., FastPeopleSearch.)*

4. **Output Generation**
   - Consolidates all enriched contact info into a single output file (CSV or Excel).
   - Populates company/first/last name, phone number(s), and any other available details.

5. **Buyers List Integration**
   - Optionally, fills out a pre-formatted “Buyers List” Excel sheet using results from `skip_genie_results.csv`.

---

## ⚙️ Key Technologies & Features

- **Python** for all automation logic
- **Pandas** for fast data manipulation and file I/O
- **Selenium** for browser automation and form filling
- **PyAutoGUI** for UI automation (confirmation popups, clicks not handled by Selenium)
- **Excel/CSV Integration** for input and output flexibility
- **Robust error handling and rate limiting** to avoid lockouts and ensure reliability

---

##  How to Use

1. **Prepare your CSV input file** in the `input/` folder (see template in repo).
2. **Run the main processing scripts** in order:
    - `main.py`: Cleans, classifies, and splits owner records, producing `owners_split_classified.csv`.
    - `scraper_skipgenie.py`: Automates Skip Genie lookups for all individuals, scraping phone numbers into `skip_genie_results.csv`.
      - _Manual login to Skip Genie is required before scraping proceeds. Make sure your browser window does not move during automation._
    - `fill_buyers_list.py`: Fills out the “Buyers List” Excel sheet using the phone numbers and owner details from `skip_genie_results.csv`.
3. **Review and use the final buyers list output.**

---

