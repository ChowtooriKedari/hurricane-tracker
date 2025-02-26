import pandas as pd

INPUT_CSV_FILE = "hurricane_data.csv"
OUTPUT_LANDFALLS_CSV = "allLandfalls.csv"

def filter_landfall_entries():
    """ Reads the hurricane CSV and extracts only entries where 'Indicator' is 'L'."""
    
    # Load the CSV file
    df = pd.read_csv(INPUT_CSV_FILE)

    # Filter rows where 'Indicator' is 'L'
    landfall_df = df[df["Indicator"] == "L"]

    # Save to a new CSV file
    landfall_df.to_csv(OUTPUT_LANDFALLS_CSV, index=False)

    print(f"✅ Landfall data successfully saved to {OUTPUT_LANDFALLS_CSV}")

if __name__ == "__main__":
    filter_landfall_entries()
