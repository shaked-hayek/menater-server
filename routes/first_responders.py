from flask import Blueprint, request, jsonify
import pymongo
from bson import ObjectId

# Initialize the blueprint
first_responders_blueprint = Blueprint('first_responders', __name__)

# MongoDB client setup (reuse the connection from app.py or configure as needed)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["menaterdb"]
collection = db["first_responders"]

# Helper function to convert ObjectId to string for JSON responses
def convert_id(obj):
    obj['_id'] = str(obj['_id'])
    return obj

# Route to get all first responders
@first_responders_blueprint.route('/', methods=['GET'])
def get_first_responders():
    responders = collection.find()
    responders_list = [convert_id(responder) for responder in responders]
    return jsonify(responders_list)

# Route to add a new first responder
@first_responders_blueprint.route('/', methods=['POST'])
def add_first_responder():
    data = request.get_json()
    new_responder = {
        'full_name': data.get('full_name'),
        'department': data.get('department'),
        'assigned_to': data.get('assigned_to'),
        'phone_number': data.get('phone_number')
    }
    result = collection.insert_one(new_responder)
    new_responder['_id'] = str(result.inserted_id)
    return jsonify(new_responder), 201

# Route to remove a first responder by ID
@first_responders_blueprint.route('/<responder_id>', methods=['DELETE'])
def remove_first_responder(responder_id):
    result = collection.delete_one({'_id': ObjectId(responder_id)})
    if result.deleted_count == 0:
        return jsonify({'message': 'Responder not found'}), 404
    return jsonify({'message': 'Responder deleted successfully'}), 200
