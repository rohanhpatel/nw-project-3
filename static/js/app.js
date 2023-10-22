// Initialize the map
let myMap = L.map("map").setView([37.09, -95.71], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(myMap);

// Load state boundary data as a GeoJSON layer. State boundary geojson data from 
//https://public.opendatasoft.com/explore/dataset/us-state-boundaries/table/?flg=en-us
d3.json('../static/data/us-state-boundaries.geojson').then(stateBoundaryData => {
    // Create the GeoJSON layer using the loaded data
    let stateBoundaryLayer = L.geoJSON(stateBoundaryData, {
        style: {
            color: 'black',
            weight: 0.5,
            fill: false,
        }
    }).addTo(myMap);
});

d3.json("/hidden/states").then((states) => {
    console.log(states);

    selectElement = d3.select("#selState");

    for (let i = 0; i < states.length; i++) {
        selectElement.append("option").text(states[i]).attr("value", states[i]);
    }
});

function stateChanged(state) {
    generateStateLocationBarGraph(state);
    generateStateLeaflet(state);
}

function generateStateLocationBarGraph(state) {
    d3.json("/locationBarGraphData/" + state).then((data) => {
        let topTenValues = data.y.slice(0, 10);
        let topTenLabels = data.x.slice(0, 10);

        let barGraphData = [{
            x: topTenLabels,
            y: topTenValues,
            type: 'bar'
        }];

        let barGraphLayout = {
            title: {
                text: "Top 10 Haunted Locations in " + state
            }
        }

        Plotly.newPlot("bar", barGraphData, barGraphLayout);
    });
}

function generateStateLeaflet(state) {
    d3.json("/leaflet/" + state).then((data) => {
        console.log(data);

        let city_data = data.cities;

        // Clear the map before adding new data
        myMap.eachLayer(function (layer) {
            if (layer instanceof L.Circle) {
                myMap.removeLayer(layer);
            }
        });

        // Load the state center coordinates and zoom level from your JSON data
        d3.json("../static/data/state_centers.json").then((centerData) => {
            // Find the state data by matching the state name
            const stateInfo = centerData.find((item) => item.name === state);

            if (stateInfo) {
                const stateCenterLat = stateInfo.lat;
                const stateCenterLng = stateInfo.lon;
                const stateZoomLevel = stateInfo.zoom*1.2;

                console.log("Center Coordinates:", stateCenterLat, stateCenterLng);
                console.log("Zoom Level:", stateZoomLevel);

                const stateCenter = [stateCenterLat, stateCenterLng];

                // Set the view to center on the state with an appropriate zoom level
                myMap.setView(stateCenter, stateZoomLevel);
            }

            for (let i = 0; i < city_data.length; i++) {
                cur_city = city_data[i];
                if (cur_city["lat"] != null && cur_city["lng"] != null) {
                    L.circle([cur_city["lat"], cur_city["lng"]], {
                        fillOpacity: 0.75,
                        color: "black",
                        fillColor: "white",
                        radius: cur_city["count"] * 100,
                    }).bindPopup(`<p>City: ${cur_city["name"]}</p><p>Number of Sightings: ${cur_city["count"]}</p>`)
                    .addTo(myMap);
                }
            }
        });
    });
}    


generateStateLocationBarGraph("");
generateStateLeaflet("");
