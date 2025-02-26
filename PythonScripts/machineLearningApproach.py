import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
file_path = "PythonScripts/hurricane_data.csv"
df = pd.read_csv(file_path)

# Load Florida shapefile
admin1_shapefile = "./ne_10m_admin_1_states_provinces.shp"
states = gpd.read_file(admin1_shapefile)
florida_shape = states[states["name"] == "Florida"].geometry.iloc[0]

# Define Florida bounding box for additional filtering
FLORIDA_LAT_MIN, FLORIDA_LAT_MAX = 24.5, 31.0
FLORIDA_LON_MIN, FLORIDA_LON_MAX = -87.6, -79.8

def convert_lat_lon(value):
    """ Convert '28.0N' or '94.8W' to numeric values. """
    if pd.isna(value):
        return None
    
    value = str(value).strip()
    # Extract numeric part
    num_part = float(value[:-1])
    # Extract direction (N/S/E/W)
    direction = value[-1]

    if direction == "S" or direction == "W":
        return -num_part
    return num_part

def is_inside_florida(latitude, longitude):
    """ Check if a coordinate is inside Florida's land area or bounding box. """
    if latitude is None or longitude is None:
        return False

    point = Point(longitude, latitude)

    # Check inside Florida shape or within bounding box
    return florida_shape.contains(point) or (
        FLORIDA_LAT_MIN <= latitude <= FLORIDA_LAT_MAX and 
        FLORIDA_LON_MIN <= longitude <= FLORIDA_LON_MAX
    )

# Extract 'Year' from 'Date' column
df["Year"] = df["Date"].astype(str).str[:4].astype(int)

# Filter only hurricanes from 1900 onwards
df = df[df["Year"] >= 1900].copy()

# Convert Latitude and Longitude values
df["Latitude"] = df["Latitude"].apply(convert_lat_lon)
df["Longitude"] = df["Longitude"].apply(convert_lat_lon)

# Fix Longitude values > 180
df["Longitude"] = df["Longitude"].apply(lambda lon: lon - 360 if lon > 180 else lon)

# Convert Wind Speed & Pressure to Numeric
df["Max_Wind_Speed"] = pd.to_numeric(df["Max_Wind_Speed"], errors='coerce')
df["Min_Pressure"] = pd.to_numeric(df["Min_Pressure"], errors='coerce')

# Filter only hurricanes with 'L' indicator (landfall)
df["Landfall"] = df["Indicator"] == "L"

# Filter hurricanes that made landfall in Florida
df["In_Florida"] = df.apply(lambda row: is_inside_florida(row["Latitude"], row["Longitude"]), axis=1)
df = df[df["In_Florida"] == True].copy()

# Selecting Features and Target
features = ["Latitude", "Longitude", "Max_Wind_Speed", "Min_Pressure"]
df = df.dropna(subset=features + ["Landfall"])  # Drop rows with missing values
X = df[features]
y = df["Landfall"].astype(int)  # Convert boolean to integer for classification

# Split dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest Classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Predictions and Evaluation
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)

# Save the predictions to a CSV file
df["Predicted_Landfall"] = clf.predict(X)
output_file_path = "PythonScripts/florida_hurricane_predictions.csv"
df[df["Predicted_Landfall"] == 1].to_csv(output_file_path, index=False)

# Return the results
output_file_path, accuracy, classification_rep
