import pymongo
from bson import ObjectId
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError

from settings import Collections


event_summery_bp = Blueprint('eventSummery', __name__)

class EventSummeryModel(BaseModel):
    eventId: str
    destructionSites: list
    recommendedNatars: list  # list of dicts: {'natarId': str, 'staff': [str, str, ...]}

@event_summery_bp.route('/eventSummery', methods=['GET', 'POST'])
def manage_event_summery():
    db = current_app.config['db']
    summery_collection = db[Collections.EVENT_SUMMERY]
    events_collection = db[Collections.EVENTS]
    destruction_sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]
    staff_collection = db[Collections.STAFF]

    if request.method == 'GET':
        event_id = request.args.get('eventId', default=None, type=str)

        if event_id is not None:
            event_summery = summery_collection.find_one({'eventId': event_id}, {'_id': 0})
            if event_summery:
                return jsonify(event_summery)
            else:
                return jsonify({'message': 'Event summery not found'}), 404

        all_summaries = list(summery_collection.find({}, {'_id': 0}))
        return jsonify(all_summaries)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'eventId' not in data:
            return jsonify({'message': 'Missing eventId'}), 400

        event_id = data['eventId']

        # Fetch destruction sites for this event
        destruction_sites = list(destruction_sites_collection.find({}, {'_id': 0}))

        # Fetch recommended natars
        recommended_natars = list(recommended_natars_collection.find({}, {'_id': 0}))

        # Attach assigned staff for each natar (based on natarId in staff)
        for natar in recommended_natars:
            natar_id = natar.get('id')
            staff_members = list(staff_collection.find({'natarId': natar_id}))
            for staff in staff_members:
                staff['id'] = str(staff['_id'])
                del staff['_id']
            natar['staff'] = staff_members

        # Build and validate model
        try:
            summary_model = EventSummeryModel(
                eventId=event_id,
                destructionSites=destruction_sites,
                recommendedNatars=recommended_natars
            )
        except ValidationError:
            return jsonify({'message': 'Invalid data'}), 400

        # Insert to DB
        summery_collection.insert_one(summary_model.dict())
        return jsonify({'message': 'Event summery created'}), 201


def run_clear_event_data(destruction_sites_collection, recommended_natars_collection, staff_collection):
    # Delete destruction sites and recommended natars
    destruction_sites_collection.delete_many({})
    recommended_natars_collection.delete_many({})

    # Reset all staff natarId to 0
    staff_collection.update_many({}, {'$set': {'natarId': 0}})

@event_summery_bp.route('/eventSummery/clear', methods=['POST'])
def clear_event_data():
    db = current_app.config['db']
    destruction_sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]
    staff_collection = db[Collections.STAFF]

    run_clear_event_data(destruction_sites_collection, recommended_natars_collection, staff_collection)

    return jsonify({'message': f'Data for event cleared successfully'}), 200


@event_summery_bp.route('/eventSummery/load/<event_id>', methods=['POST'])
def load_event_data(event_id):
    db = current_app.config['db']
    summery_collection = db[Collections.EVENT_SUMMERY]
    destruction_sites_collection = db[Collections.SITES]
    recommended_natars_collection = db[Collections.RECOMMENDED_NATARS]
    staff_collection = db[Collections.STAFF]

    summary = summery_collection.find_one({'eventId': event_id})
    if not summary:
        return jsonify({'message': 'Event summary not found'}), 404

    # Clear existing data
    run_clear_event_data(destruction_sites_collection, recommended_natars_collection, staff_collection)

    # Restore destruction sites
    if 'destructionSites' in summary:
        destruction_sites_collection.insert_many(summary['destructionSites'])

    # Restore recommended natars
    if 'recommendedNatars' in summary:
        for natar in summary['recommendedNatars']:
            staff_ids = [s['id'] for s in natar.get('staff', [])]
            natar_to_insert = {k: v for k, v in natar.items() if k != 'staff'}
            recommended_natars_collection.insert_one(natar_to_insert)

            # Update staff natarId
            for staff_id in staff_ids:
                staff_collection.update_one(
                    {'_id': ObjectId(staff_id)},
                    {'$set': {'natarId': natar_to_insert['id']}}
                )

    return jsonify({'message': f'Data for event {event_id} loaded from summary'}), 200
