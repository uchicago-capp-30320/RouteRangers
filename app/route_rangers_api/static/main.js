function initializeUserRoute(coordinates) {
    
    // Helper Function: route to GeoJSON, LineString 
    (function() {
        'use strict';
        L.Routing = L.Routing || {};
        L.Routing.routeToGeoJson = function(route) {
            var wpNames = [],
                wpCoordinates = [],
                i,
                wp,
                latLng;
            for (i = 0; i < route.waypoints.length; i++) {
                wp = route.waypoints[i];
                latLng = L.latLng(wp.latLng);
                wpNames.push(wp.name);
                wpCoordinates.push([latLng.lng, latLng.lat]);
            }
            return {
                type: 'FeatureCollection',
                features: [
                    {
                        type: 'Feature',
                        properties: {
                            id: 'waypoints',
                            names: wpNames
                        },
                        geometry: {
                            type: 'MultiPoint',
                            coordinates: wpCoordinates
                        }
                    },
                    {
                        type: 'Feature',
                        properties: {
                            id: 'line',
                        },
                        geometry: L.Routing.routeToLineString(route)
                    }
                ]
            };
        };
        L.Routing.routeToLineString = function(route) {
            var lineCoordinates = [],
                i,
                latLng;
            for (i = 0; i < route.coordinates.length; i++) {
                latLng = L.latLng(route.coordinates[i]);
                lineCoordinates.push([latLng.lng, latLng.lat]);
            }
            return {
                type: 'LineString',
                coordinates: lineCoordinates
            };
        };
    })();

    // Helper Function: export route in linestring format
    function addExportButton(lineStringGeometry) {
        const buttonContainer = document.querySelector('.leaflet-routing-container');
        if (buttonContainer) {
            if (!exportButton) {
                exportButton = document.createElement('button');
                exportButton.className = 'leaflet-bar export-button';
                exportButton.innerText = 'Export Route';
                buttonContainer.appendChild(exportButton);
            }
            // Remove existing event listener, add new
            exportButton.replaceWith(exportButton.cloneNode(true));
            exportButton = document.querySelector('.export-button');
            exportButton.addEventListener('click', function() {
                alert('LineString: ' + JSON.stringify(lineStringGeometry.coordinates));
            });
        } else {
            setTimeout(() => addExportButton(lineStringGeometry), 60);
        }
    }

    // Initialize map at center of city
    var map = L.map('map').setView(coordinates, 13);

    // Layer design
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 15,
    }).addTo(map);

    // Declare variables
    let control;
    let currentRoute;
    let exportButton;

    // Geocoder setup
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
    .addTo(map);

    // Control setup
    control = L.Routing.control({
        plan: new L.Routing.Plan([], {
            createMarker: function(i, wp) {
                return L.marker(wp.latLng, {
                    draggable: true
                });
            },
            geocoder: L.Control.Geocoder.nominatim(),
            reverseWaypoints: true
        }),
        routeWhileDragging: true
    })
    .on('routesfound', function(e) {
        const route = e.routes[0];
        const geoJson = L.Routing.routeToGeoJson(route);
        const lineString = geoJson.features.find(feature => feature.geometry.type === 'LineString');
        
        // If previous route exists, clear it
        if (currentRoute) {
            map.removeLayer(currentRoute);
        }

        // Add LineString to map
        currentRoute = L.Routing.line(route, {
            addWaypoints: false
        });
        currentRoute.addTo(map);

        // Update export button functionality to show LineString
        addExportButton(lineString.geometry);
    })
    .addTo(map);

    // Clear previous route if reverse button is clicked
    map.on('routingstart', function() {
        if (currentRoute) {
            map.removeLayer(currentRoute);
            currentRoute = null;
        }
    });

    // Add export route button
    addExportButton();
}



