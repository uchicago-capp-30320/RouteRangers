function drawgraph(csv,xaxis,yaxis) {
    var margin = {top: 30, right: 30, bottom: 70, left: 60},
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var bargraph_bus = d3.select("#my_dataviz");

    // Remove existing SVG elements
    bargraph_bus.selectAll("*").remove();

    // Append SVG and set dimensions
    bargraph_bus = bargraph_bus
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Initialize the X axis
    var x = d3.scaleBand()
        .range([0, width])
        .padding(0.2);
    var xAxis = bargraph_bus.append("g")
        .attr("transform", "translate(0," + height + ")");

    // Initialize the Y axis
    var y = d3.scaleLinear()
        .range([height, 0]);
    var yAxis = bargraph_bus.append("g")
        .attr("class", "myYaxis");

    // A function that create / update the plot for a given variable:
function update(selectedVar) {
    // Parse the Data
    d3.csv(csv, function(data) {
        // X axis
        x.domain(data.map(function(d) { return d.group; }));
        xAxis.transition().duration(1000).call(d3.axisTop(x));

        // Add Y axis
        y.domain([0, d3.max(data, function(d) { return +d[selectedVar]; })]);
        yAxis.transition().duration(1000).call(d3.axisLeft(y));

        // variable u: map data to existing bars
        var u = bargraph_bus.selectAll("rect")
            .data(data);

        // update bars
        u.enter()
            .append("rect")
            .merge(u)
            .transition()
            .duration(5)
            .attr("x", function(d) { return x(d[xaxis]); })
            .attr("y", function(d) { return y(d[selectedVar]); })
            .attr("width", x.bandwidth())
            .attr("height", function(d) { return height - y(d[selectedVar]); })
            .attr("fill", "#69b3a2");
    });
}

    // Initialize plot
    update(yaxis);
}

function drawTrends(csv) {
    var margin = {top: 10, right: 100, bottom: 30, left: 30},
        width = 460 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    var trend = d3.select("#trend_dataviz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    //Read the data
    d3.csv(csv, function(data) {
        // List of groups (here I have one group per column)
        var allGroup = ["valueA", "valueB", "valueC"];

        // Reformat the data: we need an array of arrays of {x, y} tuples
        var dataReady = allGroup.map(function(grpName) {
            return {
                name: grpName,
                values: data.map(function(d) {
                    return {time: d.time, value: +d[grpName]};
                })
            };
        });

        // A color scale: one color for each group
        var myColor = d3.scaleOrdinal()
            .domain(allGroup)
            .range(d3.schemeSet2);

        // Add X axis --> it is a date format
        var x = d3.scaleLinear()
            .domain([0, 10])
            .range([0, width]);
        trend.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        // Add Y axis
        var y = d3.scaleLinear()
            .domain([0, 20])
            .range([height, 0]);
        trend.append("g")
            .call(d3.axisLeft(y));

        // Add the lines
        var line = d3.line()
            .x(function(d) { return x(+d.time) })
            .y(function(d) { return y(+d.value) });
        trend.selectAll("myLines")
            .data(dataReady)
            .enter()
            .append("path")
            .attr("class", function(d) { return d.name })
            .attr("d", function(d) { return line(d.values) })
            .attr("stroke", function(d) { return myColor(d.name) })
            .style("stroke-width", 4)
            .style("fill", "none");

        // Add the points
        trend.selectAll("myDots")
            .data(dataReady)
            .enter()
            .append('g')
            .style("fill", function(d) { return myColor(d.name) })
            .attr("class", function(d) { return d.name })
            .selectAll("myPoints")
            .data(function(d) { return d.values }) 
            .enter()
            .append("circle")
            .attr("cx", function(d) { return x(d.time) })
            .attr("cy", function(d) { return y(d.value) })
            .attr("r", 5)
            .attr("stroke", "white");

        // Add a label at the end of each line
        trend.selectAll("myLabels")
            .data(dataReady)
            .enter()
            .append('g')
            .append("text")
            .attr("class", function(d) { return d.name })
            .datum(function(d) { return {name: d.name, value: d.values[d.values.length - 1]}; })
            .attr("transform", function(d) { return "translate(" + x(d.value.time) + "," + y(d.value.value) + ")"; })
            .attr("x", 12)
            .text(function(d) { return d.name; })
            .style("fill", function(d) { return myColor(d.name) })
            .style("font-size", 15);

        // Add a legend (interactive)
        trend.selectAll("myLegend")
            .data(dataReady)
            .enter()
            .append('g')
            .append("text")
            .attr('x', function(d, i) { return 30 + i * 60 })
            .attr('y', 30)
            .text(function(d) { return d.name; })
            .style("fill", function(d) { return myColor(d.name) })
            .style("font-size", 15)
            .on("click", function(d) {
                // is the element currently visible ?
                currentOpacity = d3.selectAll("." + d.name).style("opacity");
                // Change the opacity: from 0 to 1 or from 1 to 0
                d3.selectAll("." + d.name).transition().style("opacity", currentOpacity == 1 ? 0 : 1);
            });
    });
}