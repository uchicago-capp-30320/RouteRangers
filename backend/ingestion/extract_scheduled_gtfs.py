### Imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import gtfs_kit as gk
import re

### Constants

# Each of these links contains a static (scheduled) GTFS feed for its relevant
# city/agency, as a set of files that can be downloaded with a click, or read into
# memory using the gtfs_kit library's .read_feed() method [which works on a zipped
# directory saved locally as well]. These scheduled feeds do not require an API key.

## CHICAGO
# note: CTA contains both El train and bus data
CTA_URL = "https://www.transitchicago.com/downloads/sch_data/google_transit.zip"
METRA_URL = "https://schedules.metrarail.com/gtfs/schedule.zip"

## NEW YORK
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

## PORTLAND
TRIMET_URL = "http://developer.trimet.org/schedule/gtfs.zip"


ALL_PILOT_CITY_URLS = [
    CTA_URL,
    METRA_URL,
    MTA_SUBWAY_URL,
    BRONX_BUS_URL,
    BROOKLYN_BUS_URL,
    MANHATTAN_BUS_URL,
    QUEENS_BUS_URL,
    STATEN_ISLAND_BUS_URL,
    MTA_BUS_CO_BUS_URL,
    TRIMET_URL,
]

URL_TO_CITY = {
    "https://www.transitchicago.com/": {"City": "Chicago", "Agency": "CTA"},
    "https://schedules.metrarail.com/": {"City": "Chicago", "Agency": "Metra"},
    "http://web.mta.info/": {"City": "New York", "Agency": "MTA"},
    "http://developer.trimet.org/": {"City": "Portland", "Agency": "Trimet"},
}

FILE_TO_PRIMARY_KEY = {
    # Primary keys as defined in GTFS standard guide
    # https://gtfs.org/schedule/reference/#stopstxt
    # TODO: Question -- do we want to create a new primary key that concatenates
    # city and agency information, or just do JOINs that add city and agency
    # to the ON condition to make sure all JOINs are within a city-agency system?
    "routes": ("route_id"),
    "trips": ("trip_id"),
    "stops": ("stop_id"),
    "stop_times": ("trip_id", "stop_sequence"),
    "shapes": ("shape_id", "shape_pt_sequence"),
    "transfers": (
        "from_stop_id",
        "to_stop_id",
        "from_trip_id",
        "to_trip_id",
        "from_route_id",
        "to_route_id",
    ),
    "shape_geometries": ("route_id"),  # speculative
}

### Functions

# TODO: write a test for every function as you write it


# ingest_transit_data()
# use gtfs_kit to read in feed URL as object or collection of DataFrames (can you store dataframes in a dict?)
def ingest_gtfs_feed(feed_url: str) -> tuple:
    """
    Use gtfs_kit library to ingest the most up-to-date scheduled (static) GTFS
    data from a particular URL, and return each component file as a GeoDataFrame.
    """
    url_base = re.findall(r"https?:\/\/[^\/]+\/", feed_url)[0]
    feed_city = URL_TO_CITY[url_base]["City"]
    feed_agency = URL_TO_CITY[url_base]["Agency"]
    feed = gk.read_feed(feed_url, dist_units="km")  # dist_units TBD
    # feed.validate() <-- gives "TypeError: strptime() argument 1 must be str, not int"
    # when called on METRA_URL. TODO: investigate/debug further

    return feed_city, feed_agency, feed


# give each DataFrame a city_id column and a system_route_id column (to disambiguate routes named "1" for example)
def get_gtfs_component_dfs(
    feed_city: str, feed_agency: str, feed
) -> dict[pd.DataFrame | gpd.GeoDataFrame]:
    """
    Take in a city name, an agency name, and the results of reading in a GTFS
    feed with gtfs_kit. Isolate each component of the feed as its own GeoDataFrame.
    Add extra columns to each component object

    Should be called directly on output of ingest_gtfs_feed() above.
    """
    routes = feed.routes
    trips = feed.trips
    stops = feed.stops
    stop_times = feed.stop_times
    shapes = feed.shapes

    gtfs_dataframe_dict = {
        "routes": routes,
        "trips": trips,
        "stops": stops,
        "stop_times": stop_times,
        "shapes": shapes,
    }
    # Some systems have a "transfers.txt" file; others don't.
    # gtfs_kit will initialize the feed.transfers attribute as None if no such file exists
    if feed.transfers is not None:
        transfers = feed.transfers
        gtfs_dataframe_dict["transfers"] = transfers
    else:
        print(
            # Question: if we only need feed city and agency for these warnings,
            # do we strictly need to pass it in here, or should we not bother?
            f"Warning: {feed_city} {feed_agency} GTFS feed has no transfers.txt file."
        )

    # The gtfs_kit library's geometrize_routes() method breaks on some of our feeds.
    # That method is itself called by the map_routes() method that outputs a line map
    # on Folium, so fixing the issue or finding an alternative may be a priority later.
    try:
        shape_geometries = gk.routes.geometrize_routes(feed)
        gtfs_dataframe_dict["shape_geometries"] = shape_geometries
    except:
        print(
            f"Warning: gtfs_kit library failed to geometrize {feed_city} {feed_agency} feed shapes.txt"
        )
        print(
            "Consider running a function to generate those linestrings from shapes.txt table in Postgres"
        )

    return gtfs_dataframe_dict


