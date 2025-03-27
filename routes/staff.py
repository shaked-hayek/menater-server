import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Staff(BaseModel):
    name: str
    occupation: str

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
