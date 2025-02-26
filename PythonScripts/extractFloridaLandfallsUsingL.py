import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Path to the shapefile containing state boundaries
# This shapefile is from Natural Earth (https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/)
# Using this shapefile allows us to accurately determine the boundaries of Florida for geographic calculations
# It is important to ensure that the shapefile is in the same coordinate reference system (CRS) as the latitude and longitude data
# This file helps in identifying whether a hurricane made landfall in Florida
admin1_shapefile = "./ne_10m_admin_1_states_provinces.shp"
states = gpd.read_file(admin1_shapefile)

# Extract Florida's polygon from the shapefile
florida_shape = states[states["name"] == "Florida"].geometry.iloc[0]

# Define the bounding box for Florida to filter out hurricanes that are not in Florida
FLORIDA_LAT_MIN, FLORIDA_LAT_MAX = 24.5, 31.0
FLORIDA_LON_MIN, FLORIDA_LON_MAX = -87.6, -79.8

# Function to convert latitude and longitude from string format to numeric
def convert_lat_lon(value):
    if pd.isna(value):
        return None 
    value = str(value).strip()
    num_part = float(value[:-1])
    direction = value[-1]

    # Convert S and W to negative since they represent southern and western hemispheres
    if direction == "S" or direction == "W":
        return -num_part
    return num_part

# Function to check if a hurricane made landfall in Florida
def is_inside_florida(latitude, longitude):
    if latitude is None or longitude is None:
        return False
    
    # Create a point from the latitude and longitude
    point = Point(longitude, latitude)
    if florida_shape.contains(point):
        return True

    # Check if the point is within the bounding box of Florida
    if (FLORIDA_LAT_MIN <= latitude <= FLORIDA_LAT_MAX) and (FLORIDA_LON_MIN <= longitude <= FLORIDA_LON_MAX):
        return True

    return False

def extract_florida_landfalls(file_path: str):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Extract 'Year' from 'Date' column
    df["Year"] = df["Date"].astype(str).str[:4].astype(int)

    # Convert Latitude and Longitude values
    df["Latitude"] = df["Latitude"].apply(convert_lat_lon)
    df["Longitude"] = df["Longitude"].apply(convert_lat_lon)
    # Fix Longitude values > 180 beacause it is in the range of -180 to 180
    df["Longitude"] = df["Longitude"].apply(lambda lon: lon - 360 if lon > 180 else lon)

    # Filter only hurricanes with 'L' indicator (landfall)
    df_landfalls = df[df["Indicator"] == "L"].copy()

    # Filter only hurricanes from 1900 onwards
    df_landfalls = df_landfalls[df_landfalls["Year"] >= 1900]

    # Check if the hurricane made landfall in Florida
    df_landfalls["In_Florida"] = df_landfalls.apply(lambda row: is_inside_florida(row["Latitude"], row["Longitude"]), axis=1)

    # Filter only hurricanes that made landfall in Florida
    df_florida_landfalls = df_landfalls[df_landfalls["In_Florida"] == True]
    return df_florida_landfalls

df_florida_landfalls = extract_florida_landfalls("PythonScripts/hurricane_data.csv")
df_florida_landfalls.to_csv("PythonScripts/florida_landfalls_using_L.csv", index=False)  # Save to CSV