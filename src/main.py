import os
import pandas as pd
from classify import classify_name
#from scraper_bizfile import run_scraper

INPUT_FILE = "input/sample.csv"
CLASSIFIED_OUTPUT = "output/sample.csv"

def load_and_classify(filepath=INPUT_FILE):
    """
    Loads the CSV file, skips metadata rows, classifies owner types.
    """
    # Load CSV, skip first metadata row
    df = pd.read_csv(filepath, skiprows=1)
    df.columns = df.iloc[0]  # Use the second row as header
    df = df[1:].reset_index(drop=True)

    # Apply classification to each row
    df["Owner Type"] = df.apply(
        lambda row: classify_name(row["Owner Name"], row["Lender Name"]),
        axis=1
    )

    return df

def main():
    print("📂 Loading and classifying data...")
    df = load_and_classify()

    os.makedirs("output", exist_ok=True)
    df.to_csv(CLASSIFIED_OUTPUT, index=False)
    print(f"✅ Saved classified data to {CLASSIFIED_OUTPUT}")

    # Filter out companies only
    company_df = df[df["Owner Type"] == "company"]
    company_names = company_df["Owner Name"].dropna().unique()

    print(f"🔍 Starting scraper for {len(company_names)} company names...")
    #run_scraper(company_names)
    print("🎉 Scraping complete!")

if __name__ == "__main__":
    main()
