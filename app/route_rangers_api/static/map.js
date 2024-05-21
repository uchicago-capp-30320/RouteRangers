export function initializeMap(coordinates, stations, iconUrl, routes) {

  // Add a tile layer
  var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    // attribution:
    //   'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, (c) <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: 'abcd',
    minZoom: 0,
    maxZoom: 17,
  });

  // Initialize the map at center of city
  var map = L.map('map', { layers: [tileLayer] }).setView(coordinates, 13);

  // Custom icon for smaller markers
  var smallIcon = L.icon({
    iconUrl: iconUrl, // URL to a smaller icon image
    iconSize: [15, 15],
    iconAnchor: [6, 6],
  });

  // Set level of zoom at which each kind of transit stop declusters,
  // based on how spaced apart they usually are
  var zoomEnd = {
    0: 12,
    1: 12,
    2: 10,
    3: 15,
    6: 12
  };

  var routeNames = {
    0: "Streetcar",
    1: "Subway",
    2: "Commuter rail",
    3: "Bus",
    6: "Aerial tram"
  };

  var markerClusterGroups = {};

  // Add stations layers

  L.geoJSON(stations, {
    onEachFeature: function (feature, layer) {
      var x = feature.geometry.coordinates[0];
      var y = feature.geometry.coordinates[1];
      var stationName = feature.properties.station_name;
      var routeType = routeNames[feature.properties.mode];

      var marker = L.marker([x, y], { icon: smallIcon });
      marker.bindTooltip(stationName + '<br>(' + routeType + ')');

      // create new cluster group for each type of route as needed
      if (!markerClusterGroups[routeType]) {
        // This isn't retrieving a valid value from the dictionary
        // to correctly give different transit types different values
        // for disableClusteringonZoom. TODO: fix (low priority)
        var maxZoom = parseInt(zoomEnd[parseInt(routeType, 10)], 10);
        if (isNaN(maxZoom)) {
          maxZoom = 14;
        }
        markerClusterGroups[routeType] = L.markerClusterGroup({
          disableClusteringAtZoom: maxZoom
        });
      }
      markerClusterGroups[routeType].addLayer(marker);
    }
  });

  var markerClustersLayer = L.layerGroup();
  for (var routeType in markerClusterGroups) {
    markerClustersLayer.addLayer(markerClusterGroups[routeType]);
  }
  map.addLayer(markerClustersLayer);


  // Add routes layers

  var routeLayers = {};

  L.geoJSON(routes, {
    style: function (feature) {
      return {
        color: '#' + feature.properties.color,
        weight: 3,
        "opacity": .7
      };
    },
    onEachFeature: function (feature, layer) {
      var routeType = feature.properties.mode;
      var mode = routeNames[routeType];
      if (!routeLayers[mode]) {
        routeLayers[mode] = L.layerGroup();
      }
      routeLayers[mode].addLayer(layer);
      layer.bindPopup(feature.properties.route_name + '<br> (' + mode + ')');
    }
  });

  // Adjust width of routes with zoom level
  function updateRouteWidth() {
    var zoom = map.getZoom();
    for (var rType in routeLayers) {
      routeLayers[rType].eachLayer(function (layer) {
        layer.setStyle({ weight: (zoom / 4) - 1 });
      });
    }
  }

  var baseMaps = {
    "base": tileLayer
  }

  // Initialize layer control

  var overlays = {};

  for (var key in markerClusterGroups) {
    overlays[key + " stops"] = markerClusterGroups[key];
  }
  for (var key in routeLayers) {
    overlays[key + " routes"] = routeLayers[key];
  }

  var layerControl = L.control.layers(baseMaps, overlays).addTo(map);

  map.on("zoom", updateRouteWidth);

};