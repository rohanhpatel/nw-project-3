const url = "https://2u-data-curriculum-team.s3.amazonaws.com/dataviz-classroom/v1.1/14-Interactive-Web-Visualizations/02-Homework/samples.json";

// set up dropdown with all the options
d3.json(url).then((data) => {

    console.log(data);
    
    selectElement = d3.select("#selDataset");

    for (let i = 0; i < data.names.length; i++) {
        selectElement.append("option").text(data.names[i]).attr("value", data.names[i]);
    }

});

function updateBarGraph(dataset) {
    d3.json(url).then((data) => {
        // find data point where dataset = sample.id
        let dataPoint = data.samples.filter((sample) => sample.id == dataset)[0];
        
        // data is already sorted
        let topTenValues = dataPoint.sample_values.slice(0, 10).reverse();
        let topTenHoverTexts = dataPoint.otu_labels.slice(0, 10).reverse();
        let topTenOTUIDs = dataPoint.otu_ids.slice(0, 10).reverse();
        let topTenOTUNames = [];
        for (let i = 0; i < topTenOTUIDs.length; i++) {
            topTenOTUNames.push("OTU " + topTenOTUIDs[i].toString());
        }

        let barGraphData = [{
            x: topTenValues,
            y: topTenOTUNames,
            text: topTenHoverTexts,
            orientation: 'h',
            type: 'bar'
        }];

        Plotly.newPlot("bar", barGraphData);

    });
}

function updateMetadataInfo(dataset) {
    // remove all previous data
    metadataElement = d3.select("#sample-metadata");
    metadataElement.selectAll("p").remove();

    d3.json(url).then((data) => {
        // find metadata for dataset
        let metaPoint = data.metadata.filter((sample) => sample.id == dataset)[0];
        // put it in the info box
        for (const [key, value] of Object.entries(metaPoint)) {
            metadataElement.append("p").text(key.toString() + ": " + value.toString());
        }

    });
}

function updateBubbleGraph(dataset) {
    d3.json(url).then((data) => {
        // find the data point in samples
        let dataPoint = data.samples.filter((sample) => sample.id == dataset)[0];

        // make the graph using all the values
        let bubbleGraphData = [{
            x: dataPoint.otu_ids,
            y: dataPoint.sample_values,
            mode: 'markers',
            marker: {
                size: dataPoint.sample_values,
                color: dataPoint.otu_ids
            },
            text: dataPoint.otu_labels
        }];

        Plotly.newPlot("bubble", bubbleGraphData);
    });
}

function updateAllGraphs(dataset) {
    updateBarGraph(dataset);
    updateMetadataInfo(dataset);
    updateBubbleGraph(dataset);
    // updateGaugeGraph(dataset);
}

// on dropdown change, change the plots
d3.selectAll("#selDataset").on("change", updatePlots);

function updatePlots() {
    let dataset = d3.select("#selDataset").property("value");
    updateAllGraphs(dataset);
}

updateAllGraphs("940");