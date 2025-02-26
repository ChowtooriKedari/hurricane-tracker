import csv

# The file downlaoded from https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2023-051124.txt
HURDAT2_FILE = "Hurricanes.txt"

# The output file that will be created and stores all the parsed data
OUTPUT_CSV_FILE = "hurricane_data.csv"

def parse_hurdat2():
    with open(HURDAT2_FILE, "r") as file:
        lines = file.readlines()
    count=0
    parsed_data = []
    current_storm = None

    # Iterate through each line in the file
    for line in lines:

        # Split the line by commas and strip whitespace
        parts = [p.strip() for p in line.split(",")]

        # If the line has 4 parts, it's a new storm
        # As it was mentioned in the https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf
        # The first part is the basin, the second is the name, and the third is the data count, and 
        # the fourth is extra value generated after the value, which is empty

        if len(parts) == 4:
            if current_storm and current_storm["Entries"]:
                parsed_data.extend(current_storm["Entries"])

            current_storm = {
                "Basin": parts[0],
                "Name": parts[1].strip(),
                "Entries": []
            }
        
        # If the line has 8 or more parts, it's an entry for the current storm
        # The format is according to the documentation provided at https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf

        elif len(parts) >= 8 and current_storm:
            count+=1

            # Parse the entry
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
            
            # Append the entry to the current storm's entries
            current_storm["Entries"].append(entry)

    # Append the last storm's entries
    if current_storm and current_storm["Entries"]:
        parsed_data.extend(current_storm["Entries"])
    print(count)

    # Return the parsed data
    return parsed_data


def save_to_csv(parsed_data):

    # Define the fieldnames for the CSV
    fieldnames = [
        "Basin", "Name", "Date", "Time", "Indicator", "Status", "Latitude", "Longitude",
        "Max_Wind_Speed", "Min_Pressure", "34kt_NE", "34kt_SE", "34kt_SW", "34kt_NW",
        "50kt_NE", "50kt_SE", "50kt_SW", "50kt_NW", "64kt_NE", "64kt_SE", "64kt_SW", "64kt_NW",
        "Radius_Max_Wind"
    ]

    # Write the parsed data to a CSV file
    with open(OUTPUT_CSV_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)


if __name__ == "__main__":

    # Parse the HURDAT2 file and save the data to CSV
    parsed_data = parse_hurdat2()

    # Save the parsed data to CSV
    save_to_csv(parsed_data)
