import pymongo
from flask import Blueprint, jsonify, request, current_app
from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Optional
from enum import Enum
from bson import ObjectId

from settings import Collections


class MODE(str, Enum):
    TRIAL = 'trial'
    EMERGENCY = 'emergency'

class Event(BaseModel):
    name: Optional[str] = None
    timeOpened: Optional[datetime] = None
    timeUpdated: Optional[datetime] = None
    mode: MODE
    earthquakeTime: datetime
    earthquakeMagnitude: float


events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET', 'POST'])
def manage_events():
    db = current_app.config['db']
    events_collection = db[Collections.EVENTS]

    if request.method == 'GET':
        event_id = request.args.get('eventId', default=None, type=str)

        if event_id is not None:
            event = events_collection.find_one({'_id': ObjectId(event_id)})
            if event:
                event['id'] = str(event['_id'])
                del event['_id']
                return jsonify(event)
            else:
                return jsonify({'message': 'Event not found'}), 404

        events_list = list(events_collection.find())
        for event in events_list:
            event['id'] = str(event['_id'])
            del event['_id']

        return jsonify(events_list)

    elif request.method == 'POST':
        try:
            data = request.get_json()

            # Add timeOpened and timeUpdated as now if not provided
            if 'timeOpened' not in data or data['timeOpened'] is None:
                data['timeOpened'] = datetime.utcnow().isoformat()

            if 'timeUpdated' not in data or data['timeUpdated'] is None:
                data['timeUpdated'] = datetime.utcnow().isoformat()

            # Ensure mode, earthquakeTime, and earthquakeMagnitude exist
            for field in ['mode', 'earthquakeTime', 'earthquakeMagnitude']:
                if field not in data:
                    return jsonify({'message': f'Missing required field: {field}'}), 400

            # Generate name if not provided
            if 'name' not in data or data['name'] is None:
                try:
                    mode = data['mode']
                    magnitude = float(data['earthquakeMagnitude'])
                    eq_time = datetime.fromisoformat(data['earthquakeTime'])
                    eq_time_str = eq_time.strftime('%Y%m%d_%H%M%S')
                    data['name'] = f'{mode}_mag{magnitude}_{eq_time_str}'
                except Exception as e:
                    return jsonify({'message': 'Failed to generate name', 'error': str(e)}), 400

            event = Event(**data)
        except ValidationError as e:
            return jsonify({'message': 'Bad request', 'errors': e.errors()}), 400

        event_data = event.dict()
        inserted_event = events_collection.insert_one(event_data)
        return jsonify({
            'message': 'Event added',
            'id': str(inserted_event.inserted_id)
        }), 201
