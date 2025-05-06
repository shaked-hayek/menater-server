# routes/arcgis.py
import requests
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
