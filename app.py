import pandas as pd
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

CSV_PATH = 'DataScraping\contiguousUSParks.csv'
TSP_OUTPUT_PATH = 'DataScraping\TSP_Solution_Permutation.txt'
OSRM_ROUTE_URL = "http://router.project-osrm.org/route/v1/driving/{}"


def load_data():
    try:
        return pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        return None


def load_tsp_permutation():
    try:
        with open(TSP_OUTPUT_PATH, 'r') as f:
            txt = f.read().strip()
            nums = [int(x.strip()) for x in txt.split(",")]
            return nums
    except:
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/parks')
def get_parks():
    df = load_data()
    if df is None:
        return jsonify({"error": "CSV not found"}), 500

    parks = df.sort_values("Park Name")[['Park Name', 'Latitude', 'Longitude']].to_dict(orient="records")
    return jsonify(parks)


@app.route('/api/route', methods=['POST'])
def get_route():
    req = request.get_json()
    start_park = req.get('start_park', None)

    df = load_data()
    if df is None:
        return jsonify({"error": "CSV not found"}), 500

    permutation = load_tsp_permutation()
    if permutation is None:
        return jsonify({"error": "TSP permutation file not found"}), 500

    tsp_df = df.iloc[permutation].reset_index(drop=True)

    if start_park:
        if start_park not in tsp_df['Park Name'].values:
            return jsonify({"error": f"{start_park} not found in TSP permutation"}), 400

        start_index = tsp_df.index[tsp_df['Park Name'] == start_park][0]
        tsp_df = pd.concat([tsp_df.iloc[start_index:], tsp_df.iloc[:start_index]]).reset_index(drop=True)

    start_lon = tsp_df.iloc[0]['Longitude']
    start_lat = tsp_df.iloc[0]['Latitude']

    coord_list = [
        f"{row['Longitude']},{row['Latitude']}"
        for _, row in tsp_df.iterrows()
    ]
    coord_list.append(f"{start_lon},{start_lat}")

    coord_string = ";".join(coord_list)

    url = OSRM_ROUTE_URL.format(coord_string) + "?overview=full&geometries=geojson"

    try:
        r = requests.get(url, timeout=25)
        if r.status_code != 200:
            return jsonify({"error": "OSRM API Error"}), 400

        osrm_json = r.json()
        route = osrm_json["routes"][0]

        return jsonify({
            "route_geometry": route["geometry"],
            "waypoints": tsp_df[['Park Name', 'Latitude', 'Longitude']].to_dict(orient="records"),
            "total_distance_miles": round(route["distance"] * 0.000621371, 1),
            "total_duration_hours": round(route["duration"] / 3600, 1),
            "closed_tour": True
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)