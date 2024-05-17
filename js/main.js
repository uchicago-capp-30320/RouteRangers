// Initialize the map centered around Chicago (or city of interest)
map = L.map('map').setView([41.8781, -87.6298], 13);

// Layer design
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 15,
}).addTo(map);

// Geocoder control
L.Control.geocoder({
    defaultMarkGeocode: false
})
    .on('markgeocode', function(e) {
        bbox = e.geocode.bbox;
        poly = L.polygon([
            bbox.getSouthEast(),
            bbox.getNorthEast(),
            bbox.getNorthWest(),
            bbox.getSouthWest()
        ]).addTo(map);
        map.fitBounds(poly.getBounds());
    })
    .on('routesfound', function(e) {
        routes = e.routes;
        alert('Found ' + routes.length + ' route(s).');
    })
    .addTo(map);

// Routing control
L.Routing.control({
    plan: new L.Routing.Plan([], {
        createMarker: function(i, wp) {
            return L.marker(wp.latLng, {
                draggable: true
            });
        },
        geocoder: L.Control.Geocoder.nominatim(),
        reverseWaypoints: true
    }),
    routeWhileDragging: true,
}).addTo(map);

