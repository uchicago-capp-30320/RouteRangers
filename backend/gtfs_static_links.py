# Each of these links contains a static (scheduled) GTFS feed for its relevant
# city/agency, as a set of files that can be downloaded with a click, or read into
# memory using the gtfs_kit library's .read_feed() method [which works on a zipped
# directory saved locally as well]. These scheduled feeds do not require an API key.

### CHICAGO

# note: CTA contains both El train and bus data
CTA_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"

METRA_URL = "https://schedules.metrarail.com/gtfs/schedule.zip"

### NEW YORK
# Source: https://new.mta.info/developers

MTA_SUBWAY_URL = "http://web.mta.info/developers/data/nyct/subway/google_transit.zip"

# Bus data is divided up by borough, with a sixth "MTA Bus Company" feed for
# select lines in Brooklyn/Queens. "shapes.txt" file for each of these is huge
BRONX_BUS_URL = "http://web.mta.info/developers/data/nyct/bus/google_transit_bronx.zip"
BROOKLYN_BUS_URL = (
    "http://web.mta.info/developers/data/nyct/bus/google_transit_brooklyn.zip"
)
MANHATTAN_BUS_URL = (
    "http://web.mta.info/developers/data/nyct/bus/google_transit_manhattan.zip"
)
QUEENS_BUS_URL = (
    "http://web.mta.info/developers/data/nyct/bus/google_transit_queens.zip"
)
STATEN_ISLAND_BUS_URL = (
    "http://web.mta.info/developers/data/nyct/bus/google_transit_staten_island.zip"
)
MTA_BUS_CO_BUS_URL = "http://web.mta.info/developers/data/busco/google_transit.zip"

### PORTLAND

TRIMET_URL = "http://developer.trimet.org/schedule/gtfs.zip"
