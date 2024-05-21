function heatmaps(
  filepath,
  coordinates,
  label,
  scale,
  variable,
  colorscale = [
    "#FFEDA0",
    "#FED976",
    "#FEB24C",
    "#FD8D3C",
    "#FC4E2A",
    "#E31A1C",
    "#BD0026",
    "#800026",
  ],
) {
  // file path- expects string
  // coordinates are expected in list form
  // label is our title
  // scale inputs the color scale as a list- highest to lowest.
  // variable expects a key from the feature properties section
  var geojson;
  fetch(filepath)
    .then((response) => response.json())
    .then((data) => {
      var geojson = L.geoJson(data, {
        style: style,
        onEachFeature: onEachFeature,
      }).addTo(heatmap);
    })
    .catch((error) => {
      console.error("Error loading GeoJSON:", error);
    });

  var heatmap = L.map("heatmap").setView(coordinates, 9);
  var geojson;

  var tiles = L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    {
      maxZoom: 19,
      attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    },
  ).addTo(heatmap);

  function getColor(d) {
    return d > scale[6]
      ? colorscale[7]
      : d > scale[5]
        ? colorscale[6]
        : d > scale[4]
          ? colorscale[5]
          : d > scale[3]
            ? colorscale[4]
            : d > scale[2]
              ? colorscale[3]
              : d > scale[1]
                ? colorscale[2]
                : d > scale[0]
                  ? colorscale[1]
                  : colorscale[0];
  }

  function style(feature) {
    return {
      fillColor: getColor(feature.properties[variable]),
      weight: 2,
      opacity: 1,
      color: "white",
      dashArray: "3",
      fillOpacity: 0.7,
    };
  }
  L.geoJson(geojson, { style: style }).addTo(heatmap);

  function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
      weight: 5,
      color: "#666",
      dashArray: "",
      fillOpacity: 0.7,
    });

    layer.bringToFront();
    info.update(layer.feature.properties);
  }

  function resetHighlight(e) {
    geojson.resetStyle(e.target);
    var layer = e.target;
    layer.setStyle({
      weight: 2,
      color: "white",
      dashArray: "3",
      fillOpacity: 0.7,
    });
    info.update();
  }

  function zoomToFeature(e) {
    heatmap.fitBounds(e.target.getBounds());
  }

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: highlightFeature,
      mouseout: resetHighlight,
      click: zoomToFeature,
    });
  }
  geojson = L.geoJson(geojson, {
    style: style,
    onEachFeature: onEachFeature,
  }).addTo(heatmap);
  var info = L.control();

  info.onAdd = function (heatmap) {
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
    this._div.innerHTML =
      `<h4>${label}</h4>` +
      (props
        ? "<b>" +
          props.name +
          "</b><br />" +
          props.density +
          " people / mi<sup>2</sup>"
        : "Hover over a census tract");
  };

  info.addTo(heatmap);

  var legend = L.control({ position: "bottomright" });

  legend.onAdd = function (heatmap) {
    var div = L.DomUtil.create("div"),
      grades = scale;

    div.style.lineHeight = "18px";
    div.style.color = "#555";

    for (var i = 0; i < grades.length; i++) {
      var span = document.createElement("span");
      span.innerHTML =
        grades[i] + (grades[i + 1] ? "&ndash;" + grades[i + 1] + "<br>" : "+");
      var icon = document.createElement("i");
      icon.style.width = "18px";
      icon.style.height = "18px";
      icon.style.float = "left";
      icon.style.marginRight = "8px";
      icon.style.opacity = "0.7";
      icon.style.background = getColor(grades[i] + 1);
      div.appendChild(icon);
      div.appendChild(span);
    }

    return div;
  };

  legend.addTo(heatmap);

  var geojson;
  geojson = L.geoJson(geojson, {
    style: style,
    onEachFeature: onEachFeature,
  }).addTo(heatmap);
}

function loadGeoJSONAndProcess(filepath) {
  fetch(filepath)
    .then((response) => response.json())
    .then((data) => {
      processGeoJSONData(data);
    })
    .catch((error) => {
      console.error("Error loading GeoJSON:", error);
    });
}
