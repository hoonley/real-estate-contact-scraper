import pandas as pd

# Load Skip Genie results
skipgenie_df = pd.read_csv("output/skip_genie_results.csv")

# Load Buyers List Excel (output file you want to fill)
buyers_list = pd.read_excel("input/buyerList.xlsx")

# Clear all rows except header (if needed)
buyers_list.iloc[1:, :] = ""

# Fill out rows using skipgenie_df
for idx, row in skipgenie_df.iterrows():
    # Row 0 is the header, so start at 1
    excel_row = idx + 1
    buyers_list.at[excel_row, "Company Name"] = row.get("Owner Name", "")
    buyers_list.at[excel_row, "First Name"] = row.get("First Name", "")
    buyers_list.at[excel_row, "Last Name"] = row.get("Last Name", "")
    buyers_list.at[excel_row, "Phone Number"] = row.get("Phone Numbers", "")

# Save the updated Excel
buyers_list.to_excel("Buyers List output (filled).xlsx", index=False)
print("✅ Buyers List updated and saved as: Buyers List output (filled).xlsx")
