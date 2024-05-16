export function initializeMap(coordinates, stations, iconUrl, routes) {

  // Add a tile layer
  var tileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    // attribution:
    //   'Map data (c) <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, (c) <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  });

  // Initialize the map at center of city
  var map = L.map('map', { layers: [tileLayer] }).setView(coordinates, 13);

  // Custom icon for smaller markers
  var smallIcon = L.icon({
    iconUrl: iconUrl, // URL to a smaller icon image
    iconSize: [15, 15],
    iconAnchor: [6, 6],
  });

  var markers = L.markerClusterGroup({
    disableClusteringAtZoom: 16
  });

  for (var i = 0; i < stations.length; i++) {
    var station = stations[i];
    var marker = L.marker([station[0], station[1]], { icon: smallIcon });
    marker.bindTooltip(station[2]);
    // console.log(station[2]);
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

  var baseMaps = {
    "base": tileLayer
  }

  var overlayMaps = {
    "Stations": markers,
    "Routes": routesJSON
  };

  var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

};