// export function initializeUserRoute(coordinates){
//     // Helper Function: route to GeoJSON, LineString 
//     (function() {
//         'use strict';
//         L.Routing = L.Routing || {};
//         L.Routing.routeToGeoJson = function(route) {
//             var wpNames = [],
//                 wpCoordinates = [],
//                 i,
//                 wp,
//                 latLng;
//             for (i = 0; i < route.waypoints.length; i++) {
//                 wp = route.waypoints[i];
//                 latLng = L.latLng(wp.latLng);
//                 wpNames.push(wp.name);
//                 wpCoordinates.push([latLng.lng, latLng.lat]);
//             }
//             return {
//                 type: 'FeatureCollection',
//                 features: [
//                     {
//                         type: 'Feature',
//                         properties: {
//                             id: 'waypoints',
//                             names: wpNames
//                         },
//                         geometry: {
//                             type: 'MultiPoint',
//                             coordinates: wpCoordinates
//                         }
//                     },
//                     {
//                         type: 'Feature',
//                         properties: {
//                             id: 'line',
//                         },
//                         geometry: L.Routing.routeToLineString(route)
//                     }
//                 ]
//             };
//         };
//         L.Routing.routeToLineString = function(route) {
//             var lineCoordinates = [],
//                 i,
//                 latLng;
//             for (i = 0; i < route.coordinates.length; i++) {
//                 latLng = L.latLng(route.coordinates[i]);
//                 lineCoordinates.push([latLng.lng, latLng.lat]);
//             }
//             return {
//                 type: 'LineString',
//                 coordinates: lineCoordinates
//             };
//         };
//     })();
//     // Helper Function: export route in linestring format
//     function addExportButton(lineStringGeometry) {
//         const buttonContainer = document.querySelector('.leaflet-routing-container');
//         if (buttonContainer) {
//             if (!exportButton) {
//                 exportButton = document.createElement('button');
//                 exportButton.className = 'leaflet-bar export-button';
//                 exportButton.innerText = 'Export Route';
//                 buttonContainer.appendChild(exportButton);
//             }        
//             // Remove existing event listener, add new
//             exportButton.replaceWith(exportButton.cloneNode(true));
//             exportButton = document.querySelector('.export-button');
//             exportButton.addEventListener('click', function() {
//                 alert('LineString: ' + JSON.stringify(lineStringGeometry.coordinates));
//             });
//         } else {
//             setTimeout(() => addExportButton(lineStringGeometry), 60);
//         }
//     }
//     // Initialize map at center of city
//     var map = L.map('map').setView(coordinates, 13);
//     // Layer design
//     L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
//         maxZoom: 15,
//     })
//     .addTo(map);
//     // Declare variables
//     let control;
//     let currentRoute;
//     let exportButton;
//     // Geocoder setup
//     L.Control.geocoder({
//         defaultMarkGeocode: false
//     })
//     .on('markgeocode', function(e) {
//             const bbox = e.geocode.bbox;
//             const poly = L.polygon([
//                 bbox.getSouthEast(),
//                 bbox.getNorthEast(),
//                 bbox.getNorthWest(),
//                 bbox.getSouthWest()
//             ]).addTo(map);
//             map.fitBounds(poly.getBounds());
//     })
//     .addTo(map);
//     // Control setup
//     control = L.Routing.control({
//         plan: new L.Routing.Plan([], {
//             createMarker: function(i, wp) {
//                 return L.marker(wp.latLng, {
//                     draggable: true
//                 });
//             },
//             geocoder: L.Control.Geocoder.nominatim(),
//             reverseWaypoints: true
//         }),
//         routeWhileDragging: true
//     })
//     .on('routesfound', function(e) {
//         const route = e.routes[0];
//         const geoJson = L.Routing.routeToGeoJson(route);
//         const lineString = geoJson.features.find(feature => feature.geometry.type === 'LineString');
//         // If previous route exists, clear
//         if (currentRoute) {
//             map.removeLayer(currentRoute);
//         }
//         // Add LineString to map
//         currentRoute = L.Routing.line(route, {
//             addWaypoints: false
//         });
//         currentRoute.addTo(map);
//         // Update export button functionality to show LineString (CHANGE LATER)
//         addExportButton(lineString.geometry);
//     })
//     .addTo(map);
//     // Clear previous route if reverse button is clicked
//     map.on('routingstart', function() {
//         if (currentRoute) {
//             map.removeLayer(currentRoute);
//             currentRoute = null;
//         }
//     });
//     // Add export route button
//     addExportButton();


// }