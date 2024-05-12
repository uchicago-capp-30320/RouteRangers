
CITIES_CHOICES = {"CHI": "Chicago", "NYC": "New York", "PDX": "Portland"}

# keying by "nospace" naming scheme b/c that is how things will be passed via the url
# TODO this should probably be turned into a dataclass

CITY_CONTEXT = {
    "Chicago": {
        "CityName": "Chicago",
        "City_NoSpace": "Chicago",
        "Coordinates": [41.8781, -87.6298],
        "DB_Name": "CHI",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        'geojsonfilepath': 'ChicagoCensus.geojson'
    },
    "NewYork": {
        "CityName": "New York",
        "City_NoSpace": "NewYork",
        "Coordinates": [40.7128, -74.0060],
        "DB_Name": "NYC",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        'geojsonfilepath': "newyork.geojson"
    },
    "Portland": {
        "CityName": "Portland",
        "City_NoSpace": "Portland",
        "Coordinates": [45.5051, -122.6750],
        "DB_Name": "PDX",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        'geojsonfilepath': 'portland.geojson'
    },
}
