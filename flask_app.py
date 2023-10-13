from flask import Flask, render_template
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

# html = open("index_copy.html", "r")
# lines = html.readlines()
# single_html_str = ""
# for l in lines:
#     single_html_str += l.strip()

@app.route("/")
def main_page():
    return render_template('index.html')

@app.route("/bar_chart")
def bar_chart():
    pass

@app.route("/leaflet")
def leaflet():
    pass

@app.route("/other_chart")
def other_chart():
    pass


if __name__ == "__main__":
    app.run(debug=True)