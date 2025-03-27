import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Site(BaseModel):
    street: str
    number: int
    casualties: int

sites_bp = Blueprint('sites', __name__)

@sites_bp.route('/sites', methods=['GET', 'POST'])
def manage_sites():
    db = current_app.config['db']
    sites_collection = db[Collections.SITES]

    if request.method == 'GET':
        sites_list = list(sites_collection.find({}, {'_id': 0}))
        return jsonify(sites_list)

    if request.method == 'POST':
        try:
            site = Site(**request.get_json())
        except ValidationError:
            return jsonify({'message': 'Bad request'}), 400
        sites_collection.insert_one(site.dict())
        return jsonify({"message": "Site added successfully!"}), 201
