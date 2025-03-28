import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Staff(BaseModel):
    name: str
    occupation: str
    status: str = 'None'
    phoneNumber: str = ''

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff', methods=['GET', 'POST'])
def manage_staff():
    db = current_app.config['db']
    staff_collection = db[Collections.STAFF]

    if request.method == 'GET':
        staff_list = list(staff_collection.find({}, {'_id': 0}))
        return jsonify(staff_list)

    elif request.method == 'POST':
        try:
            staff = Staff(**request.get_json())
        except ValidationError:
            return jsonify({'message': 'Bad request'}), 400
        staff_collection.insert_one(staff.dict())
        return jsonify({'message': 'Staff member added'}), 201

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'message': 'Missing name field'}), 400

        result = staff_collection.delete_one({'name': data['name']})

        if result.deleted_count == 0:
            return jsonify({'message': 'Staff member not found'}), 404

        return jsonify({'message': 'Staff member deleted'}), 200

