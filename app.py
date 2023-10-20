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

def get_locations():
    return ["School", "Cemetery", "House", "Hotel", "Road", "Park", "Bridge", "Hospital", "Church", "Theater", "Restaurant"]

def get_location_data(state=None):
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places'] 

    if state == None:
        query = {}
    else:
        query = {"state": state}
    filter = {"_id": 0, "description": 0, "country": 0, "state_abbrev": 0}

    state_res = list(haunted_places.find(query, filter))

    client.close()

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
    'Cementeries': 'Cemeteries',
    'cemetery': 'Cemeteries',  
    'Cemetery': 'Cemeteries', 
    'Graveyard': 'Cemeteries',
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
    haunted_state['place_merge'].replace('', None, inplace=True)
    haunted_state.dropna(inplace=True)

    return haunted_state

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/hidden/states")
def return_state_data():
    return jsonify(get_states())

@app.route("/hidden/locations")
def return_location_data():
    haunted_locations = get_location_data()
    return jsonify(list(haunted_locations['place_merge'].unique()))

@app.route("/locations/<chosenState>")
def get_state_location_data(chosenState):
    haunted_state = get_location_data(chosenState)
    merged_place_counts = haunted_state['place_merge'].value_counts()
    return jsonify({"x": list(merged_place_counts.index), "y": [int(x) for x in merged_place_counts.values]})

@app.route("/leaflet/<chosenState>")
def get_leaflet_data(chosenState):
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places']

    match_query = {"$match": {"state": chosenState}}
    group_query = {"$group": {"_id": "$city", "lat": {"$first": "$city_latitude"}, "lng": {"$first": "$city_longitude"}, "count": {"$sum": 1}}}
    group_state_query = {"$group": {"_id": "$state", "lat": {"$first": "$latitude"}, "lng": {"$first": "$longitude"}}}

    state_city_res = list(haunted_places.aggregate([match_query, group_query]))

    city_list = list()
    for res in state_city_res:
        d = dict()
        for key in res:
            if key == "_id":
                d["name"] = res[key]
            else:
                d[key] = res[key]
        city_list.append(d)

    state_res = list(haunted_places.aggregate([match_query, group_state_query]))
    state_lat = float(state_res[0]['lat'])
    state_lng = float(state_res[0]['lng'])

    client.close()

    return jsonify({"state_lat": state_lat, "state_lng": state_lng, "cities": city_list})

if __name__ == "__main__":
    app.run(debug=True)