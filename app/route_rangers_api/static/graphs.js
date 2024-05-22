function drawgraph(jsonData, xaxis, yaxis, id, color="#69b3a2") {
  var parentContainer = d3.select(id).node().getBoundingClientRect();
  const margin = {
      top: 0.05 * parentContainer.height,
      right: 0.05 * parentContainer.width,
      bottom: 0.2 * parentContainer.height,
      left: 0.15 * parentContainer.width
  };
  var width = parentContainer.width - margin.left - margin.right;
  var height = parentContainer.height - margin.top - margin.bottom;
  
  var bargraph_bus = d3.select(id);

  // Remove existing SVG elements
  bargraph_bus.selectAll("*").remove();

  // Append SVG and set dimensions
  bargraph_bus = bargraph_bus
    .append("svg")
    .attr("width", "100%")
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Initialize the X axis
  var x = d3.scaleBand().range([0, width]).padding(0.2);
  var xAxis = bargraph_bus
    .append("g")
    .attr("transform", "translate(0," + height + ")");

  // Initialize the Y axis
  var y = d3.scaleLinear().range([height, 0]);
  var yAxis = bargraph_bus.append("g").attr("class", "myYaxis");

  // A function that create / update the plot for a given variable:
  function update(xaxis, yaxis) {
    // X axis
    x.domain(jsonData.map(function (d) {
      return d[xaxis];
    }));
    xAxis.transition().duration(1000).call(d3.axisBottom(x))
      .selectAll("text")
      .style("text-anchor", "middle")
      .attr("dx", "0em")
      .attr("dy", "1em")
      .attr("transform", "rotate(0)")
      .style("font-size", function() {
        // Scale font size based on available space
        var availableWidth = x.bandwidth();
        var textWidth = this.getBBox().width*7;
        var scaleFactor = Math.min(1, availableWidth*.7 / textWidth);
        return scaleFactor + "em";
      });

    // Add Y axis
    y.domain([0, d3.max(jsonData, function (d) {
      return +d[yaxis];
    })]);
    yAxis.transition().duration(1000).call(d3.axisLeft(y));
  
    // variable u: map data to existing bars
    var u = bargraph_bus.selectAll("rect").data(jsonData);
  
    // update bars
    u.enter()
      .append("rect")
      .merge(u)
      .transition()
      .duration(1000)
      .attr("x", function (d) {
        return x(d[xaxis]);
      })
      .attr("y", function (d) {
        return y(d[yaxis]);
      })
      .attr("width", x.bandwidth())
      .attr("height", function (d) {
        return height - y(d[yaxis]);
      })
      .attr("fill", color);
  }

  // Initialize plot
  update(xaxis, yaxis);
}
  function drawTrends(jsonData, datasetLabels) {
    var parentContainer = d3.select("#my_dataviz").node().getBoundingClientRect();
    var margin = { top: 30, right: 30, bottom: 150, left: 60 },
        width = parentContainer.width - margin.left - margin.right,
        height = parentContainer.height - margin.top - margin.bottom;
  
    var trend = d3
      .select("#my_dataviz")
      .append("svg")
      .attr("width", "100%")
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
  
    // Reformat the data: we need an array of arrays of {x, y} tuples
    var dataReady = datasetLabels.map(function (grpName) {
      return {
        name: grpName,
        values: jsonData.map(function (d) {
          return { time: d.time, value: +d[grpName] };
        }),
      };
    });
  
    // A color scale: one color for each group
    var myColor = d3.scaleOrdinal().domain(datasetLabels).range(d3.schemeSet2);
  
    // Add X axis --> it is a date format
    var xDomain = d3.extent(jsonData, function(d) { return +d.time; });
    var yMax = d3.max(dataReady, function (d) {
      return d3.max(d.values, function (v) {
        return v.value;
      });
    });
  
    // Define scales with dynamic domains
    var x = d3.scaleLinear().domain(xDomain).range([0, width]);
    var y = d3.scaleLinear().domain([0, yMax]).range([height, 0]);
  
    // Add X axis
    trend.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));
  
    // Add Y axis
    trend.append("g")
      .call(d3.axisLeft(y));
  
    // Add the lines
    var line = d3
      .line()
      .x(function (d) {
        return x(+d.time);
      })
      .y(function (d) {
        return y(+d.value);
      });
    trend
      .selectAll("myLines")
      .data(dataReady)
      .enter()
      .append("path")
      .attr("class", function (d) {
        return d.name;
      })
      .attr("d", function (d) {
        return line(d.values);
      })
      .attr("stroke", function (d) {
        return myColor(d.name);
      })
      .style("stroke-width", 4)
      .style("fill", "none");
  
    // Add the points
    trend
      .selectAll("myDots")
      .data(dataReady)
      .enter()
      .append("g")
      .style("fill", function (d) {
        return myColor(d.name);
      })
      .attr("class", function (d) {
        return d.name;
      })
      .selectAll("myPoints")
      .data(function (d) {
        return d.values;
      })
      .enter()
      .append("circle")
      .attr("cx", function (d) {
        return x(d.time);
      })
      .attr("cy", function (d) {
        return y(d.value);
      })
      .attr("r", 5)
      .attr("stroke", "white");
  
    // Add a label at the end of each line
    trend
      .selectAll("myLabels")
      .data(dataReady)
      .enter()
      .append("g")
      .append("text")
      .attr("class", function (d) {
        return d.name;
      })
      .datum(function (d) {
        return { name: d.name, value: d.values[d.values.length - 1] };
      })
      .attr("transform", function (d) {
        return "translate(" + x(d.value.time) + "," + y(d.value.value) + ")";
      })
      .attr("x", 12)
      .text(function (d) {
        return d.name;
      })
      .style("fill", function (d) {
        return myColor(d.name);
      })
      .style("font-size", 15);
  
    // Add a legend (interactive)
    trend
      .selectAll("myLegend")
      .data(dataReady)
      .enter()
      .append("g")
      .append("text")
      .attr("x", function (d, i) {
        return 30 + i * 60;
      })
      .attr("y", 30)
      .text(function (d) {
        return d.name;
      })
      .style("fill", function (d) {
        return myColor(d.name);
      })
      .style("font-size", 15)
      .on("click", function (d) {
        // is the element currently visible ?
        currentOpacity = d3.selectAll("." + d.name).style("opacity");
        // Change the opacity: from 0 to 1 or from 1 to 0
        d3.selectAll("." + d.name)
          .transition()
          .style("opacity", currentOpacity == 1 ? 0 : 1);
      });
  }

  function drawhorizontalgraph(jsonData, xaxis, yaxis, id, color="#69b3a2") {
    var parentContainer = d3.select(id).node().getBoundingClientRect();
    var margin = { top: 30, right: 30, bottom: 70, left: 150 },
        width = parentContainer.width - margin.left - margin.right,
        height = parentContainer.height - margin.top - margin.bottom;

    var bargraph = d3.select(id);

    // Remove existing SVG elements
    bargraph.selectAll("*").remove();

    // Append SVG and set dimensions
    bargraph = bargraph
      .append("svg")
      .attr("width", "100%")
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Initialize the Y axis
    var y = d3.scaleBand().range([0, height]).padding(0.2);
    var yAxis = bargraph.append("g").attr("transform", "translate(0,0)");

    // Initialize the X axis
    var x = d3.scaleLinear().range([0, width]);
    var xAxis = bargraph.append("g").attr("class", "myXaxis").attr("transform", `translate(0, ${height})`);

    // Function to update the plot
    function update(selectedX, selectedY) {
      // Update X axis domain
      x.domain([0, d3.max(jsonData, function (d) {
        return +d[selectedY];
      })]);
      xAxis.transition().duration(1000).call(d3.axisBottom(x));

      // Update Y axis domain
      y.domain(jsonData.map(function (d) {
        return d[selectedX];
      }));
      yAxis.transition().duration(1000).call(d3.axisLeft(y))
        .selectAll("text")
        .call(wrap, margin.left - 20); // Call wrap function for text wrapping with padding

      // Bind data to rectangles (bars)
      var u = bargraph.selectAll("rect").data(jsonData);

      // Enter new data, update existing data, remove old data
      u.enter()
        .append("rect")
        .merge(u)
        .transition()
        .duration(500)
        .attr("y", function (d) {
          return y(d[selectedX]);
        })
        .attr("x", 0)
        .attr("height", y.bandwidth())
        .attr("width", function (d) {
          return x(d[selectedY]);
        })
        .attr("fill", color);

      // Remove old bars
      u.exit().remove();
    }

    // Text wrapping function
    function wrap(text, width) {
      text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1, // ems
            y = text.attr("y"),
            dy = parseFloat(text.attr("dy")) || 0,
            tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
        while (word = words.pop()) {
          line.push(word);
          tspan.text(line.join(" "));
          if (tspan.node().getComputedTextLength() > width) {
            line.pop();
            tspan.text(line.join(" "));
            line = [word];
            tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
          }
        }
      });
    }

    // Initialize plot
    update(xaxis, yaxis);
  }

  // Sample JSON data
  var jsonData = [
    { transit_type: "Bus", count: 50 },
    { transit_type: "Train", count: 70 },
    { transit_type: "Tram", count: 30 },
    { transit_type: "Ferry", count: 20 },
    { transit_type: "Bike", count: 10 }
  ];

  