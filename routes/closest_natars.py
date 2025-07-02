import requests
from flask import Blueprint, jsonify, current_app


from .arcgis import generate_token
from settings import ArcgisSettings, Collections


closest_natars_bp = Blueprint('closest_natars', __name__)

def query_features(layer_name, token):
    url = f'{ArcgisSettings.LAYER_SERVER_URL}/{layer_name}/query'
    params = {
        'where': '1=1',
        'outFields': '*',
        'f': 'json',
        'token': token,
        'returnGeometry': True
    }
    response = requests.get(url, params=params, verify=False)
    response.raise_for_status()
    data = response.json()
    
    if 'error' in data:
        raise Exception(f"ArcGIS error: {data['error']['message']} (code {data['error']['code']})")

    return data['features']

def get_distance_two_points(x_lat, y_lat, x_long, y_long):
    return abs(x_lat - y_lat) + abs(x_long - y_long)

def create_table(buildings, natars):
    result_table = []

    for building in buildings:
        b_id = building['attributes']['OBJECTID']
        b_lat = building['attributes']['LAT']
        b_long = building['attributes']['LONG']

        # Compute distances
        distances = []
        for natar in natars:
            n_id = natar['attributes']['OBJECTID']
            n_lat = natar['attributes']['LAT']
            n_long = natar['attributes']['LONG']

            distances.append((n_id, get_distance_two_points(b_lat, n_lat, b_long, n_long)))

        # Keep 20 closest natars
        distances.sort(key=lambda x: x[1])
        closest_20 = {str(n_id): dist for n_id, dist in distances[:20]}

        result_table.append({
            'building_id': b_id,
            'lat': b_lat,
            'long': b_long,
            'natar_distances': closest_20
        })
    
    return result_table

@closest_natars_bp.route('/generateClosestNatarsTable', methods=['POST'])
def generate_natar_building_table():
    db = current_app.config['db']

    try:
        token_data = generate_token()
        token = token_data.get('token')

        # Get buildings and natars
        buildings = query_features(ArcgisSettings.BUILDINGS_LAYER, token)
        natars = query_features(ArcgisSettings.NATARS_LAYER, token)

        if not buildings or not natars:
            raise Exception('Missing data from ArcGIS server')

        results_table = create_table(buildings, natars)

        db.drop_collection(Collections.CLOSEST_NATARS)
        db[Collections.CLOSEST_NATARS].insert_many(results_table)

        return jsonify({'status': 'success', 'count': len(results_table)})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
