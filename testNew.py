import pandas as pd

# Load the two CSV files
file1_path = "florida_hurricane_landfalls.csv"
file2_path = "florida_landfalls_1900.csv"

df1 = pd.read_csv(file1_path)
df2 = pd.read_csv(file2_path)

# Selecting relevant columns for comparison
columns_to_compare = ["Basin", "Date", "Name","Indicator","Time"]

# Finding common rows based on Basin, Date, and Name
common_rows = df1.merge(df2, on=columns_to_compare, how="inner")

# Count of matching rows
matching_count = len(common_rows)
print(f"Matching rows based on {columns_to_compare}: {matching_count}")
matching_count
