import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
import time

from settings import Collections

get_recommended_natars_bp = Blueprint('get_recommended_natars', __name__)

@get_recommended_natars_bp.route('/getRecommendedNatars', methods=['GET'])
def get_recommended_natars():
    db = current_app.config['db']
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]

    natars_list = list(recommended_natars_collection.find({}, {'_id': 0}))
    return jsonify(natars_list)
