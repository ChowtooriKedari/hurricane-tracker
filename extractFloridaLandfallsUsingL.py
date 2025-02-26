import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 📌 Load Florida shapefile
admin1_shapefile = "ne_10m_admin_1_states_provinces.shp"  # Update path
states = gpd.read_file(admin1_shapefile)
florida_shape = states[states["name"] == "Florida"].geometry.iloc[0]

# 📍 Florida Bounding Box (for additional filtering)
FLORIDA_LAT_MIN, FLORIDA_LAT_MAX = 24.5, 31.0
FLORIDA_LON_MIN, FLORIDA_LON_MAX = -87.6, -79.8

def convert_lat_lon(value):
    """ Convert '28.0N' or '94.8W' to numeric values. """
    if pd.isna(value):
        return None  # Handle missing values
    
    value = str(value).strip()
    num_part = float(value[:-1])  # Extract numeric part
    direction = value[-1]  # Extract direction (N/S/E/W)

    if direction == "S" or direction == "W":
        return -num_part  # Convert S & W to negative
    return num_part  # Keep N & E positive

def is_inside_florida(latitude, longitude):
    """ Check if a coordinate is inside Florida's land area or bounding box. """
    if latitude is None or longitude is None:
        return False

    point = Point(longitude, latitude)

    # Check inside Florida shape
    if florida_shape.contains(point):
        return True

    # Check within bounding box
    if (FLORIDA_LAT_MIN <= latitude <= FLORIDA_LAT_MAX) and (FLORIDA_LON_MIN <= longitude <= FLORIDA_LON_MAX):
        return True

    return False

def extract_florida_landfalls(file_path: str):
    """
    Extracts hurricanes that made landfall in Florida using the 'L' indicator.
    Returns the filtered DataFrame.
    """
    # 🔹 Load dataset
    df = pd.read_csv(file_path)

    # 🔹 Extract 'Year' from 'Date' column
    df["Year"] = df["Date"].astype(str).str[:4].astype(int)  # Get first 4 digits as year

    # 🔹 Convert Latitude and Longitude
    df["Latitude"] = df["Latitude"].apply(convert_lat_lon)
    df["Longitude"] = df["Longitude"].apply(convert_lat_lon)

    # 🔹 Fix Longitude values > 180
    df["Longitude"] = df["Longitude"].apply(lambda lon: lon - 360 if lon > 180 else lon)

    # 🔹 Filter hurricanes with 'L' (Landfall Indicator)
    df_landfalls = df[df["Indicator"] == "L"].copy()

    # 🔹 Filter only hurricanes from 1900 onwards
    df_landfalls = df_landfalls[df_landfalls["Year"] >= 1900]

    # 🔹 Check if landfall happened in Florida
    df_landfalls["In_Florida"] = df_landfalls.apply(lambda row: is_inside_florida(row["Latitude"], row["Longitude"]), axis=1)

    # 🔹 Keep only those inside Florida
    df_florida_landfalls = df_landfalls[df_landfalls["In_Florida"] == True]

    return df_florida_landfalls  # Returns filtered DataFrame


# Extract Florida landfalls and save the result to a CSV file
df_florida_landfalls = extract_florida_landfalls("hurricane_data.csv")
df_florida_landfalls.to_csv("florida_landfalls_using_L.csv", index=False)  # Save to CSV