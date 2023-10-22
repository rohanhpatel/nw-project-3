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

@app.route('/leaflet')
def delete_undefined_coord():
    client = MongoClient("mongodb://localhost:27017/")
    haunted_places = client['nw_project_3']['haunted_places'] 
    
    result = haunted_places.delete_many({"$or": [{"latitude": {"$exists": False}}, {"longitude": {"$exists": False}}]})
    data = list(haunted_places.find({}, {'_id': 0}))
    client.close()
    
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)