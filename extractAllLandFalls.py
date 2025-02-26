#--------------------------------------------------------------------------------------------
# This script extracts all landfall entries from a CSV file and saves them to a new CSV file.
# --------------------------------------------------------------------------------------------

import pandas as pd

INPUT_CSV_FILE = "hurricane_data.csv"
OUTPUT_LANDFALLS_CSV = "allLandfalls.csv"

def filter_landfall_entries():
    df = pd.read_csv(INPUT_CSV_FILE)
    landfall_df = df[df["Indicator"] == "L"]
    landfall_df.to_csv(OUTPUT_LANDFALLS_CSV, index=False)

    print(f"Landfall data successfully saved to {OUTPUT_LANDFALLS_CSV}")

if __name__ == "__main__":
    filter_landfall_entries()
