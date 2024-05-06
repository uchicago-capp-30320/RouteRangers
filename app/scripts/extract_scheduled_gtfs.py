### Imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import gtfs_kit as gk
import re
from datetime import datetime

import pdb


from django.contrib.gis.geos import GEOSGeometry, LineString, Point
from route_rangers_api.models import TransitStation, TransitRoute


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
    "https://www.transitchicago.com/": {"City": "CHI", "Agency": "CTA"},
    "https://schedules.metrarail.com/": {"City": "CHI", "Agency": "Metra"},
    "http://web.mta.info/": {"City": "NYC", "Agency": "MTA"},
    "http://developer.trimet.org/": {"City": "PDX", "Agency": "TRIMET"},
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


def get_gtfs_feed(feed_url: str) -> tuple:
    """
    Use gtfs_kit library to obtain the most up-to-date scheduled (static) GTFS
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
    feed_city: str, feed
) -> dict[pd.DataFrame | gpd.GeoDataFrame]:
    """
    Take in a city name and the results of reading in a GTFS
    feed with gtfs_kit. Isolate each component of the feed as its own GeoDataFrame.
    Add extra columns to each component object

    Should be called directly on output of get_gtfs_feed() above.
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
            f"Warning: this {feed_city} GTFS feed has no transfers.txt file."
        )

    # The gtfs_kit library's geometrize_routes() method breaks on some of our feeds.
    # That method is itself called by the map_routes() method that outputs a line map
    # on Folium, so fixing the issue or finding an alternative may be a priority later.
    try:
        shape_geometries = gk.routes.geometrize_routes(feed)
        gtfs_dataframe_dict["shape_geometries"] = shape_geometries
    except:
        print(
            f"Warning: gtfs_kit library failed to geometrize this {feed_city} feed shapes.txt"
        )
        print(
            "Consider running a function to generate those linestrings from shapes.txt table in Postgres"
        )

    return gtfs_dataframe_dict


def add_extra_columns(
    feed_city: str, feed_component: pd.DataFrame | gpd.GeoDataFrame
) -> pd.DataFrame | gpd.GeoDataFrame:
    """
    Add additional columns city and time of update in case there are any
    duplicates for routes, stops, etc. in multiple cities.
    """
    orig_columns = feed_component.columns
    feed_component.loc[:, "city"] = feed_city
    # Static feeds may be scraped on a schedule; system should preserve for users
    # how recent the data is
    NOW = datetime.now()
    feed_component.loc[:, "last_updated"] = NOW
    # Perhaps pass NOW in from outside the function, so it's the same for all entries
    # from a particular GTFS feed as it gets processed

    # TODO: miscellaneous cleanup (one thing: standardize CTA route names to
    # standard English words for colors)
    # TODO: Consider adding a # sign to color column (or see if Postgres has a
    # color data type)
    return feed_component


def combine_different_feeds(
    feed_url_list: list[str], output_folder: None | str = None
) -> dict[pd.DataFrame | gpd.GeoDataFrame]:
    """
    Run the entire GTFS ingestion pipeline for multiple endpoint URLs.
    TODO: consider allowing this to take an arbitrary list of *args rather than
    a list.

    Optional parameter output_folder allows for saving results to file storage.
    """
    # This doesn't seem to require initailizing empty dataframes with the proper
    # columns to concat to -- it'll take those from the first dataframe processed
    all_routes = None
    all_trips = None
    all_stops = None
    all_stop_times = None
    all_shapes = None
    all_transfers = None
    all_shape_geometries = None

    for this_url in feed_url_list:
        this_city, this_agency, this_feed = get_gtfs_feed(this_url)
        print(f"{this_city} {this_agency} feed ingested")
        these_gtfs_dataframes = {
            name: add_extra_columns(this_city, df)
            for name, df in get_gtfs_component_dfs(this_city, this_feed).items()
        }

        for name, df in these_gtfs_dataframes.items():
            # TODO: this in a  more programmatic way
            if name == "routes":
                all_routes = pd.concat([all_routes, df])
            elif name == "trips":
                all_trips = pd.concat([all_trips, df])
            elif name == "stops":
                all_stops = pd.concat([all_stops, df])
            elif name == "stop_times":
                all_stop_times = pd.concat([all_stop_times, df])
            elif name == "shapes":
                all_shapes = pd.concat([all_shapes, df])
            elif name == "transfers":
                all_transfers = pd.concat([all_transfers, df])
            elif name == "shape_geometries":
                all_shape_geometries = pd.concat([all_shape_geometries, df])
        print(f"{this_city} {this_agency} dataframes concatenated to whole")
    # end for

    all_dfs = {
        "routes": all_routes,
        "trips": all_trips,
        "stops": all_stops,
        "stop_times": all_stop_times,
        "shapes": all_shapes,
        "transfers": all_transfers,
        "shape_geometries": all_shape_geometries,
    }

    print(all_dfs)

    if output_folder is not None:
        for name, df in all_dfs.items():
            pd.to_csv(df, f"{output_folder}/{name}.csv")

    return all_dfs


