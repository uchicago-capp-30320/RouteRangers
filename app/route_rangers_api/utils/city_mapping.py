CITIES_CHOICES = {"CHI": "Chicago", "NYC": "New York", "PDX": "Portland"}

# keying by "nospace" naming scheme b/c that is how things will be passed via the url
# TODO this should probably be turned into a dataclass

CITY_CONTEXT = {
    "Chicago": {
        "CityName": "Chicago",
        "City_NoSpace": "Chicago",
        "Coordinates": [41.8781, -87.6298],
    },
    "NewYork": {
        "CityName": "New York",
        "City_NoSpace": "NewYork",
        "Coordinates": [40.7128, -74.0060],
    },
    "Portland": {
        "CityName": "Portland",
        "City_NoSpace": "Portland",
        "Coordinates": [45.5051, -122.6750],
    },
}