def add_extra_columns(
    feed_city: str, feed_agency: str, feed_component: pd.DataFrame | gpd.GeoDataFrame
) -> pd.DataFrame | gpd.GeoDataFrame:
    """
    Add additional columns to disambiguate city and agency in case there are any
    duplicate names for routes, stops, etc. in multiple cities. This will ensure
    that all rows of data for a particular kind of feature (row, stop, etc.) can
    live in the same table in Postgres irrespective of which city they came from
    originally, reducing the total number of tables required.
    """
    print(feed_component.columns)
    # TODO: Question: can I force these to be the leftmost columns?
    # Would this mess up gtfs_kit i.e. do underlying functions index to a column
    # position rather than a name?
    feed_component.loc[:, "city"] = feed_city
    feed_component.log[:, "agency"] = feed_agency
    # TODO: decide whether we need a new primary key or just add city/agency to JOINs
    # after the fact.
    # If the former, figure out how to pass in the proper primary key column name given
    # which component of GTFS feed the input GeoDataFrame came from.
    # This may involve inference based on the full set of component columns,
    # or referencing FILE_TO_PRIMARY_KEY above, or both
    # For now, leaving it as is

    # TODO: feed_component.loc[:,"last_updated"] = datetime.now() in some format.
    # In a "real" application,
    # Perhaps call that from outside the function and pass it in so it's the
    # same for all entries from a particular GTFS feed as it gets processed

    # TODO: convert lat/long columns to Django and Postgres-compatible Point() objects
    # if present

    # TODO: miscellaneous cleanup (one thing: standardize CTA route names to
    # standard English words for colors
    # TODO: Consider adding a # sign to color column (or see if Postgres has a color data type)
    return feed_component


def combine_different_feeds(
    feed_url_list: list[str], output_folder: None | str = None
) -> dict[pd.DataFrame | gpd.GeoDataFrame]:
    """
    Run the entire GTFS ingestion pipeline for multiple endpoint URLs.

    Optional parameter output_folder
    """
    # TODO: initialize empty dataframes with the proper columns to concat to
    all_routes = None
    all_trips = None
    all_stops = None
    all_stop_times = None
    all_shapes = None
    all_transfers = None
    all_shape_geometries = None

    for this_url in feed_url_list:
        this_city, this_agency, this_feed = ingest_gtfs_feed(this_url)
        these_gtfs_dataframes = {
            name: add_extra_columns(this_city, this_agency, df)
            for name, df in get_gtfs_component_dfs(
                this_city, this_agency, this_feed
            ).items()
        }

    for name, df in these_gtfs_dataframes.items():
        # TODO: this in a  more programmatic way
        if name == "routes":
            all_routes = pd.concat(all_routes, df)
        elif name == "trips":
            all_trips = pd.concat(all_trips, df)
        elif name == "stops":
            all_stops = pd.concat(all_stops, df)
        elif name == "stop_times":
            all_stop_times = pd.concat(all_stop_times, df)
        elif name == "shapes":
            all_shapes = pd.concat(all_shapes, df)
        elif name == "transfers":
            all_transfers = pd.concat(all_transfers, df)
        elif name == "shape_geometries":
            all_shape_geometries = pd.concat(all_shape_geometries, df)

    all_dfs = {
        "routes": all_routes,
        "trips": all_trips,
        "stops": all_stops,
        "stop_times": all_stop_times,
        "shapes": all_shapes,
        "transfers": all_transfers,
        "shape_geometries": all_shape_geometries,
    }

    if output_folder is not None:
        for name, df in all_dfs.items():
            pd.to_csv(df, f"{output_folder}/{name}.csv")

    return all_dfs


# TODO: function for feeding data into Django and/or Postgres


if __name__ == "__main__":
    print(f"Getting feed from {METRA_URL}...")
    feed_city, feed_agency, feed = ingest_gtfs_feed(METRA_URL)
    feed_dict = get_gtfs_component_dfs(feed_city, feed_agency, feed)
    print(feed_dict)
    # TODO: BUILD UP TO:
    # gtfs_data_for_postgres = combine_different_feeds(ALL_PILOT_CITY_URLS)
    # TODO: send this data into Postgres (or at least into thing that sends it
    # into Postgres), CREATE-ing the relevant table if it doesn't exist, and
    # UPDATE-ing it if not
    # (if data feature enabled, overwrite rows where some number of keys match
    # with new data and new date, rather than appending new)
