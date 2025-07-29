import pymongo
from flask import Flask
from flask_cors import CORS

from settings import Settings
from routes.events import events_bp
from routes.staff import staff_bp
from routes.sites import sites_bp
from routes.arcgis import arcgis_bp
from routes.generateRecommendation import generate_recommendation_bp
from routes.natars import natars_bp
from routes.actions_log import actions_log_bp
from routes.event_summery import event_summery_bp
from routes.errors import errors_bp
from routes.init_db import init_bp

def db_connect():
    client = pymongo.MongoClient(Settings.DB_SERVER)
    db = client[Settings.DB_CLIENT]
    return db

def start_app(debug_mode):
    app = Flask(__name__)
    CORS(app)

    # Connect to MongoDB and create the database
    db = db_connect()
    app.config['db'] = db

    # Register blueprints with URL prefixes
    app.register_blueprint(events_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(arcgis_bp)
    app.register_blueprint(generate_recommendation_bp)
    app.register_blueprint(natars_bp)
    app.register_blueprint(actions_log_bp)
    app.register_blueprint(event_summery_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(init_bp)

    app.run(debug=debug_mode, use_reloader=False)

if __name__ == '__main__':
    start_app(Settings.DEBUG)
