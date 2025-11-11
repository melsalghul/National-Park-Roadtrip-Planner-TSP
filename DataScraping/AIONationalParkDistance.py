# All in one file to create distance matrices
# 1 Input Needed: KML file of locations, longitude, latitude
# 3 Outputs (CSV files): Filtered locations (Name, Longuitude, Latitude), Straight Line Distance Matrix, Drivable Distance Matrix

# Import necessary libraries
import geopandas as gpd
import fiona
import pandas as pd
import geopy
from geopy.distance import geodesic
import sys
import requests
from tqdm import tqdm
import math
import json
import subprocess
import importlib

# Get ParkName, Lonitude, Latitude from KML file and filter for contiguous US parks only
def filterFromKMLtoCSV(kml_file, output_file):
    # Enable KML driver for reading
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

    # Read KML file
    gdf = gpd.read_file(kml_file, driver='KML')

    gdf['longitude'] = gdf.geometry.x
    gdf['latitude'] = gdf.geometry.y

    parks_df = gdf[['Name', 'longitude', 'latitude']]
    parks_df.columns = ['Park Name', 'Longitude', 'Latitude']

    # Filter for contiguous US
    contiguous_mask = (
        (parks_df['Latitude'] >= 24.5) & (parks_df['Latitude'] <= 49.5) &
        (parks_df['Longitude'] >= -125) & (parks_df['Longitude'] <= -66.9)
    )

    parks_df = parks_df[contiguous_mask].reset_index(drop=True)

    # Save to CSV
    parks_df.to_csv(output_file, index=False)
    print(f"Contiguous US parks data saved to {output_file}")


###Create Shortest Distance Matrix while taking into account earth curvature
# Read previous csv output
def createGeodesicDistanceMatrix(input_file, output_file):
    parks_df = pd.read_csv(input_file)

    # Get list of parks
    parks = parks_df['Park Name'].tolist()

    # Initialize an empty DataFrame for the distance matrix
    distance_matrix = pd.DataFrame(index=parks, columns=parks)

    # Fill the matrix
    for i, park_a in enumerate(parks):
        coord_a = (parks_df.loc[i, 'Latitude'], parks_df.loc[i, 'Longitude'])
        for j, park_b in enumerate(parks):
            coord_b = (parks_df.loc[j, 'Latitude'], parks_df.loc[j, 'Longitude'])
            distance = geodesic(coord_a, coord_b).miles 
            distance_matrix.at[park_a, park_b] = round(distance, 2)
        
    distance_matrix.to_csv(output_file)
    print(f"Distance matrix saved to '{output_file}'")


####Create Drivable Distance Matrix using OSRM API

# URL for OSRM table, public server
OSRM_URL = "http://router.project-osrm.org/table/v1/driving/{}?annotations=distance"

METERS_TO_MILES = 1 / 1609.344

# OSRM wants lon,lat, and semicolon separated
def buildOSRMString(df, lon_col='Longitude', lat_col='Latitude'):
    return ";".join([f"{lon},{lat}" for lon, lat in zip(df[lon_col].astype(str), df[lat_col].astype(str))])

def createDrivableDistanceMatrix(input_file, output_file):
    df = pd.read_csv(input_file)
    if df.shape[0] < 2:
        raise Exception("Need at least 2 rows/locations.")

    # Get the Park Names as labels
    if "Park Name" in df.columns:
        labels = df["Park Name"].astype(str).tolist()
    else:
        labels = df.index.astype(str).tolist()

    # Checks number of locations before OSRM request, public server have request limits
    n = len(df)
    if n > 100:
        print(f"Warning: {n} locations detected.")
    
    coord_str = buildOSRMString(df)
    url = OSRM_URL.format(coord_str)

    print(f"Requesting OSRM table for {n} locations...")
    r = requests.get(url, timeout=120)
    if r.status_code != 200:
        print("OSRM request failed:", r.status_code, r.text[:500])
        raise Exception("OSRM request failed. See message above.")

    data = r.json()
    
    # Save raw JSON file
    with open('DataScraping/osrmResponse.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print("Raw OSRM JSON file saved")

    if "distances" not in data:
        print("OSRM response missing 'distances':", data)
        raise Exception("OSRM did not return distances. Possibly too many locations or server limit.")

    distances_m = data["distances"]  # distances in meters
    # Convert meters to miles, and handle null values
    distances_miles = []
    for i, row in enumerate(distances_m):
        newrow = []
        for j, val in enumerate(row):
            if val is None:
                newrow.append(float("nan"))
            else:
                newrow.append(val * METERS_TO_MILES)
        distances_miles.append(newrow)

    # Build DataFrame, the distance matrix of fastest drivable miles between the parks
    df_matrix = pd.DataFrame(distances_miles, index=labels, columns=labels)

    # Save matrix to CSV
    df_matrix.to_csv(output_file, index=True)
    print(f"Saved driving distance matrix to: {output_file} (units: miles)")

# Run Everything
filterFromKMLtoCSV('DataScraping/parkdata.kml', 'DataScraping/contiguousUSParks.csv')
print()
createGeodesicDistanceMatrix('DataScraping/contiguousUSParks.csv', 'DataScraping/geodesicDistanceMatrix.csv')
print()
createDrivableDistanceMatrix('DataScraping/contiguousUSParks.csv', 'DataScraping/drivableDistanceMatrix.csv')
