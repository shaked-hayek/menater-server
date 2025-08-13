import pymongo
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
from typing import Union, Optional

from settings import Collections


class ClientError(BaseModel):
    message: str
    error: Optional[Union[str, dict]] = None

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
            error_data = ClientError(**request.get_json())

        except ValidationError:
            return jsonify({'message': 'Bad request'}), 400
        
        data = error_data.dict()
        data['timestamp'] = datetime.utcnow().isoformat()
        result = errors_collection.insert_one(data)

        return jsonify({'message': 'Error logged', 'id': str(result.inserted_id)}), 201

