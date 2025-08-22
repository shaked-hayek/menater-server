import pymongo
import requests
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
from pymongo.errors import BulkWriteError

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

def extract_natars(natars, recommended_natars):
    # Index recommended natars by ID for quick lookup
    recommended_index = {
        rec['id']: rec for rec in recommended_natars
    }

    natars_data = []
    for natar in natars:
        attr = natar['attributes']
        natar_id = attr.get('OBJECTID')
        lat = attr.get('LAT')
        long = attr.get('LONG')
        father = attr.get('father')
        is_main = 1 if father == 0 else 0
        capacity = attr.get('capacity')

        # Check if natar is in recommended list
        rec = recommended_index.get(natar_id)
        was_recommended = rec is not None
        if was_recommended:
            capacity -= rec.get('capacityUsed', 0)
        was_opened = rec.get('wasOpened', False) if was_recommended else False

        natars_data.append([natar_id, lat, long, capacity, is_main, father, was_recommended, was_opened])

    return natars_data

def mark_all_sites_as_used(sites_collection):
    result = sites_collection.update_many(
        {},  # Match all documents
        {'$set': {'wasUsedInRec': True}}
    )
    return result.modified_count

def update_recommended_natars_to_db(recommended_natars_collection, recommended_natars):
    now = datetime.now()
    recommended_documents = [{
        'id': natar_id,
        'date': now,
        'capacityUsed': sum([c for s, c in sites_array])
    } for natar_id, sites_array in recommended_natars.items()]

    if not recommended_documents:
        print('No recommended natars to insert')
        return

    try:
        recommended_natars_collection.insert_many(recommended_documents, ordered=False)
        print(f'Inserted {len(recommended_documents)} recommended natars')

    except BulkWriteError as bwe:
        write_errors = bwe.details['writeErrors']

        # Get the ids of the natars that failed to insert (already existed)
        duplicate_ids = [err['op']['id'] for err in write_errors]

        for doc in recommended_documents:
            if doc['id'] in duplicate_ids:
                # Increment capacityUsed in existing document
                recommended_natars_collection.update_one(
                    {'id': doc['id']},
                    {
                        '$inc': {'capacityUsed': doc['capacityUsed']},
                        '$set': {'date': now}
                    }
                )

        inserted_count = len(recommended_documents) - len(write_errors)
        print(f'Inserted {inserted_count} recommended natars, updated {len(write_errors)} duplicates')

def assign_natars_to_sites(sites_collection, new_recommended_natars):
    for natar_id, site_pairs in new_recommended_natars.items():
        for site_id, _ in site_pairs:
            sites_collection.update_one(
                {'buildingId': site_id},
                {'$set': {'coupledNatarId': natar_id}}
            )


@generate_recommendation_bp.route('/generateRecommendation', methods=['GET'])
def generate_recommendation():
    db = current_app.config['db']
    sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]

    sites_list = list(sites_collection.find({'wasUsedInRec': False}, {'_id': 0}))
    if not sites_list:
        return jsonify({'message': 'No new sites', 'rec_natars_amount': 0}), 200

    recommended_natars = list(recommended_natars_collection.find({}, {'_id': 0}))
    buildings, natars = get_arcgis_data()
    
    # sites_data : [id, lat, long, casualties]
    sites_data = extract_sites(sites_list, buildings)

    # natars_data : [id, lat, long, capacity, is_main, father, wasRecommended, wasOpened]
    natars_data = extract_natars(natars, recommended_natars)

    # Run algorithm
    new_recommended_natars = get_recommended_natars(sites_data, natars_data)
    update_recommended_natars_to_db(recommended_natars_collection, new_recommended_natars)

    mark_all_sites_as_used(sites_collection)
    assign_natars_to_sites(sites_collection, new_recommended_natars)

    return jsonify({'message': 'Recommendation was generated', 'rec_natars_amount': len(new_recommended_natars)}), 200
