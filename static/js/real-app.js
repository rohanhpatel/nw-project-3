
let full_data;
let states;

d3.json("/api/states").then((states) => {
    console.log(states);

    selectElement = d3.select("#selDataset");

    for (let i = 0; i < states.length; i++) {
        selectElement.append("option").text(states[i]).attr("value", states[i]);
    }
});

d3.json("/api/data").then((data) => {
    full_data = data;

    console.log(data);
});

function optionChanged(state) {
    generateStatePlaceBarGraph(state);
}

function generateStatePlaceBarGraph(state) {
    d3.json("/sights/state/" + state).then((data) => {
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

generateStatePlaceBarGraph("Alabama");