// Initialize the map centered around Chicago (or city of interest)
map = L.map('map').setView([41.8781, -87.6298], 13);

// Layer design
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
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

// Export route button
function addExportButton() {
    const buttonContainer = document.querySelector('.leaflet-routing-container');
    if (buttonContainer) {
        const exportButton = document.createElement('button');
        exportButton.className = 'leaflet-bar export-button';
        exportButton.innerText = 'Export Route';
        exportButton.addEventListener('click', function() {
            const waypoints = control.getWaypoints().map(wp => ({
                lat: wp.latLng.lat,
                lng: wp.latLng.lng
            }));

            fetch('https://your-backend-endpoint/api/route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ waypoints })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Route exported successfully:', data);
            })
            .catch(error => {
                console.error('Error exporting route:', error);
            });
        });
        buttonContainer.appendChild(exportButton);
    } else {
        setTimeout(addExportButton, 60);
    }
}
addExportButton();
