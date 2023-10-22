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

    values = list()
    for loc in get_locations():
        match_query = {"$match": {"$and": [{"location": {"$regex": loc, "$options": "i"}}, {"state": state}]}}
        if state == None:
            match_query = {"$match": {"location": {"$regex": loc, "$options": "i"}}}
        group_query = {"$group": {"_id": "$state", "count": {"$sum": 1}}}
        result = list(haunted_places.aggregate([match_query, group_query]))
        if len(result) == 0:
            values.append(0)
        else:
            values.append(result[0]['count'])

    client.close()

    res_df = pd.DataFrame({
        "locations": get_locations(),
        "values": values
    })

    res_df.sort_values(by="values", ascending=False, inplace=True)

    return res_df

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/hidden/states")
def return_state_data():
    return jsonify(get_states())

@app.route("/hidden/locations")
def return_location_data():
    return jsonify(get_locations())

@app.route("/locationBarGraphData/<chosenState>")
def get_location_bar_graph_data(chosenState):
    haunted_state = get_location_data(chosenState)
    return jsonify({"x": list(haunted_state['locations']), "y": list(haunted_state['values'])})

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


# Define a dictionary to map keywords to categories
keyword_mapping = {
    'witch': 'Witches',
    'light': 'Lights',
    'lights': 'Lights',
    'footsteps': 'Footsteps',
    'steps': 'Footsteps',
    'sounds': 'Sounds',
    'sound': 'Sounds',
    'shadows': 'Shadows',
    'shadow': 'Shadows',
    'old man': 'Old Man',
    'old guy': 'Old Man',
    'by themselves': 'Objects Moving',
    'on its own': 'Objects Moving',
}

# Function to categorize descriptions and return the category
def categorize_description(description):
    for keyword in keyword_mapping:
        if keyword in description.lower():
            return keyword_mapping.get(keyword, 'Other')
    return 'Other'

@app.route("/sightings/<chosenState>")
def get_sightings_for_state(chosenState):
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places']

    # Initialize a dictionary to store counts for each category
    category_counts = {
        'Total': 0,
        'Witches': 0,
        'Lights': 0,
        'Footsteps': 0,
        'Sounds': 0,
        'Shadows': 0,
        'Lady': 0,
        'Fire': 0,
        'Little Girl': 0,
        'Old Man': 0,
        'Objects Moving': 0,
        'Other': 0
    }

   # Get all descriptions for the chosen state
    descriptions = haunted_places.find({"state": chosenState}, {"description": 1})

    # Categorize and count observations
    for desc in descriptions:
        category = categorize_description(desc['description'])
        category_counts[category] += 1

    # Calculate the total count of observations
    total_observations = sum(category_counts.values())

    # Add the total count to the 'Total' category
    category_counts['Total'] = total_observations

    client.close()

    labels = list(category_counts.keys())
    counts = list(category_counts.values())

    return jsonify({"labels": labels, "counts": counts})


if __name__ == "__main__":
    app.run(debug=True)