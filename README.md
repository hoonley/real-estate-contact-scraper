# Real Estate Owner Contact Enrichment Scraper

This is a Python-based automation tool for enriching real estate lead data. Starting from a spreadsheet of owner/property information, the tool identifies whether each owner is a company or individual, extracts company officer names, and searches public people databases to retrieve phone numbers, emails, and addresses.

---

## 📌 Project Overview

**Input**:  
Excel spreadsheet containing:
- Lender Name
- Owner Name(s)
- Property Address, City, Zip Code

**Output**:  
New Excel spreadsheet with:
- Company Name
- First and Last Name (for individuals)
- Phone Numbers (from FastPeopleSearch, Skip Genie)
- Email Address (if found)
- Mailing Address
- Previous Flip Address (from input)

---

## 🔁 Workflow Steps

1. **Load Owner Data**
   - Read Excel input file
   - Determine if each owner is a person or a company

2. **Search Business Registry**
   - For companies, search [bizfileonline.sos.ca.gov](https://bizfileonline.sos.ca.gov/search/business)
   - Download most recent Statement of Information (PDF)

3. **Parse Statement of Info**
   - Extract `Manager or Member Name` and `CEO Name` from PDF

4. **Look Up Contacts**
   - Search extracted names on:
     - [FastPeopleSearch.com](https://www.fastpeoplesearch.com)
     - Skip Genie (requires login/API access)
   - Collect all phone numbers, mailing addresses, and emails (if present)

5. **Save Output**
   - Format and write enriched data into a new Excel file

---

## 📁 Project Structure

