
d3.json("/hidden/states").then((states) => {
    console.log(states);

    selectElement = d3.select("#selState");

    for (let i = 0; i < states.length; i++) {
        selectElement.append("option").text(states[i]).attr("value", states[i]);
    }
});

d3.json("/hidden/locations").then((locations) => {
    console.log(locations);

    selectElement = d3.select("#selLocation");

    for (let i = 0; i < locations.length; i++) {
        selectElement.append("option").text(locations[i]).attr("value", locations[i]);
    }
});

function stateChanged(state) {
    generateStateSightsBarGraph(state);
}

function locationChanged(location) {
    console.log(location);
}

function generateStateLocationBarGraph(state) {
    d3.json("/locations/" + state).then((data) => {
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

        let myMap = L.map("map", {
            center: [data.state_lat, data.state_lng],
            zoom: 5
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(myMap);

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

generateStateSightsBarGraph("Alabama");
// generateStateLeaflet("Alabama");