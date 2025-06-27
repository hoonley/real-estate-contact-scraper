import pandas as pd
from classify import classify_name, split_owner_names

INPUT_FILE = "input/sample.csv"
OUTPUT_FILE = "output/sample_output5.csv"

def main():
    # Step 1: Load and clean CSV
    df = pd.read_csv(INPUT_FILE, skiprows=1)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # Step 2: Strip whitespace from relevant fields
    df["Owner Name"] = df["Owner Name"].astype(str).str.strip()
    df["Lender Name"] = df["Lender Name"].astype(str).str.strip()

    # Step 3: Split owners by '/' into separate rows
    df = split_owner_names(df)

    # Step 4: Classify each owner
    df["Owner Type"] = df.apply(
        lambda row: classify_name(row["Owner Name"], row["Lender Name"]), axis=1
    )

    # Step 5: Save the new DataFrame
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Done! Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
