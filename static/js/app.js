// Initialize the map
let myMap = L.map("map").setView([37.09, -95.71], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(myMap);

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
}

generateStateLocationBarGraph("Alabama");
generateStateLeaflet("Alabama");
