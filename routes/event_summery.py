import pymongo
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
            staff_members = list(staff_collection.find({'natarId': natar_id}, {'_id': 0}))
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
