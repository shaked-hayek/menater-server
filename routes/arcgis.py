# routes/arcgis.py
import requests
import random
from flask import Blueprint, request, jsonify
from settings import ArcgisSettings

arcgis_bp = Blueprint('arcgis', __name__)


def generate_token(referer='http://localhost'):
    payload = {
        'username': ArcgisSettings.USERNAME,
        'password': ArcgisSettings.PASSWORD,
        'client': 'referer',
        'referer': referer,
        'expiration': '60',
        'f': 'json',
    }

    response = requests.post(
        f'{ArcgisSettings.PORTAL_URL}/sharing/rest/generateToken',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        verify=False
    )

    return response.json()

@arcgis_bp.route('/arcgis/token', methods=['POST'])
def get_arcgis_token():
    try:
        token = generate_token()
        return jsonify(token)

    except Exception as e:
        print('ArcGIS token fetch error:', e)
        return jsonify({'error': 'Failed to get token'}), 500

