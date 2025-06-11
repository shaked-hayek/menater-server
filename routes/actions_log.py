import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections

class Action(BaseModel):
    name: str

actions_log_bp = Blueprint('actionsLog', __name__)

@actions_log_bp.route('/actionsLog', methods=['GET', 'POST'])
def manage_actions_log():
    db = current_app.config['db']
    log_collection = db[Collections.LOG]

    if request.method == 'GET':
        actions_list = list(log_collection.find({}, {'_id': 0}))
        return jsonify(actions_list)

    elif request.method == 'POST':
        try:
            action = Action(**request.get_json())
        except ValidationError:
            return jsonify({'message': 'Bad request'}), 400
        log_collection.insert_one(action.dict())
        return jsonify({'message': 'Action added'}), 201

