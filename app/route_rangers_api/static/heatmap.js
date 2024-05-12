function heatmaps(filepath, coordinates, label) {
    var geojson
    fetch(filepath)
    .then(response => response.json())
    .then(data => {
        var geojson = L.geoJson(data, {
            style: style,
            onEachFeature: onEachFeature
        }).addTo(heatmap);
    })
    .catch(error => {
        console.error('Error loading GeoJSON:', error);
    });

    var heatmap = L.map('heatmap').setView(coordinates, 9);
    var geojson;

    var tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(heatmap);

    function getColor(d) {
        return d > 1000 ? '#800026' :
               d > 500  ? '#BD0026' :
               d > 200  ? '#E31A1C' :
               d > 100  ? '#FC4E2A' :
               d > 50   ? '#FD8D3C' :
               d > 20   ? '#FEB24C' :
               d > 10   ? '#FED976' :
                          '#FFEDA0';
    }

    function style(feature) {
        return {
            fillColor: getColor(feature.properties.density),
            weight: 2,
            opacity: 1,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
        };
    }
    L.geoJson(geojson, {style: style}).addTo(heatmap);

    function highlightFeature(e) {
        var layer = e.target;

        layer.setStyle({
            weight: 5,
            color: '#666',
            dashArray: '',
            fillOpacity: 0.7
        });

        layer.bringToFront();
        info.update(layer.feature.properties);
    }

    function resetHighlight(e) {
        geojson.resetStyle(e.target);
        var layer = e.target;
        layer.setStyle({
            weight: 2,
            color: 'white',
            dashArray: '3',
            fillOpacity: 0.7
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
            click: zoomToFeature
        });
    }
    geojson = L.geoJson(geojson, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(heatmap);
    var info = L.control();

    info.onAdd = function (heatmap) {
        this._div = L.DomUtil.create('div', 'info');
        this._div.style.padding = '6px 8px';
        this._div.style.font = '14px/16px Arial, Helvetica, sans-serif';
        this._div.style.background = 'white';
        this._div.style.background = 'rgba(255,255,255,0.8)';
        this._div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';
        this._div.style.borderRadius = '5px';
        this.update();
        return this._div;
    };

    info.update = function (props) {
        this._div.innerHTML = `<h4>${label}</h4>` + (props ?
            '<b>' + props.name + '</b><br />' + props.density + ' people / mi<sup>2</sup>'
            : 'Hover over a census block');
    };

    info.addTo(heatmap);

    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (heatmap) {
        var div = L.DomUtil.create('div'),
            grades = [0, 10, 20, 50, 100, 200, 500, 1000];

        div.style.lineHeight = '18px';
        div.style.color = '#555';

        for (var i = 0; i < grades.length; i++) {
            var span = document.createElement('span');
            span.innerHTML = grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
            var icon = document.createElement('i');
            icon.style.width = '18px';
            icon.style.height = '18px';
            icon.style.float = 'left';
            icon.style.marginRight = '8px';
            icon.style.opacity = '0.7';
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
        onEachFeature: onEachFeature
    }).addTo(heatmap);
}


function loadGeoJSONAndProcess(filepath) {
    fetch(filepath)
      .then(response => response.json())
      .then(data => {
        processGeoJSONData(data);
      })
      .catch(error => {
        console.error('Error loading GeoJSON:', error);
      });
  }