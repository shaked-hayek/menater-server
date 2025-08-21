import pymongo
from bson import ObjectId
from typing import Optional
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Staff(BaseModel):
    name: str
    occupation: str
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


@staff_bp.route('/staff/bulk-add', methods=['POST'])
def bulk_create_staff():
    db = current_app.config['db']
    staff_collection = db[Collections.STAFF]

    try:
        staff_list = request.get_json()
        if not isinstance(staff_list, list):
            return jsonify({'message': 'Expected a list of staff members'}), 400

        validated_staff = []
        for staff_data in staff_list:
            try:
                staff = Staff(**staff_data)
                staff_dict = staff.dict()
                if 'natarId' not in staff_dict or staff_dict['natarId'] is None:
                    staff_dict['natarId'] = 0
                validated_staff.append(staff_dict)
            except ValidationError as e:
                return jsonify({'message': 'Validation error', 'error': e.errors()}), 400

        if not validated_staff:
            return jsonify({'message': 'No valid staff records found'}), 400

        result = staff_collection.insert_many(validated_staff)
        return jsonify({'message': f'Inserted {len(result.inserted_ids)} staff members'}), 201

    except Exception as e:
        return jsonify({'message': 'Server error', 'error': str(e)}), 500


@staff_bp.route('/staff/bulk-update', methods=['PUT'])
def bulk_update_staff():
    db = current_app.config['db']
    staff_collection = db[Collections.STAFF]

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validate required fields
    if 'staffIds' not in data or 'natarId' not in data:
        return jsonify({'message': 'Missing required fields: staffIds and natarId'}), 400

    staff_ids = data['staffIds']
    natar_id = data['natarId']

    # Validate that staffIds is a list
    if not isinstance(staff_ids, list):
        return jsonify({'message': 'staffIds must be a list'}), 400

    # Validate natarId is a number
    if not isinstance(natar_id, (int, float)):
        return jsonify({'message': 'natarId must be a number'}), 400

    try:
        # Convert string IDs to ObjectIds
        object_ids = [ObjectId(staff_id) for staff_id in staff_ids]

        # Step 1: Unassign staff who were previously assigned to this natar but are no longer selected
        staff_collection.update_many(
            {'natarId': natar_id, '_id': {'$nin': object_ids}},
            {'$set': {'natarId': 0}}
        )

        # Step 2: Assign natarId to selected staff
        result = staff_collection.update_many(
            {'_id': {'$in': object_ids}},
            {'$set': {'natarId': natar_id}}
        )

        return jsonify({
            'message': f'Updated {result.modified_count} staff members',
            'matched_count': result.matched_count,
            'modified_count': result.modified_count
        }), 200

    except Exception as e:
        return jsonify({'message': 'Invalid staff ID format or database error'}), 400