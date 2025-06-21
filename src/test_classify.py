from classify import classify_name

# List of test cases: (Owner Name, Lender Name, Expected Output)
test_cases = [
    ("SARISSA ENTS INC", "", "company"),
    ("REELAND INVESTMENTS", "", "company"),
    ("WESTCLIFF REALTY PARTNERS", "", "company"),
    ("BICH VENTURES", "", "company"),
    ("OCHOA MARIA", "", "individual"),
    ("ASLANYAN AZNIV", "", "individual"),
    ("WESTERN PRO BUILDERS", "", "company"),
    ("365HAUS INC", "", "company"),
    ("SUNSET PROPERTIES LLC", "", "company"),
    ("B & J CAP GRP INVS", "", "company"),
    ("SANGES CRISTINA", "", "individual"),
    ("TRUSTY TRUST", "", "ignored"),
    ("", "", "unknown"),
    ("SANTA MONICA HOMES", "", "company"),
    ("JOHN DOE", "", "individual"),
    ("ANY COMPANY TRUST", "", "ignored"),
    ("ANY PERSON", "REALTY TRUST", "ignored"),
]

print("Testing classify_name()...")
for owner_name, lender_name, expected in test_cases:
    result = classify_name(owner_name, lender_name)
    print(f"{owner_name!r:30} | {lender_name!r:20} => {result!r} (expected: {expected!r}) {'✔' if result == expected else '❌'}")
