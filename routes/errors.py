import pymongo
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections


errors_bp = Blueprint('errors', __name__)

@errors_bp.route('/errors', methods=['GET', 'POST'])
def manage_errors():
    db = current_app.config['db']
    errors_collection = db[Collections.ERRORS]

    if request.method == 'GET':
        errors_list = list(errors_collection.find({}, {'_id': 0}))
        return jsonify(errors_list), 200

    if request.method == 'POST':
        try:
            error_data = request.get_json()

            if not error_data:
                return jsonify({'error': 'No data provided'}), 400

            error_data['timestamp'] = datetime.utcnow().isoformat()
            result = errors_collection.insert_one(error_data)
            return jsonify({'message': 'Error logged', 'id': str(result.inserted_id)}), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

