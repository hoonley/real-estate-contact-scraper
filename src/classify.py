import pandas as pd

BUSINESS_KEYWORDS = [
    "LLC", "LL", "INC", "CORP", "CO", "COMPANY", "LTD", "LP", "PC",
    "LLP", "HOLDINGS", "GROUP", "ENTERPRISES", "INVESTMENTS", "VENTURES",
    "PROPERTIES", "REALTY", "ESTATE", "CAP", "HOMES", "BUILDERS", "DEVELOPMENT", "TRUST"
]

def classify_name(name: str, lender_name: str = "") -> str:
    if pd.isna(name):
        return "unknown"

    name_str = name.strip().lower() if isinstance(name, str) else ""
    lender_str = lender_name.strip().lower() if isinstance(lender_name, str) else ""

    if name_str.endswith("trust") or lender_str.endswith("trust"):
        return "ignored"

    name_upper = name.strip().upper()
    if any(keyword in name_upper for keyword in BUSINESS_KEYWORDS):
        return "company"
    return "individual"

def split_owner_names(df):
    """
    Splits rows with multiple owners separated by '/' into separate rows.
    Copies all other columns for each split owner.
    """
    rows = []
    for _, row in df.iterrows():
        owner_names = [n.strip() for n in str(row['Owner Name']).split('/') if n.strip()]
        for owner in owner_names:
            new_row = row.copy()
            new_row['Owner Name'] = owner
            rows.append(new_row)
    return pd.DataFrame(rows).reset_index(drop=True)
