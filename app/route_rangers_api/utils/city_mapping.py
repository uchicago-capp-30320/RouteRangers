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
        "geojsonfilepath": "ChicagoCensus.geojson",
    },
    "NewYork": {
        "CityName": "New York",
        "City_NoSpace": "NewYork",
        "Coordinates": [40.7128, -74.0060],
        "DB_Name": "NYC",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        "geojsonfilepath": "newyork.geojson",
    },
    "Portland": {
        "CityName": "Portland",
        "City_NoSpace": "Portland",
        "Coordinates": [45.5051, -122.6750],
        "DB_Name": "PDX",
        "csv": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/barplot_change_data.csv",
        "lineplot": "https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/data_connectedscatter.csv",
        "geojsonfilepath": "portland.geojson",
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

MODES_OF_TRANIST = {
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
}

TIME_OF_DAY = {1: "Peak commute hours", 2: "Daytime", 3: "Nighttime"}

BOOL_CHOICES = {1: "Yes", 2: "No"}

SATISFIED = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5"}


CARD_DATA = {
    "Bus": {
        "Fall": {
            "Weekdays": {
                "TotalRiders": 5000,
                "TotalRoutes": 30,
                "AverageCommuteTime": "45 minutes",
            },
            "Weekends": {
                "TotalRiders": 6000,
                "TotalRoutes": 35,
                "AverageCommuteTime": "50 minutes",
            },
        },
        "Winter": {
            "Weekdays": {
                "TotalRiders": 5500,
                "TotalRoutes": 32,
                "AverageCommuteTime": "48 minutes",
            },
            "Weekends": {
                "TotalRiders": 5800,
                "TotalRoutes": 33,
                "AverageCommuteTime": "47 minutes",
            },
        },
        "Spring": {
            "Weekdays": {
                "TotalRiders": 6200,
                "TotalRoutes": 37,
                "AverageCommuteTime": "52 minutes",
            },
            "Weekends": {
                "TotalRiders": 1,
                "TotalRoutes": 2,
                "AverageCommuteTime": "3 minutes",
            },
        },
        "Summer": {
            "Weekdays": {
                "TotalRiders": 4,
                "TotalRoutes": 5,
                "AverageCommuteTime": "6 minutes",
            },
            "Weekends": {
                "TotalRiders": 7,
                "TotalRoutes": 8,
                "AverageCommuteTime": "9 minutes",
            },
        },
    },
    "Train": {
        "Fall": {
            "Weekdays": {
                "TotalRiders": 50020,
                "TotalRoutes": 320,
                "AverageCommuteTime": "415 minutes",
            },
            "Weekends": {
                "TotalRiders": 60100,
                "TotalRoutes": 315,
                "AverageCommuteTime": "510 minutes",
            },
        },
        "Winter": {
            "Weekdays": {
                "TotalRiders": 51500,
                "TotalRoutes": 312,
                "AverageCommuteTime": "418 minutes",
            },
            "Weekends": {
                "TotalRiders": 5100,
                "TotalRoutes": 33,
                "AverageCommuteTime": "417 minutes",
            },
        },
        "Spring": {
            "Weekdays": {
                "TotalRiders": 62010,
                "TotalRoutes": 317,
                "AverageCommuteTime": "512 minutes",
            },
            "Weekends": {
                "TotalRiders": 11,
                "TotalRoutes": 21,
                "AverageCommuteTime": "31 minutes",
            },
        },
        "Summer": {
            "Weekdays": {
                "TotalRiders": 41,
                "TotalRoutes": 51,
                "AverageCommuteTime": "6 minutes",
            },
            "Weekends": {
                "TotalRiders": 71,
                "TotalRoutes": 81,
                "AverageCommuteTime": "91 minutes",
            },
        },
    },
    "all": {
        "all": {
            "all": {
                "TotalRiders": 71,
                "TotalRoutes": 81,
                "AverageCommuteTime": "91 minutes",
            }
        }
    },
}
