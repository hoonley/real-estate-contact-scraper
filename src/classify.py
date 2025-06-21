import pandas as pd

# Expanded list with your recent addition "LL"
BUSINESS_KEYWORDS = [
    "LLC", "LL", "INC", "CORP", "CO", "COMPANY", "LTD", "LP", "PC",
    "LLP", "HOLDINGS", "GROUP", "ENTERPRISES"
]

def classify_name(name: str, lender_name: str = "") -> str:
    """
    Classifies an owner name as 'company', 'individual', 'ignored', or 'unknown'.
    Ignores rows where either the lender name OR owner name ends with 'trust' (case-insensitive).
    Matching to company is case-insensitive and trims whitespace.
    """
    # Handle missing owner name
    if pd.isna(name):
        return "unknown"

    # Normalize and strip whitespace for both fields
    name_str = name.strip().lower() if isinstance(name, str) else ""
    lender_str = lender_name.strip().lower() if isinstance(lender_name, str) else ""

    # Ignore if owner name or lender name ends with 'trust'
    if name_str.endswith("trust") or lender_str.endswith("trust"):
        return "ignored"

    # Check for business keywords (case-insensitive, trims whitespace)
    name_upper = name.strip().upper()
    if any(keyword in name_upper for keyword in BUSINESS_KEYWORDS):
        return "company"

    # Otherwise, it's likely an individual
    return "individual"
