function heatmaps(
  filepath,
  coordinates,
  label,
  variables,
  variableunits,
  titles,
  titles_reversed,
  colorscale = [
    "#FFF7EC",
    "#FEE0C4",
    "#FDBB84",
    "#FC8D59",
    "#EF6548",
    "#D7301F",
    "#B30000",
    "#7F0000",
  ]
) {
  // Initialize the map
  var heatmap = L.map("heatmap").setView(coordinates, 10);

  // Add base layer
  var tiles = L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }
  ).addTo(heatmap);

  // Function to compute the dynamic scale and round to the nearest 10s
  function computeScale(data, variable) {
    let values = data.features.map((f) => Number(f.properties[variable]));
    let min = Math.min(...values);
    let max = Math.max(...values);
    let interval = (max - min) / colorscale.length;
    let scale = [];
    for (let i = 0; i < colorscale.length; i++) {
      scale.push(Math.round(min + i * interval));
    }
    return scale;
  }

  // Segment color by dynamically produced scale
  function getColor(d, scale) {
    return d > scale[6] ? colorscale[7]
      : d > scale[5] ? colorscale[6]
      : d > scale[4] ? colorscale[5]
      : d > scale[3] ? colorscale[4]
      : d > scale[2] ? colorscale[3]
      : d > scale[1] ? colorscale[2]
      : d > scale[0] ? colorscale[1]
      : colorscale[0];
  }

  // Define controls
  var infoControls = {};
  var currentVariable = variables[0];

  variables.forEach((variable) => {
    var info = L.control({ position: "topright" });

    info.onAdd = function () {
      this._div = L.DomUtil.create("div", "info");
      this._div.style.padding = "6px 8px";
      this._div.style.font = "14px/16px Arial, Helvetica, sans-serif";
      this._div.style.background = "white";
      this._div.style.background = "rgba(255,255,255,0.8)";
      this._div.style.boxShadow = "0 0 15px rgba(0,0,0,0.2)";
      this._div.style.borderRadius = "5px";
      this.update();
      return this._div;
    };

    info.update = function (props) {
      this._div.innerHTML = `<h4> ${label} - ${titles[variable]}</h4>` +
        (props
          ? "<b>" + "Census Tract " + props["census_tract"] + "</b><br />" + props[variable] + " " + variableunits[variable]
          : "Hover over a census tract");
    };

    info.addTo(heatmap);
    infoControls[variable] = info;
  });

  // info controls
  Object.values(infoControls).forEach((info) => (info._div.style.display = "none"));
  infoControls[currentVariable]._div.style.display = "block";

  var legend = L.control({ position: "bottomright" });

  legend.onAdd = function () {
    var div = L.DomUtil.create("div", "legend");
    div.innerHTML = "<h4>Legend</h4>";
    return div;
  };

  legend.addTo(heatmap);

  // Function to populate legend
  function updateLegend(scale) {
    var div = legend.getContainer();
    div.innerHTML = "<h4>Legend</h4>";

    for (var i = 0; i < scale.length; i++) {
      var span = document.createElement("span");
      span.innerHTML = scale[i] + (scale[i + 1] ? "&ndash;" + scale[i + 1] + "<br>" : "+");
      var icon = document.createElement("i");
      icon.style.width = "18px";
      icon.style.height = "18px";
      icon.style.float = "left";
      icon.style.marginRight = "8px";
      icon.style.opacity = "0.7";
      icon.style.background = getColor(scale[i] + 1, scale);
      div.appendChild(icon);
      div.appendChild(span);
    }
  }

  fetch(filepath)
    .then((response) => response.json())
    .then((data) => {
      var baseLayers = {}; 
      var defaultLayer;

      //Create base layers
      for (var i = 0; i < variables.length; i++) {
        var variable = variables[i];
        var scale = computeScale(data, variable); 
        var geojson = L.geoJson(data, {
          style: createStyleFunction(variable, scale),
          onEachFeature: function (feature, layer) {
            onEachFeature(feature, layer, variable);
          },
        });
        baseLayers[titles[variable]] = geojson; 

        // Set the default layer to the first variable
        if (i === 0) {
          defaultLayer = geojson;
          updateLegend(scale); 
        }
      }

      if (defaultLayer) {
        defaultLayer.addTo(heatmap);
      }

      // Create a single layer control with radio buttons
      var layerControl = L.control.layers(baseLayers, null, { collapsed: true }).addTo(heatmap);

      // Listen for the layerchange event to update the info box visibility and current variable
      heatmap.on("baselayerchange", function (event) {
        // Hide all info boxes
        Object.values(infoControls).forEach((info) => (info._div.style.display = "none"));
        // Show the selected info box
        currentVariable = titles_reversed[event.name];
        infoControls[currentVariable]._div.style.display = "block";
        // Update the info box with the new layer name
        infoControls[currentVariable].update(null);

        // Update the legend for the new layer
        var scale = computeScale(data, currentVariable);
        updateLegend(scale);
      });
    });

  // Function to create a style function for each variable
  function createStyleFunction(variable, scale) {
    return function (feature) {
      return {
        fillColor: getColor(Number(feature.properties[variable]), scale),
        weight: 2,
        opacity: 1,
        color: "grey",
        dashArray: "1",
        fillOpacity: 0.9,
      };
    };
  }

  // Function to handle feature highlighting
  function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
      weight: 5,
      color: "#666",
      dashArray: "",
      fillOpacity: 0.7,
    });

    layer.bringToFront();
    infoControls[currentVariable].update(layer.feature.properties);
  }

  function resetHighlight(e) {
    var layer = e.target;
    layer.setStyle({
      weight: 2,
      color: "grey",
      dashArray: "1",
      fillOpacity: 0.9,
    });
    infoControls[currentVariable].update(null);
  }


  function zoomToFeature(e) {
    heatmap.fitBounds(e.target.getBounds());
  }

  function onEachFeature(feature, layer, variable) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: zoomToFeature,
    });
  }
}