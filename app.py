import pandas as pd
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

CSV_PATH = 'DataScraping/contiguousUSParks.csv'
TSP_OUTPUT_PATH = 'DataScraping/tsp_result.txt'
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{}"

def load_data():
    """Load the park CSV containing names + coordinates."""
    try:
        return pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        return None

def load_tsp_route():
    """Read the TSP solver output listing park names in optimal order."""
    try:
        with open(TSP_OUTPUT_PATH, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/parks')
def get_parks():
    """Return list of parks for frontend dropdown."""
    df = load_data()
    if df is None:
        return jsonify({"error": "CSV not found. Run data acquisition first."}), 500
    
    parks = df.sort_values('Park Name')[['Park Name', 'Latitude', 'Longitude']] \
              .to_dict(orient='records')
    return jsonify(parks)


@app.route('/api/route', methods=['POST'])
def get_route():
    """Return the optimized TSP route + mapped OSRM route."""
    
    df = load_data()
    if df is None:
        return jsonify({"error": "CSV not found"}), 500

    tsp_route = load_tsp_route()
    if tsp_route is None:
        return jsonify({"error": "TSP output file tsp_result.txt not found"}), 500

    ordered_points = []
    for park_name in tsp_route:
        match = df[df['Park Name'] == park_name]
        if match.empty:
            return jsonify({"error": f"Park not found in CSV: {park_name}"}), 500
        ordered_points.append(match.iloc[0])

    ordered_df = pd.DataFrame(ordered_points)

    coordinates = [
        f"{row['Longitude']},{row['Latitude']}"
        for _, row in ordered_df.iterrows()
    ]

    start_coord = coordinates[0]
    coordinates.append(start_coord)

    coord_string = ";".join(coordinates)

    url = OSRM_ROUTE_URL.format(coord_string) + "?overview=full&geometries=geojson"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return jsonify({"error": "OSRM API Error"}), 400

        osrm_data = r.json()

        return jsonify({
            "route_geometry": osrm_data['routes'][0]['geometry'],
            "waypoints": ordered_df[['Park Name', 'Latitude', 'Longitude']].to_dict(orient='records'),
            "total_distance_miles": round(osrm_data['routes'][0]['distance'] * 0.000621371, 1),
            "total_duration_hours": round(osrm_data['routes'][0]['duration'] / 3600, 1),
            "closed_tour": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)