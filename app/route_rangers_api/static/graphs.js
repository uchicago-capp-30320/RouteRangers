function drawgraph(jsonData, xaxis, yaxis, id, color="#69b3a2") {
  // Size to parent container for relative screens
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

  // Remove existing SVG elements to update if previously initialed. 
  bargraph_bus.selectAll("*").remove();

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

  // swap json files and/ or y axis 
  function update(xaxis, yaxis) {

    x.domain(jsonData.map(function (d) {
      return d[xaxis];
    }));
    xAxis.transition().duration(1000).call(d3.axisBottom(x))
      .selectAll("text")
      .style("text-anchor", "middle")
      .attr("dx", "0em")
      .attr("dy", "-2em")
      .attr("transform", "rotate(0)")
      .style("font-size", function() {
        // Scale font size based on available space
        var availableWidth = x.bandwidth();
        var textWidth = this.getBBox().width*.8;
        var scaleFactor = Math.min(1, availableWidth*.7 / textWidth);
        return scaleFactor + "em";
      });

    y.domain([0, d3.max(jsonData, function (d) {
      return +d[yaxis];
    })]);
    yAxis.transition().duration(1000).call(d3.axisLeft(y));
  

    var rect_bar_graph = bargraph_bus.selectAll("rect").data(jsonData);
  
    // update bars
    rect_bar_graph.enter()
      .append("rect")
      .merge( rect_bar_graph )
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
  // resize to parent container for dynamic sizing
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

  // Function to filter data points based on graph width for diverse data
  function filterData(values, minDistance) {
    if (values.length < 2) return values;

    let filtered = [values[0]]; // Always include the first point
    let lastIncludedIndex = 0;

    for (let i = 1; i < values.length; i++) {
      let currentX = x(values[i].time);
      let lastIncludedX = x(filtered[filtered.length - 1].time);
      if (currentX - lastIncludedX >= minDistance) {
        filtered.push(values[i]);
      }
    }

    return filtered;
  }

  var dataReady = datasetLabels.map(function (grpName) {
    return {
      name: grpName,
      values: jsonData.map(function (d) {
        return { time: new Date(d.date), value: +d[grpName] };
      }),
    };
  });

  var colors = ["#BF5002","#566C4B","#425469"];
  var timeColors = d3.scaleOrdinal()
    .domain(datasetLabels)
    .range(colors);

  // Add X axis and set domains
  var xDomain = d3.extent(jsonData, function(d) { return new Date(d.date); });
  var yMax = d3.max(dataReady, function (d) {
      return d3.max(d.values, function (v) {
          return v.value;
      });
  });
  var x = d3.scaleTime().domain(xDomain).range([0, width]);
  var y = d3.scaleLinear().domain([0, yMax*1.1]).range([height, 0]);

  trend.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));
  trend.append("g")
      .call(d3.axisLeft(y));

  // Filter points based on minimum distance
  var minDistance = 20;
  dataReady.forEach(function(d) {
    d.values = filterData(d.values, minDistance);
  });
  var line = d3
      .line()
      .x(function (d) {
          return x(d.time);
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
          return timeColors(d.name);
      })
      .style("stroke-width", 4)
      .style("fill", "none");

  // Add the points
  var points = trend
      .selectAll("myDots")
      .data(dataReady)
      .enter()
      .append("g")
      .style("fill", function (d) {
          return timeColors(d.name);
      })
      .attr("class", function (d) {
          return d.name;
      });

  points.selectAll("myPoints")
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
          return timeColors(d.name);
      })
      .style("font-size", 15)
      .on("click", function (d) {
          // toggle opacity for lines
          var currentOpacity = d3.selectAll("." + d.name).style("opacity");
          d3.selectAll("." + d.name)
              .transition()
              .style("opacity", currentOpacity == 1 ? 0 : 1);
      });
}
  function drawhorizontalgraph(jsonData, xaxis, yaxis, id, color="#69b3a2") {
    var parentContainer = d3.select(id).node().getBoundingClientRect();
    const margin = {
        top: 0.05 * parentContainer.height,
        right: 0.05 * parentContainer.width,
        bottom: 0.2 * parentContainer.height,
        left: 0.3 * parentContainer.width
    };
    var width = parentContainer.width - margin.left - margin.right;
    var height = parentContainer.height - margin.top - margin.bottom;
    var bargraph = d3.select(id);
    bargraph.selectAll("*").remove();

    bargraph = bargraph
      .append("svg")
      .attr("width", "100%")
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var y = d3.scaleBand().range([0, height]).padding(0.4);
    var yAxis = bargraph.append("g").attr("transform", "translate(0,0)");

    var x = d3.scaleLinear().range([0, width]);
    var xAxis = bargraph.append("g").attr("class", "myXaxis").attr("transform", `translate(0, ${height})`);

    function update(selectedX, selectedY) {
      x.domain([0, d3.max(jsonData, function (d) {
        return +d[selectedY];
      })]);
      xAxis.transition().duration(1000).call(d3.axisBottom(x));

      y.domain(jsonData.map(function (d) {
        return d[selectedX];
      }));
      yAxis.transition().duration(1000).call(d3.axisLeft(y))
        .selectAll("text")
        .call(wrap, margin.left - 20); 

      var rect_bar_graph = bargraph.selectAll("rect").data(jsonData);

      rect_bar_graph.enter()
        .append("rect")
        .merge(rect_bar_graph)
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
      rect_bar_graph.exit().remove();
    }

    // Text wrapping function
    function wrap(text, width) {
      text.each(function() {
        var text = d3.select(this),
            words = text.text().split(/\s+/).reverse(),
            word,
            line = [],
            lineNumber = 0,
            lineHeight = 1.1,
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