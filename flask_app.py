from flask import Flask, render_template, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pprint import pprint
import pandas as pd
import numpy as np
import re
import json

app = Flask(__name__)
CORS(app)

def get_states():
    # get states
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places']   

    group_states = {"$group": {"_id": "$state"}}
    sort_states= {"$sort": {"_id": 1}}

    all_states = list(haunted_places.aggregate([group_states, sort_states]))
    state_list = list()
    for state in all_states:
        state_list.append(state["_id"])
    
    client.close()

    return state_list

@app.route("/")
def main_page():
    return render_template('real_index.html')

@app.route("/api/states")
def return_state_data():
    return jsonify(get_states())

@app.route("/api/data")
def return_all_data():
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places']   

    full_res = list(haunted_places.find())
    full_data = list()
    for res in full_res:
        d = dict()
        for key in res:
            if key == "_id":
                d[key] = str(res[key])
            else:
                d[key] = res[key]
        full_data.append(d)
    
    client.close()

    return jsonify(full_data)

@app.route("/sights/state/<chosenState>")
def get_state_place_data(chosenState):
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places'] 

    query = {"state": chosenState}
    filter = {"_id": 0, "description": 0, "country": 0, "state_abbrev": 0}

    state_res = list(haunted_places.find(query, filter))

    client.close()

    # make dataframe and then use Joel's code to get the x and y values for this bar graph
    haunted_state = pd.DataFrame(state_res)
    haunted_state['place'] = haunted_state['location'].str.extract(r'([a-zA-Z]+)\s*$')

    # Replace 'inn' with 'hotel' in the 'place' column
    haunted_state['place'] = haunted_state['place'].str.replace('inn', 'hotel', case=False)
    
    haunted_state['place'] = haunted_state['location'].str.split().str[-1]
    haunted_state['place'] = haunted_state['place'].apply(lambda word: re.sub(r'[^a-zA-Z]', '', word) if pd.notnull(word) else '') #Removing non-letter characters from the last position using regular expression
    haunted_state['place'] = haunted_state['place'].str.replace('inn', 'hotel')

    merge_dict = {
    'school': 'Schools',
    'School': 'Schools',
    'High': 'Schools',
    'university': 'Schools',
    'University': 'Schools',
    'college': 'Schools',
    'College': 'Schools',
    'Elementary': 'Schools',  
    'elementary': 'Schools',
    'Academy': 'Schools',
    'Cementeries': 'Cementeries',
    'cemetery': 'Cementeries',  
    'Cemetery': 'Cementeries', 
    'Graveyard': 'Cementeries',
    'House': 'Houses',
    'Apartments': 'Houses',
    'home': 'Houses',
    'Mansion': 'Houses',
    'Home': 'Houses',
    'house':'Houses',
    'Road': 'Roads',
    'road': 'Roads',
    'Street':'Roads',
    'Rd': 'Roads',
    'hotel':'Hotels',
    'Hotel':'Hotels',
    }
    haunted_state['place_merge'] = haunted_state['place'].replace(merge_dict)

    merged_place_counts = haunted_state['place_merge'].value_counts()

    values = list()
    for val in merged_place_counts.values:
        values.append(int(val))

    return jsonify({"x": list(merged_place_counts.index), "y": values})

@app.route('/leaflet')
def delete_undefined_coord():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['nw_project_3']
    collection = db['haunted_placed']
    
    result = collection.delete_many({"$or": [{"latitude": {"$exists": False}}, {"longitude": {"$exists": False}}]})
    data = list(collection.find({}, {'_id': 0}))

    client.close()
    
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)