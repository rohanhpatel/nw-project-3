from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['haunted_places']
collection = db['haunted_places']


@app.route('/')
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/all_data<br/>"
        f"/leaflet<br/>"
    )

@app.route('/all_data')
def get_data():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)

@app.route('/leaflet')
def delete_undefined_coord():
    result = collection.delete_many({"$or": [{"latitude": {"$exists": False}}, {"longitude": {"$exists": False}}]})
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
