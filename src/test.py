import pandas as pd 

#ignores the first row since it contains county info
df = pd.read_csv("input/sample.csv", skiprows = 1)

#use second row as header
df.columns = df.iloc[0]
df = df[1:].reset_index(drop = True)

# List of business keywords to check (case-insensitive)
BUSINESS_KEYWORDS = [
    "LLC", "INC", "CORP", "CO", "COMPANY", "LTD", "LP", "PC", "LLP", "HOLDINGS", "GROUP", "ENTERPRISES"
]

def classify_name(name: str, lender_name: str = "") -> str:
    if pd.isna(name):
        return "unknown"
    
    # If lender name ends with TRUST (case-insensitive), ignore the row
    if isinstance(lender_name, str) and lender_name.strip().lower().endswith("trust"):
        return "ignored"

    # Normalize name to uppercase for matching
    name_upper = name.upper()

    # Check if any business keyword is in the name
    if any(keyword in name_upper for keyword in BUSINESS_KEYWORDS):
        return "company"
    
    return "individual"

# adds owner type column
df["Owner Type"] = df.apply(lambda row: classify_name(row["Owner Name"], row["Lender Name"]), axis=1)
