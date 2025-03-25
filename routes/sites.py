from flask import Blueprint, jsonify, request
import pymongo

from settings import Collections

sites_bp = Blueprint("sites", __name__)

@sites_bp.route('/sites', methods=['GET', 'POST'])
def manage_sites():
    db = staff_bp.app.config['db']
    staff_collection = db[Collections.SITES]

    if request.method == 'GET':
        sites = collection.find()
        site_list = [{**site, "_id": str(site["_id"])} for site in sites]
        return jsonify(site_list)

    if request.method == 'POST':
        site = {
            "street": street_name,
            "number": number,
            "casualties": casualties
        }
        collection.insert_one(site)
        return jsonify({"message": "Site added successfully!"})
