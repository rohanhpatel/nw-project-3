// Initialize the map
let myMap = L.map("map").setView([37.09, -95.71], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(myMap);

d3.json("/hidden/states").then((states) => {
    console.log(states);

    selectElement = d3.select("#selDataset");

    for (let i = 0; i < states.length; i++) {
        selectElement.append("option").text(states[i]).attr("value", states[i]);
    }
});

function optionChanged(state) {
    generateStateSightsBarGraph(state);
    generateStateLeaflet(state);
}

function generateStateSightsBarGraph(state) {
    d3.json("/sights/" + state).then((data) => {
        let topTenValues = data.y.slice(0, 10);
        let topTenLabels = data.x.slice(0, 10);

        let barGraphData = [{
            x: topTenLabels,
            y: topTenValues,
            type: 'bar'
        }];

        let barGraphLayout = {
            title: {
                text: "Top 10 Sights in " + state
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

generateStateSightsBarGraph("Alabama");
generateStateLeaflet("Alabama");





// Initialize the map
//function generateLeaflet() {
//    let map = L.map('map').setView([39.82, -98.58], 5);
//    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//    maxZoom: 19,
//    }).addTo(map);

    // Load state boundary data as a GeoJSON layer. State boundary geojson data from 
    //https://public.opendatasoft.com/explore/dataset/us-state-boundaries/table/?flg=en-us
//    d3.json('../static/data/us-state-boundaries.geojson').then(stateBoundaryData => {
        // Create the GeoJSON layer using the loaded data
//        let stateBoundaryLayer = L.geoJSON(stateBoundaryData, {
//            style: {
//                color: 'black',
//                weight: 0.5,
//                fill: false,
//            }
//        }).addTo(map);
//    });


    // Create an empty object to store state clusters
//    let markers = L.markerClusterGroup();

    // Make request to leaflet API endpoint
//    d3.json("/leaflet").then(data => {

            // Add each marker to the MarkerClusterGroup instead of directly to the map
//            data.forEach(item => {
//                let lat = item.latitude;
//                let lng = item.longitude;
//                let state = item.state;
//                let name = item.city + ", " + state;

//                if (lat !== undefined && lng !== undefined) {
//                    let marker = L.marker([lat, lng])
//                        .bindPopup(name + '<br>' + item.location);

                    // Create a cluster for the state if it doesn't exist
//                    if (lat !== undefined && lng !== undefined) {
//                    let marker = L.marker([lat, lng])
//                        .bindPopup(name + '<br>' + item.location);

                    // Add the marker to the single MarkerClusterGroup
//                    markers.addLayer(marker);
//                } else {
//                    console.warn(`Skipping item (${name}) without valid coordinates.`);
//                }
//                }});    
    

            // Add the single MarkerClusterGroup to the map
//            map.addLayer(markers);
//        });
//}

//generateLeaflet()