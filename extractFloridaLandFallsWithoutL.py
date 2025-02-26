import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
import numpy as np

# 📍 Load Florida shapefile
admin1_shapefile = "ne_10m_admin_1_states_provinces.shp"  # Update path if needed
states = gpd.read_file(admin1_shapefile)
florida_shape = states[states["name"] == "Florida"].geometry.iloc[0]

# Create a buffer around Florida to capture hurricanes near the shore and at borders
florida_buffer = florida_shape.buffer(0.05)  # ~20-mile (32 km) buffer
florida_border = florida_shape.boundary  # Get the state border

def convert_lat_lon(value):
    """ Convert coordinates from strings like '28.0N' or '94.8W' to numeric values. """
    if pd.isna(value) or value is None or value == '':
        return np.nan
    
    value = str(value).strip()
    num_part = float(value[:-1])  
    direction = value[-1]  

    if direction in ["S", "W"]:
        return -num_part  
    return num_part  

def is_border_or_land(latitude, longitude):
    """ Check if a point is on land, within 20 miles of Florida's coast, or at the border. """
    if pd.isna(latitude) or pd.isna(longitude):
        return False

    point = Point(longitude, latitude)
    return (
        florida_shape.contains(point) or  # Land
        florida_buffer.contains(point) or  # Near coast (within buffer)
        florida_border.distance(point) < 0.05  # Close to Florida's border
    )

def calculate_distance(coord1, coord2):
    """ Returns distance in miles between two (lat, lon) coordinates. """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return np.nan  

    return geodesic(coord1, coord2).miles  

def extract_florida_landfalls_without_l(file_path: str):
    """
    Extracts hurricanes that made landfall in Florida **without using the 'L' indicator**.
    Returns the filtered DataFrame.
    """
    # 🔹 Load dataset
    df = pd.read_csv(file_path)

    # ✅ Extract 'Year' from Date column
    df["Year"] = df["Date"].astype(str).str[:4].astype(int)

    # ✅ Filter only hurricanes from 1900 onwards
    df = df[df["Year"] >= 1900].copy()

    # Convert Latitude and Longitude values
    df["Latitude"] = df["Latitude"].apply(convert_lat_lon)
    df["Longitude"] = df["Longitude"].apply(convert_lat_lon)

    # Fix Longitude values > 180
    df["Longitude"] = df["Longitude"].apply(lambda lon: lon - 360 if lon > 180 else lon)

    # Convert Wind Speed & Pressure to Numeric
    df["Max_Wind_Speed"] = pd.to_numeric(df["Max_Wind_Speed"], errors='coerce')
    df["Min_Pressure"] = pd.to_numeric(df["Min_Pressure"], errors='coerce')

    # Detect landfall by checking offshore-to-onshore movement
    df["Prev_Latitude"] = df["Latitude"].shift(1)
    df["Prev_Longitude"] = df["Longitude"].shift(1)
    df["Next_Latitude"] = df["Latitude"].shift(-1)
    df["Next_Longitude"] = df["Longitude"].shift(-1)

    df["Prev_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Prev_Latitude"], row["Prev_Longitude"]), axis=1)
    df["Curr_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Latitude"], row["Longitude"]), axis=1)
    df["Next_Near_Land"] = df.apply(lambda row: is_border_or_land(row["Next_Latitude"], row["Next_Longitude"]), axis=1)

    # Calculate Distance Moved
    df["Prev_Distance"] = df.apply(lambda row: calculate_distance(
        (row["Prev_Latitude"], row["Prev_Longitude"]),
        (row["Latitude"], row["Longitude"])
    ), axis=1)

    df["Next_Distance"] = df.apply(lambda row: calculate_distance(
        (row["Latitude"], row["Longitude"]),
        (row["Next_Latitude"], row["Next_Longitude"])
    ), axis=1)

    # Define landfall criteria
    df["Wind_Drop"] = (df["Max_Wind_Speed"] < df["Max_Wind_Speed"].shift(1) * 0.90)
    df["Pressure_Rise"] = (df["Min_Pressure"] > df["Min_Pressure"].shift(1) + 1.5)

    df["Landfall_Detected"] = (df["Prev_Near_Land"] == False) & (df["Curr_Near_Land"] == True) & (df["Next_Near_Land"] == True) & (
        (df["Prev_Distance"] < 100) | (df["Next_Distance"] < 100)
    )

    print(len(df[df["Landfall_Detected"] == True]))  # Debugging line
    # Keep only the first landfall per hurricane
    df_landfalls = df[df["Landfall_Detected"] == True].drop_duplicates(subset=["Basin", "Date", "Latitude", "Longitude"], keep="first")
    print(len(df_landfalls))  # Debugging line
    return df_landfalls  # Returns filtered DataFrame
s= extract_florida_landfalls_without_l("hurricane_data.csv")
s.to_csv("florida_landfalls_without_using_L_new.csv", index=False)  # Save to CSV