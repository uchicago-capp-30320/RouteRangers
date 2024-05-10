export function initializeMap(coordinates, stations, iconUrl) {
  // Initialize the map with the given coordinates as the center
  var map = L.map('map').setView(coordinates, 13);

  // Add a tile layer
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution:
      'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19,
  }).addTo(map);

  // Custom icon for smaller markers
  var smallIcon = L.icon({
    iconUrl: iconUrl, // URL to a smaller icon image
    iconSize: [12, 12], // Set the icon size you want
    iconAnchor: [6, 6], // Adjust the anchor point if necessary
  });

    // Loop through the stations and add a smaller marker for each
    stations.forEach(function(station) {
        var marker = L.marker([station[0], station[1]], {icon: smallIcon}).addTo(map);
    });

}

//  code to use standard marker
//   stations.forEach(function (station) {
//     L.marker([station[0], station[1]]).addTo(map);
//   });