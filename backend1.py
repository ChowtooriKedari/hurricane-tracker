from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
from shapely.geometry import Point

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

HURDAT2_FILE = "Hurricanes.txt"

# Load Florida boundary from shapefile
admin1_shapefile = "ne_10m_admin_1_states_provinces.shp"  # Update with the correct path
states = gpd.read_file(admin1_shapefile)
florida = states[states["name"] == "Florida"]


def is_on_land(latitude, longitude):
    """ Check if a given latitude and longitude is inside Florida. """
    point = Point(longitude, latitude)
    return florida.geometry.contains(point).any()


def parse_hurdat2():
    """ Reads HURDAT2 file and returns parsed storm data. """
    with open(HURDAT2_FILE, "r") as file:
        lines = file.readlines()

    parsed_data = []
    current_storm = None

    for line in lines:
        parts = [p if p != "" else " " for p in line.strip().split(",")]

        if len(parts) == 4:
            if current_storm and current_storm["Entries"]:
                parsed_data.append(current_storm)

            try:
                current_storm = {
                    "Basin": parts[0][:2],
                    "Cyclone_Number": parts[0][2:4],
                    "Year": parts[0][4:8],
                    "Name": parts[1].strip(),
                    "Data_Count": int(parts[2].strip()),
                    "Entries": []
                }
            except ValueError:
                current_storm = None
                continue

        elif len(parts) >= 8 and current_storm:
            try:
                date = parts[0].strip()
                time = parts[1].strip()
                indicator = parts[2].strip()  # Check for "L"
                status = parts[3].strip()

                lat_value = float(parts[4][:-1])
                lat_direction = parts[4][-1]
                lon_value = float(parts[5][:-1])
                lon_direction = parts[5][-1]

                if lon_value > 180:
                    lon_value -= 360

                latitude = lat_value if lat_direction == "N" else -lat_value
                longitude = -lon_value if lon_direction == "W" else lon_value

                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    continue

                max_wind_speed = int(parts[6].strip()) if parts[6].strip().isdigit() else 0
                min_pressure = int(parts[7].strip()) if len(parts) > 7 and parts[7].strip().isdigit() else None

                entry = {
                    "Date": date,
                    "Time": time,
                    "Indicator": indicator,  # "L" for landfall
                    "Status": status,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Max_Wind_Speed": max_wind_speed,
                    "Min_Pressure": min_pressure
                }

                current_storm["Entries"].append(entry)

            except ValueError:
                continue

    if current_storm and current_storm["Entries"]:
        parsed_data.append(current_storm)

    return parsed_data


@app.get("/api/florida-landfalls")
def get_florida_landfalls():
    """ Detect hurricanes that made landfall in Florida using only the 'L' indicator and geographic filtering. """
    parsed_data = parse_hurdat2()
    florida_landfalls = []

    for storm in parsed_data:
        if int(storm["Year"]) >= 1900:
            for entry in storm["Entries"]:
                if entry["Indicator"] == "L" and is_on_land(entry["Latitude"], entry["Longitude"]):  
                    # Only count landfalls in Florida
                    florida_landfalls.append({
                        "Hurricane": storm["Name"],
                        "Year": storm["Year"],
                        "Date": entry["Date"],
                        "Time": entry["Time"],
                        "Latitude": entry["Latitude"],
                        "Longitude": entry["Longitude"],
                        "Max Wind Speed (knots)": entry["Max_Wind_Speed"]
                    })

    print(f"Total Florida Landfalls Found: {len(florida_landfalls)}")
    return florida_landfalls


@app.get("/api/hurricanes")
def get_hurricanes():
    """ Returns all hurricane data. """
    return parse_hurdat2()


if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, timeout_keep_alive=120)
