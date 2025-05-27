# routes/arcgis.py
import requests
import random
from flask import Blueprint, request, jsonify
from settings import ArcgisSettings

arcgis_bp = Blueprint('arcgis', __name__)

@arcgis_bp.route('/arcgis/token', methods=['POST'])
def get_arcgis_token():
    try:
        payload = {
            'username': ArcgisSettings.USERNAME,
            'password': ArcgisSettings.PASSWORD,
            'client': 'referer',
            'referer': request.json.get('referer', 'http://localhost'),  # fallback
            'expiration': '60',
            'f': 'json',
        }

        # Disable SSL verification for dev only
        response = requests.post(
            f'{ArcgisSettings.PORTAL_URL}/sharing/rest/generateToken',
            data=payload,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            verify=False
        )

        return jsonify(response.json())

    except Exception as e:
        print('ArcGIS token fetch error:', e)
        return jsonify({'error': 'Failed to get token'}), 500


@arcgis_bp.route('/arcgis/casualties_estimate', methods=['GET'])
def get_casualties_estimate():
    try:
        street = request.args.get('street')
        number = request.args.get('number')

        if not street or not number:
            return jsonify({'message': 'Missing street or number field'}), 400

        estimate = str(random.randint(3, 50)) # TODO: Add real algorithm
        return jsonify({'estimate': estimate}), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get casualties estimate'}), 500