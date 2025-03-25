from flask import Flask
from flask_cors import CORS
from routes import first_responders_blueprint  # Import the new blueprint
import pymongo

app = Flask(__name__)
CORS(app)

# Connect to MongoDB and create the database
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["menaterdb"]

# Register blueprints with URL prefixes
app.register_blueprint(first_responders_blueprint, url_prefix="/first_responders")  # Register new blueprint

if __name__ == '__main__':
    app.run(debug=True)
