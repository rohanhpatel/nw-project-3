from flask import Flask, jsonify
from pymongo import MongoClient
from pprint import pprint

###################
# Database Setup
###################
client = MongoClient(port=27017)
db = client['nw-project-3']

# haunted-places is the name of the collection

###################
# App Setup
###################
app = Flask(__name__)

###################
# Define routes
###################
@app.route("/")
def main_page():
    return (
        f"Available routes:<br/>"
        f"need to come up with routes"
    )

if __name__ == "__main__":
    app.run(debug=True)