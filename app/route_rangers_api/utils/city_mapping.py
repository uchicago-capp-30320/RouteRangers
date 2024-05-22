CITIES_CHOICES = {"CHI": "Chicago", "NYC": "New York", "PDX": "Portland"}
CITIES_CHOICES_SURVEY = {"Chicago": "CHI", "NewYork": "NYC", "Portland": "PDX"}
# keying by "nospace" naming scheme b/c that is how things will be passed via the url
# TODO this should probably be turned into a dataclass

CITY_FIPS = {
    "nyc": {"state": "36", "county": ["061", "047", "081", "005", "085"]},
    "chicago": {"state": "17", "county": ["031"]},
    "portland": {"state": "41", "county": ["051"]},
}

CITY_CONTEXT = {
    "Chicago": {
        "CityName": "Chicago",
        "City_NoSpace": "Chicago",
        "Coordinates": [41.8781, -87.6298],
        "DB_Name": "CHI",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        "geojsonfilepath": "ChicagoCensus_2020.geojson",
        "fips_county": CITY_FIPS["chicago"]["county"],
    },
    "NewYork": {
        "CityName": "New York",
        "City_NoSpace": "NewYork",
        "Coordinates": [40.7128, -74.0060],
        "DB_Name": "NYC",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        "geojsonfilepath": "NewYorkCensus_2020.geojson",
        "fips_county": CITY_FIPS["nyc"]["county"],
    },
    "Portland": {
        "CityName": "Portland",
        "City_NoSpace": "Portland",
        "Coordinates": [45.5051, -122.6750],
        "DB_Name": "PDX",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        "geojsonfilepath": "PortlandCensus_2020.geojson",
        "fips_county": CITY_FIPS["portland"]["county"],
    },
}

TRIP_FREQ = {
    1: "Everyday",
    2: "Weekdays",
    3: "Weekends",
    4: "A few times per week",
    5: "A few times per month",
    6: "A few times per year",
}

MODES_OF_TRANSIT = {
    1: "Bus",
    2: "Train",
    3: "Car",
    4: "Bike",
    5: "Walking",
    6: "Rideshare",
}

SWITCH_TO_TRANSIT = {
    1: "There are stops near you",
    2: "There are many scheduled departures",
    3: "It doesn't take significantly longer than driving",
    4: "There are enough seats for all riders",
    5: "It feels safe at the station and onboard",
    6: "It will save me money",
    7: "I would not be willing to switch to transit",
}

TRANSIT_IMPROVEMENT = {
    1: "More frequent service",
    2: "More accurate schedule times",
    3: "Fewer transfers or a more direct route",
    4: "It feels safe at the station and onboard",
    5: "No improvement needed",
}

TIME_OF_DAY = {1: "Peak commute hours", 2: "Daytime", 3: "Nighttime"}

BOOL_CHOICES = {1: "Yes", 2: "No"}

SATISFIED = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}

CITY_RIDERSHIP_LEVEL = {
    "Portland": {"bus": "stations", "subway": "stations"},
    "Chicago": {"bus": "route", "subway": "stations"},
    "NewYork": {"bus": "route", "subway": "stations"},
}
