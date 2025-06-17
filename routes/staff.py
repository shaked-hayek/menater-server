import pymongo
from bson import ObjectId
from typing import Optional
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Staff(BaseModel):
    name: str
    occupation: str
    status: str = 'None'
    phoneNumber: str = ''
    natarId: Optional[int] = 0

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff', methods=['GET', 'POST', 'DELETE'])
def manage_staff():
    db = current_app.config['db']
    staff_collection = db[Collections.STAFF]

    if request.method == 'GET':
        natar_id = request.args.get('natarId', default=None, type=int)

        if natar_id is not None:
            staff_list = list(staff_collection.find({'natarId': natar_id}))
        else:
            staff_list = list(staff_collection.find({}))

        for staff in staff_list:
            staff['id'] = str(staff['_id'])
            del staff['_id']
        return jsonify(staff_list)

    elif request.method == 'POST':
        try:
            staff = Staff(**request.get_json())
        except ValidationError:
            return jsonify({'message': 'Bad request'}), 400
        
        staff_data = staff.dict()
        if 'natarId' not in staff_data or staff_data['natarId'] is None:
            staff_data['natarId'] = 0

        staff_collection.insert_one(staff_data)
        return jsonify({'message': 'Staff member added'}), 201

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'id' not in data:
            return jsonify({'message': 'Missing id field'}), 400

        try:
            object_id = ObjectId(data['id'])
            result = staff_collection.delete_one({'_id': object_id})
        except Exception as e:
            return jsonify({'message': 'Invalid id format', 'error': e}), 400

        if result.deleted_count == 0:
            return jsonify({'message': 'Staff member not found'}), 404

        return jsonify({'message': 'Staff member deleted'}), 200

