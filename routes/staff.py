from flask import Blueprint, jsonify, request, current_app
import pymongo
from settings import Collections

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff', methods=['GET', 'POST'])
def manage_staff():
    db = current_app.config['db']
    staff_collection = db[Collections.STAFF]

    if request.method == 'GET':
        staff_list = list(staff_collection.find({}, {'_id': 0}))
        return jsonify(staff_list)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data or 'occupation' not in data:
            return jsonify({'error': 'Missing name or occupation'}), 400
        staff_collection.insert_one({'name': data['name'], 'occupation': data['occupation']})
        return jsonify({'message': 'Staff member added'}), 201


