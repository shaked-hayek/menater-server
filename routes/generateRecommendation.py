import pymongo
import requests
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from .arcgis import generate_token
from settings import ArcgisSettings, Collections
from recommended_natars_algorithm.get_recommended_natars import get_recommended_natars


generate_recommendation_bp = Blueprint('generate_recommendation', __name__)


def query_features(layer_name, token):
    url = f'{ArcgisSettings.LAYER_SERVER_URL}/{layer_name}/query'
    all_features = []
    offset = 0
    page_size = 2000  # ArcGIS default max

    while True:
        params = {
            'where': '1=1',
            'outFields': '*',
            'f': 'json',
            'token': token,
            'resultOffset': offset,
            'resultRecordCount': page_size
        }

        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            raise Exception(f"ArcGIS error: {data['error']['message']} (code {data['error']['code']})")

        features = data.get('features', [])
        all_features.extend(features)

        print(f'Fetched {len(features)} records at offset {offset}')

        if len(features) < page_size:
            break  # No more data

        offset += page_size

    return all_features

def get_arcgis_data():
    token_data = generate_token()
    token = token_data.get('token')

    # Get buildings and natars
    buildings = query_features(ArcgisSettings.BUILDINGS_LAYER, token)
    natars = query_features(ArcgisSettings.NATARS_LAYER, token)

    if not buildings or not natars:
        raise Exception('Missing data from ArcGIS server')

    return buildings, natars

def extract_sites(sites_list, buildings):
    # Index buildings by OBJECTID
    building_index = {
        b['attributes'].get('OBJECTID'): b
        for b in buildings
    }

    sites_data = []
    for site in sites_list:
        building_id = site['buildingId']
        casualties = site['casualties']

        matching_building = building_index.get(building_id)
        if matching_building:
            lat = matching_building['attributes'].get('LAT')
            long = matching_building['attributes'].get('LONG')
            if lat is not None and long is not None:
                sites_data.append([building_id, lat, long, casualties])
            else:
                print(f'Building {building_id} missing LAT/LONG')
        else:
            print(f'No building match found for id={building_id}')
    return sites_data

def extract_natars(natars):
    natars_data = []
    for natar in natars:
        attr = natar['attributes']
        natar_id = attr.get('OBJECTID')
        lat = attr.get('LAT')
        long = attr.get('LONG')
        father = attr.get('father')
        if lat is not None and long is not None:
            natars_data.append([natar_id, lat, long, father])
        else:
            print(f'Natar with OBJECTID={attr.get("OBJECTID")} missing LAT/LONG')

    return natars_data

@generate_recommendation_bp.route('/generateRecommendation', methods=['GET'])
def generate_recommendation():
    db = current_app.config['db']
    sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]

    sites_list = list(sites_collection.find({}, {'_id': 0}))
    buildings, natars = get_arcgis_data()
    
    # sites_data : [id, lat, long, casualties]
    sites_data = extract_sites(sites_list, buildings)

    # natars_data : [id, lat, long, father]
    natars_data = extract_natars(natars)

    recommended_natars_ids, remaining_sites = get_recommended_natars(sites_data, natars_data)

    # Save recommended natars to DB
    now = datetime.now()
    recommended_documents = [{'id': natar_id, 'date': now} for natar_id in recommended_natars_ids]

    if recommended_documents:
        recommended_natars_collection.insert_many(recommended_documents)
        print(f'Inserted {len(recommended_documents)} recommended natars')
    else:
        print('No recommended natars to insert')

    return jsonify({'message': 'Recommendation was generated', 'rec_natars_amount': len(recommended_natars_ids)}), 200
