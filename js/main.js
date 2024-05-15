// Initialize the map centered around Chicago (or city of interest)
const map = L.map('map').setView([41.8781, -87.6298], 13);

// Layer design
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 15,
}).addTo(map);

// Geocoder control
L.Control.geocoder({
    defaultMarkGeocode: false
})
    .on('markgeocode', function(e) {
        const bbox = e.geocode.bbox;
        const poly = L.polygon([
            bbox.getSouthEast(),
            bbox.getNorthEast(),
            bbox.getNorthWest(),
            bbox.getSouthWest()
        ]).addTo(map);
        map.fitBounds(poly.getBounds());
    })
    .on('routesfound', function(e) {
        var routes = e.routes;
        alert('Found ' + routes.length + ' route(s).');
    })
    .addTo(map);

// Routing control
L.Routing.control({
    // waypoints: [
    //     L.latLng(41.8853, -87.6246),
    //     L.latLng(41.7906, -87.6001)
    // ],
    routeWhileDragging: true,
    geocoder: L.Control.Geocoder.nominatim()
    
    })
    .addTo(map);

// // Function to create a button
// function createButton(label, container) {
//     const btn = L.DomUtil.create('button', '', container);
//     btn.setAttribute('type', 'button');
//     btn.innerHTML = label;
//     return btn;
// }

// // Add a click event listener to the map
// map.on('click', function(e) {
//     var container = L.DomUtil.create('div'),
//         startBtn = createButton('Start from this location', container),
//         destBtn = createButton('Go to this location', container);

//     L.popup()
//         .setContent(container)
//         .setLatLng(e.latlng)
//         .openOn(map);

//     // Add event listeners to the buttons
//     L.DomEvent.on(startBtn, 'click', function() {
//         control.spliceWaypoints(0, 1, e.latlng);
//         map.closePopup();
//     });

//     L.DomEvent.on(destBtn, 'click', function() {
//         control.spliceWaypoints(control.getWaypoints().length - 1, 1, e.latlng);
//         map.closePopup();
//     });
// });