def ingest_transit_stations(
    stops: pd.DataFrame | gpd.GeoDataFrame,
    date=datetime.date,
    transit_mode=2,  # TODO: Undo hard-code -- should be 2 for Metra
    # 0 for Trimet streetcar, 1 for subway train, and 3 for bus
) -> None:
    """Feed a DataFrame of stops into Postgres as TransitStation objects"""
    for i, row in stops.iterrows():
        print(f"Now ingesting row {i}...")

        print(row["stop_name"])
        print(row["stop_lat"])
        print(row["stop_lon"])
        obs = TransitStation(
            city=row["city"],
            station_id=row["stop_id"],
            station_name=row["stop_name"],
            location=Point(row["stop_lat"], row["stop_lon"], srid=4326),
            mode=transit_mode,
        )
        print(
            f'Observation created: {row["city"]}, {row["stop_id"]}, '
            f'{row["stop_name"]}, Point({row["stop_lat"]},{row["stop_lon"]})'
            f", mode {obs.mode}"
        )
        print(obs)
        try:
            obs.save()
            print(f"Observation {i} saved to PostGIS")
        except Exception as e:  # TODO: make this more specific
            print(e)
            print("Skipping import of this observation\n")
    print("Ingestion complete")


def handroll_geometrize_routes(city: str, feed) -> gpd.GeoDataFrame:
    """Associate each route and its properties with an appropriate GEOS LineString.
    Handrolls a simplified version of the gtfs_kit library's geometrize_routes()
    method, which broke on some transit feeds with which we tried it.
    Results in one shape per route, irrespective of direction.

    Warning: Some users may not be able to test this function in any way
    other than running this script, due to the 'ImproperlyConfigured' error
    in which attempts to import types from django.contrib.gis.geos fail to find
    the path for GDAL.

    TODO: write test that establishes all needed fields are there for every city
    """
    geom_shapes = feed.geometrize_shapes()
    geom_shapes.loc[:, "city"] = city
    geometries = geom_shapes.loc[:, "geometry"]
    gtfs_dict = get_gtfs_component_dfs(city, feed)
    routes = gtfs_dict["routes"]
    trips = gtfs_dict["trips"]

    # Conversion of shapely/Geopandas linestrings to GEOSGeometry/Django LineStrings
    # https://stackoverflow.com/questions/56299888/how-can-i-efficiently-save-data-from-geopandas-to-django-converting-from-shapel
    # TODO: IMPORTANT: FIX PANDAS MERGE LOGIC SO THAT geometrize_shapes()
    # GeoDataFrame has all route information about each shape's route in the
    # relevant columns, instead of NaNs
    geom_shapes = geom_shapes.merge(trips, how="right", on="shape_id")
    geom_shapes.loc[:, "geometry"] = geometries
    print(geom_shapes)
    geom_shapes = geom_shapes.merge(routes, how="right", on="route_id")
    print(geom_shapes.loc[:, ["geometry"]])
    geom_shapes = geom_shapes.loc[
        :,
        [
            "shape_id",
            "geometry",
            "route_id",
            "service_id",
            "route_type",
            "route_long_name",
            "route_color",
        ],
    ].drop_duplicates()
    geom_shapes.loc[:, "city"] = city
    print(geom_shapes.loc[:, "geometry"])
    return geom_shapes


def ingest_transit_routes(geom_shapes: gpd.GeoDataFrame) -> None:
    """Ingest routes and their shapes to Postgres database."""
    for i, row in geom_shapes.iterrows():
        print(f"Now ingesting route {i}...")
        print(row["route_id"])
        obs = TransitRoute(
            city=row["city"],
            route_id=row["route_id"],
            route_name=row["route_long_name"],
            color=row["route_color"],
            geo_representation=GEOSGeometry(row["geometry"]),
            mode=row["route_type"],
        )
        print(obs)
        try:
            obs.save()
        except Exception as e:
            print(e)
            print("Skipping ingestion of this observation")
    print("Ingestion complete")


def run():
    # pdb.set_trace()
    print("Getting Metra GTFS feed...")
    CHI, _, feed = get_gtfs_feed(METRA_URL)
    print("Preparing Metra GTFS feed for ingestion...")
    gtfs_dataframe_dict = get_gtfs_component_dfs(CHI, feed)
    stops = gtfs_dataframe_dict["stops"]
    stops.loc[:, "city"] = CHI
    geom_shapes = handroll_geometrize_routes(CHI, feed)
    # print(stops.columns)
    # print("Starting test ingestion of Metra stops...")
    # ingest_transit_stations(stops)
    print("Starting test ingestion of Metra routes...")
    ingest_transit_routes(geom_shapes)
    # stops_pointified = pointify_stops(stops)
    # print(stops_pointified)
    # print(stops_pointified.columns)


# if __name__ == "__main__":
# feed_city, feed_agency, feed = get_gtfs_feed(METRA_URL)
# gtfs_dataframe_dict = get_gtfs_component_dfs(feed_city, feed_agency, feed)
# stops = gtfs_dataframe_dict["stops"]
# # pdb.set_trace()
# print(stops)

# gtfs_data_for_postgres = combine_different_feeds(ALL_PILOT_CITY_URLS)
