import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Settings


init_bp = Blueprint('init', __name__)

@init_bp.route('/initializeDB', methods=['DELETE'])
def initialize_db():
    if request.method == 'DELETE':
        db = current_app.config['db']

        for collection_name in Settings.DB_COLLECTIONS:
            collection = db[collection_name]
            collection.delete_many({})
        
        return jsonify({'message': 'DB initialized'}), 200
