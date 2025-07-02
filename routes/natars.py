import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
from datetime import datetime
import time

from settings import Collections

natars_bp = Blueprint('get_recommended_natars', __name__)

@natars_bp.route('/getRecommendedNatars', methods=['GET'])
def get_recommended_natars():
    db = current_app.config['db']
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]

    natars_list = list(recommended_natars_collection.find({}, {'_id': 0}))
    return jsonify(natars_list)


@natars_bp.route('/natars', methods=['PUT'])
def natars():
    db = current_app.config['db']
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]
    
    natar_id = request.args.get('id', type=int)
    is_opened = request.args.get('opened', type=bool)

    if natar_id is None or is_opened is None:
        return jsonify({'message': 'Missing id or opened parameter'}), 400

    # Try to update the document
    result = recommended_natars_collection.update_one(
        {'id': natar_id},
        {
            '$set': {
                'opened': is_opened,
                'time_updated': datetime.utcnow().isoformat()
            }
        }
    )

    if result.matched_count == 0:
        return jsonify({'message': 'Natar not found'}), 404

    return jsonify({'message': f'Natar {natar_id} updated', 'opened': is_opened}), 200

