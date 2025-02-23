from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (frontend)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

HURDAT2_FILE = "Hurricanes.txt"

FLORIDA_LAT_MIN, FLORIDA_LAT_MAX = 24.5, 31.0
FLORIDA_LON_MIN, FLORIDA_LON_MAX = -87.6, -79.8


def parse_hurdat2():
    """ Reads HURDAT2 file and returns parsed storm data. """
    with open(HURDAT2_FILE, "r") as file:
        lines = file.readlines()

    parsed_data = []
    current_storm = None

    for line in lines:
        parts = [p.strip() for p in line.strip().split(",") if p.strip()]

        # Header line (storm metadata)
        if len(parts) == 3:
            if current_storm and current_storm["Entries"]:
                parsed_data.append(current_storm)

            try:
                current_storm = {
                    "Basin": parts[0][:2],
                    "Cyclone_Number": parts[0][2:4],
                    "Year": parts[0][4:8],
                    "Name": parts[1],
                    "Data_Count": int(parts[2]),
                    "Entries": []
                }
            except ValueError:
                continue  # Skip malformed headers

        # Data entry (storm track records)
        elif len(parts) >= 8 and current_storm:
            try:
                lat_str, lon_str = parts[4], parts[5]

                if not lat_str or not lon_str:
                    continue

                lat = float(lat_str[:-1]) * (1 if "N" in lat_str else -1)
                lon = float(lon_str[:-1]) * (-1 if "W" in lon_str else 1)

                entry = {
                    "Date": parts[0],
                    "Time": parts[1],
                    "Indicator": parts[2],  # 'L' means landfall
                    "Status": parts[3],
                    "Latitude": lat,
                    "Longitude": lon,
                    "Max_Wind_Speed": int(parts[6]) if parts[6].isdigit() else 0
                }

                current_storm["Entries"].append(entry)
            except ValueError:
                continue  # Skip invalid data

    if current_storm and current_storm["Entries"]:
        parsed_data.append(current_storm)

    return parsed_data


@app.get("/api/hurricanes")
def get_hurricanes():
    """ Returns all hurricane data. """
    return parse_hurdat2()


@app.get("/api/florida-landfalls")
def get_florida_landfalls():
    """ Returns hurricanes that made landfall in Florida since 1900. """
    parsed_data = parse_hurdat2()
    florida_landfalls = []

    for storm in parsed_data:
        if int(storm["Year"]) >= 1900:  # Ensure year is 1900 or later
            for entry in storm["Entries"]:
                if (
                    FLORIDA_LAT_MIN <= entry["Latitude"] <= FLORIDA_LAT_MAX
                    and FLORIDA_LON_MIN <= entry["Longitude"] <= FLORIDA_LON_MAX
                    and entry["Indicator"] == "L"
                ):
                    florida_landfalls.append({
                        "Hurricane": storm["Name"],
                        "Year": storm["Year"],
                        "Date": entry["Date"],
                        "Time": entry["Time"],
                        "Latitude": entry["Latitude"],
                        "Longitude": entry["Longitude"],
                        "Max Wind Speed (knots)": entry["Max_Wind_Speed"]
                    })

    return florida_landfalls

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, timeout_keep_alive=120)
