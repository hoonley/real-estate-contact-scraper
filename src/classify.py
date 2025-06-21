import pandas as pd

BUSINESS_KEYWORDS = [
    "LLC", "LL" "INC", "CORP", "CO", "COMPANY", "LTD", "LP", "PC", "LLP", "HOLDINGS", "GROUP", "ENTERPRISES"
]

def classify_name(name: str, lender_name: str = "") -> str:
    if pd.isna(name):
        return "unknown"

    name_str = name.strip().lower() if isinstance(name, str) else ""
    lender_str = lender_name.strip().lower() if isinstance(lender_name, str) else ""

    if name_str.endswith("trust") or lender_str.endswith("trust"):
        return "ignored"

    name_upper = name.upper().strip()
    if any(keyword in name_upper for keyword in BUSINESS_KEYWORDS):
        return "company"

    return "individual"


    name_str = name.strip().lower() if isinstance(name, str) else ""
    lender_str = lender_name.strip().lower() if isinstance(lender_name, str) else ""

    # Ignore if either ends with 'trust'
    if name_str.endswith("trust") or lender_str.endswith("trust"):
        return "ignored"

    # Normalize to uppercase for keyword matching
    name_upper = name.upper()
    if any(keyword in name_upper for keyword in BUSINESS_KEYWORDS):
        return "company"

    return "individual"
