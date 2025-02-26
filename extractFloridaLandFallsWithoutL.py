import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.distance import geodesic
import numpy as np

#-----------------------------------------------------------------------------------------------------------
# This script extracts all landfall entries from a CSV file and saves them to a new CSV file.
# This is done without using the 'L' indicator in the HURDAT2 file.
# The script uses the latitude and longitude data, along with the Florida shapefile, to determine landfall.
# -----------------------------------------------------------------------------------------------------------

# Path to the shapefile containing state boundaries
# This shapefile is from Natural Earth (https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/)
# Using this shapefile allows us to accurately determine the boundaries of Florida for geographic calculations
# It is important to ensure that the shapefile is in the same coordinate reference system (CRS) as the latitude and longitude data
# This file helps in identifying whether a hurricane made landfall in Florida
admin1_shapefile = "ne_10m_admin_1_states_provinces.shp"
states = gpd.read_file(admin1_shapefile)
florida_shape = states[states["name"] == "Florida"].geometry.iloc[0]

# The buffer is used to create a zone around the Florida boundary to account for inaccuracies in the data 
# and to ensure that hurricanes that are very close to the border are also considered as landfalls 
# which could be near the border of Florida or near the shoreline
florida_buffer = florida_shape.buffer(0.05)
florida_border = florida_shape.boundary

# Function to convert latitude and longitude from string format to numeric
def convert_lat_lon(value):
    if pd.isna(value) or value is None or value == '':
        return np.nan
    value = str(value).strip()
    num_part = float(value[:-1])
    direction = value[-1]
    # Convert S and W to negative since they represent southern and western hemispheres
    if direction in ["S", "W"]:
        return -num_part
    return num_part

# Function to check if the latitude and longitude are within the Florida boundary or near the border
# The buffer is used to create a zone around the Florida boundary to account for inaccuracies in the data
# and to ensure that hurricanes that are very close to the border are also considered as landfalls
def is_border_or_land(latitude, longitude):
    if pd.isna(latitude) or pd.isna(longitude):
        return False
    
    # 0.05 is the buffer distance in degrees which is approximately 3 miles, 
    # this is a rough estimate
    point = Point(longitude, latitude)
    return (
        florida_shape.contains(point) or
        florida_buffer.contains(point) or
        florida_border.distance(point) < 0.05 
    )

# Function to calculate the distance between two coordinates
def calculate_distance(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan
    return geodesic(coord1, coord2).miles

# Function to extract landfall entries from the dataset
def extract_florida_landfalls_without_l(file_path: str):
    # Load the dataset
    df = pd.read_csv(file_path)

    # Extract 'Year' from 'Date' column and filter only hurricanes from 1900 onwards 
    df["Year"] = df["Date"].astype(str).str[:4].astype(int)
    df = df[df["Year"] >= 1900].copy()

    # Convert Latitude and Longitude values 
    df["Latitude"] = df["Latitude"].apply(convert_lat_lon)
    df["Longitude"] = df["Longitude"].apply(convert_lat_lon)

    # Fix Longitude values > 180 beacause it is in the range of -180 to 180
    df["Longitude"] = df["Longitude"].apply(lambda lon: lon - 360 if lon > 180 else lon)
    df["Max_Wind_Speed"] = pd.to_numeric(df["Max_Wind_Speed"], errors='coerce')
    df["Min_Pressure"] = pd.to_numeric(df["Min_Pressure"], errors='coerce')

    # Create new columns for previous and next entries
    df["Prev_Latitude"] = df["Latitude"].shift(1)
    df["Prev_Longitude"] = df["Longitude"].shift(1)
    df["Next_Latitude"] = df["Latitude"].shift(-1)
    df["Next_Longitude"] = df["Longitude"].shift(-1)

    # Calculate distances and check for landfall conditions
    df["Prev_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Prev_Latitude"], row["Prev_Longitude"]), axis=1)
    df["Curr_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Latitude"], row["Longitude"]), axis=1)
    df["Next_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Next_Latitude"], row["Next_Longitude"]), axis=1)

    # Calculate distances
    df["Prev_Distance"] = df.apply(lambda row: calculate_distance(
        (row["Prev_Latitude"], row["Prev_Longitude"]),
        (row["Latitude"], row["Longitude"])
    ), axis=1)
    df["Next_Distance"] = df.apply(lambda row: calculate_distance(
        (row["Latitude"], row["Longitude"]),
        (row["Next_Latitude"], row["Next_Longitude"])
    ), axis=1)

    # Detect landfall conditions
  
    #------------------------------------------------------------------------------------------------------------
    # These are rough estimates and may not be accurate for all cases
    #------------------------------------------------------------------------------------------------------------
    # Check if the wind speed dropped by more than 10% compared to the previous entry
    # Usally, a significant drop in wind speed can indicate landfall
    
    df["Wind_Drop"] = (df["Max_Wind_Speed"] < df["Max_Wind_Speed"].shift(1) * 0.90)
    
    # Check if the pressure increased by more than 1.5 units compared to the previous entry
    # An increase in pressure can indicate weakening of the storm, which may occur after landfall. 
    df["Pressure_Rise"] = (df["Min_Pressure"] > df["Min_Pressure"].shift(1) + 1.5)
    
    # Detect landfall by checking if the hurricane moved from sea to land and stayed on land
    # The hurricane is considered to have made landfall if:
    # 1. The previous entry was not near land
    # 2. The current entry is near land
    # 3. The next entry is also near land
    # 4. The distance to the previous entry is less than 100 miles
    # 5. The distance to the next entry is less than 100 miles
        # 100 miles is a rough estimate of the distance from the coast to the center of Florida, 
        # I have tested it with mutiple values and 100 helped in detecting landfalls accurately
    df["Landfall_Detected"] = (df["Prev_Near_Land"] == False) & (df["Curr_Near_Land"] == True) & (df["Next_Near_Land"] == True) & (
        (df["Prev_Distance"] < 100) | (df["Next_Distance"] < 100)
    )
    
    # Filter out the detected landfall entries and remove duplicates, by keeping the first occurrence
    # Attributes like "Basin", "Date", "Latitude", and "Longitude" are used to identify duplicates by creating a unique combination
    df_landfalls = df[df["Landfall_Detected"] == True].drop_duplicates(subset=["Basin", "Date", "Latitude", "Longitude"], keep="first")
    
    return df_landfalls

s = extract_florida_landfalls_without_l("hurricane_data.csv")
s.to_csv("florida_landfalls_without_using_L.csv", index=False)
