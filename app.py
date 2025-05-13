import pymongo
from flask import Flask
from flask_cors import CORS

from settings import Settings
from routes import first_responders_blueprint
from routes.staff import staff_bp
from routes.sites import sites_bp
from routes.arcgis import arcgis_bp

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
    app.register_blueprint(first_responders_blueprint, url_prefix="/first_responders")
    app.register_blueprint(staff_bp)
    app.register_blueprint(sites_bp)
    app.register_blueprint(arcgis_bp)

    app.run(debug=debug_mode, use_reloader=False)

if __name__ == '__main__':
    start_app(Settings.DEBUG)
