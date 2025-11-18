import pandas as pd
import requests
import json
from flask import Flask, render_template, jsonify, request
from geopy.distance import geodesic

app = Flask(__name__)

CSV_PATH = 'DataScraping/contiguousUSParks.csv'
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{}"

def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        return df
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parks')
def get_parks():
    """Returns list of parks for the dropdown."""
    df = load_data()
    if df is None:
        return jsonify({"error": "CSV not found. Run AIONationalParkDistance.py first."}), 500

    parks = df.sort_values('Park Name')[['Park Name', 'Latitude', 'Longitude']].to_dict(orient='records')
    return jsonify(parks)

@app.route('/api/route', methods=['POST'])
def get_route():
    """
    Calculates a Nearest Neighbor route starting from the selected park.
    Limits to 10 stops to prevent Public OSRM API timeouts/bans.
    """
    data = request.json
    start_park_name = data.get('start_park')
    
    df = load_data()
    if df is None:
        return jsonify({"error": "Data not found"}), 500

    start_node = df[df['Park Name'] == start_park_name]
    if start_node.empty:
        return jsonify({"error": "Park not found"}), 404

    route_indices = [start_node.index[0]]
    visited_indices = set(route_indices)
    current_idx = start_node.index[0]

    STOPS_LIMIT = 10 
    
    while len(route_indices) < STOPS_LIMIT and len(route_indices) < len(df):
        current_loc = (df.loc[current_idx, 'Latitude'], df.loc[current_idx, 'Longitude'])
        nearest_dist = float('inf')
        nearest_idx = -1

        for idx, row in df.iterrows():
            if idx not in visited_indices:
                target_loc = (row['Latitude'], row['Longitude'])
                dist = geodesic(current_loc, target_loc).miles
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_idx = idx
        
        if nearest_idx != -1:
            visited_indices.add(nearest_idx)
            route_indices.append(nearest_idx)
            current_idx = nearest_idx
        else:
            break

    ordered_points = df.loc[route_indices]
    coordinates = []
    for _, row in ordered_points.iterrows():
        coordinates.append(f"{row['Longitude']},{row['Latitude']}")
    
    coord_string = ";".join(coordinates)
    
    url = OSRM_ROUTE_URL.format(coord_string) + "?overview=full&geometries=geojson"
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return jsonify({"error": "OSRM API Error"}), 400
        
        osrm_data = r.json()
        
        return jsonify({
            "route_geometry": osrm_data['routes'][0]['geometry'],
            "waypoints": ordered_points[['Park Name', 'Latitude', 'Longitude']].to_dict(orient='records'),
            "total_distance_miles": round(osrm_data['routes'][0]['distance'] * 0.000621371, 1),
            "total_duration_hours": round(osrm_data['routes'][0]['duration'] / 3600, 1)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)