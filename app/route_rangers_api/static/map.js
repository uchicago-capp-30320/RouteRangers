export function initializeMap(coordinates, stations, iconUrl, routes) {

  // Add a tile layer
  var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    // attribution:
    //   'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, (c) <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: 'abcd',
    minZoom: 8,
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
  }

  var routeNames = {
    0: "(streetcar)",
    1: "(subway)",
    2: "(commuter rail)",
    3: "(bus)",
    6: "(aerial tram)"
  }

  var markers = L.markerClusterGroup({
    disableClusteringAtZoom: 15
  });

  for (var i = 0; i < stations.length; i++) {
    var station = stations[i];
    var x = station[0];
    var y = station[1];
    var stationName = station[2];
    var routeType = routeNames[station[3]];
    var marker = L.marker([x, y], { icon: smallIcon });
    marker.bindTooltip(stationName + '<br>' + routeType);
    markers.addLayer(marker);
  };

  map.addLayer(markers);


  // Add routes layer

  var routesJSON = L.geoJSON(routes, {
    style: function (feature) {
      return {
        color: '#' + feature.properties.color,
        weight: 3,
        "opacity": .7
      };
    },
    onEachFeature: function (feature, layer) {
      layer.bindPopup(feature.properties.route_name);
    }
  });

  map.addLayer(routesJSON);

  // Adjust width of routes with zoom level
  function updateRouteWidth() {
    var zoom = map.getZoom();
    routesJSON.eachLayer(function (layer) {
      layer.setStyle({ weight: (zoom / 4) - 1 });
    });
  }
  map.on("zoom", updateRouteWidth);

  var baseMaps = {
    "base": tileLayer
  }

  var overlayMaps = {
    "Stations": markers,
    "Routes": routesJSON
  };

  var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

};