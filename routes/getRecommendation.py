import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
import time

from settings import Collections

get_recommendation_bp = Blueprint('get_recommendation', __name__)

@get_recommendation_bp.route('/getRecommendation', methods=['GET'])
def get_recommendation():
    db = current_app.config['db']
    sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]

    sites_list = list(sites_collection.find({}, {'_id': 0}))
    sites_list = jsonify(sites_list)

    # Add to recommanded natars to natar DB
    # recommended_natars_collection.insert_one(# ADD HERE)
    time.sleep(5) # TODO: remove

    return jsonify({'message': 'Recommendation was generated'}), 200
