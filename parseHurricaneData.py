import csv

HURDAT2_FILE = "Hurricanes.txt"
OUTPUT_CSV_FILE = "hurricane_data.csv"

def parse_hurdat2():
    """ Parses the HURDAT2 file and saves all hurricane data as-is to a CSV file. """
    with open(HURDAT2_FILE, "r") as file:
        lines = file.readlines()
    count=0
    parsed_data = []
    current_storm = None

    for line in lines:
        parts = [p.strip() for p in line.split(",")]  # Split by commas and remove spaces

        # If it's a header line (storm metadata)
        if len(parts) == 4:
            if current_storm and current_storm["Entries"]:
                parsed_data.extend(current_storm["Entries"])  # Store previous storm's entries

            current_storm = {
                "Basin": parts[0],  # Full Basin Code (e.g., AL031851)
                "Name": parts[1].strip(),
                "Entries": []
            }

        # If it's a data entry (storm track record)
        elif len(parts) >= 8 and current_storm:
            count+=1
            entry = {
                "Basin": current_storm["Basin"],
                "Name": current_storm["Name"],
                "Date": parts[0].strip(),
                "Time": parts[1].strip(),
                "Indicator": parts[2].strip() if parts[2].strip() else None,
                "Status": parts[3].strip(),
                "Latitude": parts[4].strip(),
                "Longitude": parts[5].strip(),
                "Max_Wind_Speed": parts[6].strip(),
                "Min_Pressure": parts[7].strip() if len(parts) > 7 else None,
                "34kt_NE": parts[8].strip() if len(parts) > 8 else None,
                "34kt_SE": parts[9].strip() if len(parts) > 9 else None,
                "34kt_SW": parts[10].strip() if len(parts) > 10 else None,
                "34kt_NW": parts[11].strip() if len(parts) > 11 else None,
                "50kt_NE": parts[12].strip() if len(parts) > 12 else None,
                "50kt_SE": parts[13].strip() if len(parts) > 13 else None,
                "50kt_SW": parts[14].strip() if len(parts) > 14 else None,
                "50kt_NW": parts[15].strip() if len(parts) > 15 else None,
                "64kt_NE": parts[16].strip() if len(parts) > 16 else None,
                "64kt_SE": parts[17].strip() if len(parts) > 17 else None,
                "64kt_SW": parts[18].strip() if len(parts) > 18 else None,
                "64kt_NW": parts[19].strip() if len(parts) > 19 else None,
                "Radius_Max_Wind": parts[20].strip() if len(parts) > 20 else None,
            }

            current_storm["Entries"].append(entry)

    # Save remaining storm data
    if current_storm and current_storm["Entries"]:
        parsed_data.extend(current_storm["Entries"])
    print(count)
    return parsed_data


def save_to_csv(parsed_data):
    """ Saves the parsed hurricane data to a CSV file. """
    fieldnames = [
        "Basin", "Name", "Date", "Time", "Indicator", "Status", "Latitude", "Longitude",
        "Max_Wind_Speed", "Min_Pressure", "34kt_NE", "34kt_SE", "34kt_SW", "34kt_NW",
        "50kt_NE", "50kt_SE", "50kt_SW", "50kt_NW", "64kt_NE", "64kt_SE", "64kt_SW", "64kt_NW",
        "Radius_Max_Wind"
    ]

    with open(OUTPUT_CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)


if __name__ == "__main__":
    parsed_data = parse_hurdat2()
    save_to_csv(parsed_data)
