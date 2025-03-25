from flask import Blueprint, jsonify, request
import pymongo

# Initialize blueprint
sites_blueprint = Blueprint("sites", __name__)

# MongoDB connection (assumes db is available through `g` or app context)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["menaterdb"]
collection = db["sites"]

@sites_blueprint.route('/add', methods=['POST'])
def add_site():
    site = {
        "street": "Main St",
        "number": 123,
        "casualties": 5
    }
    collection.insert_one(site)
    return jsonify({"message": "Site added successfully!"})

@sites_blueprint.route('/get', methods=['GET'])
def get_sites():
    sites = collection.find()
    site_list = [{**site, "_id": str(site["_id"])} for site in sites]
    return jsonify(site_list)
