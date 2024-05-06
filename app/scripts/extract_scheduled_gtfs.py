### Imports

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import gtfs_kit as gk
import re
from datetime import datetime

import pdb

from django.contrib.gis.geos import GEOSGeometry, LineString, Point, MultiLineString
from route_rangers_api.models import TransitStation, TransitRoute

# to avoid a namespace conflict when creating shapely MultiLineStrings in geopandas
# before they are turned into Django GEOS MultiLineStrings later
from shapely.geometry import MultiLineString as shapely_MLS

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

BUS_URLS = [
    BRONX_BUS_URL,
    BROOKLYN_BUS_URL,
    MANHATTAN_BUS_URL,
    QUEENS_BUS_URL,
    STATEN_ISLAND_BUS_URL,
    MTA_BUS_CO_BUS_URL,
]

## PORTLAND
TRIMET_URL = "http://developer.trimet.org/schedule/gtfs.zip"


ALL_PILOT_CITY_URLS = [
    METRA_URL,
    CTA_URL,
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

### Functions


def get_gtfs_feed(feed_url: str) -> tuple:
    """
    Use gtfs_kit library to obtain the most up-to-date scheduled (static) GTFS
    data from a particular URL, and return each component file as a GeoDataFrame.
    """
    url_base = re.findall(r"https?:\/\/[^\/]+\/", feed_url)[0]
    feed_city = URL_TO_CITY[url_base]["City"]
    feed_agency = URL_TO_CITY[url_base]["Agency"]
    feed = gk.read_feed(feed_url, dist_units="ft")  # dist_units TBD

    return feed_city, feed_agency, feed


# give each DataFrame a city_id column (to disambiguate routes named "1" for example)
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
    shapes = feed.shapes

    gtfs_dataframe_dict = {
        "routes": routes,
        "trips": trips,
        "stops": stops,
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
            f"This {feed_city} GTFS feed has no transfers.txt file."
        )

    # Add city column
    for key in gtfs_dataframe_dict.keys():
        gtfs_dataframe_dict[key].loc[:, "city"] = feed_city

    return gtfs_dataframe_dict


def ingest_transit_stations(
    stops: pd.DataFrame | gpd.GeoDataFrame,
    url: str,
    # transit_mode=2,  # TODO: Undo hard-code -- should be 2 for Metra
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
            mode=assign_mode(row, url),
        )
        print(
            f'Observation created: {row["city"]}, {row["stop_id"]}, '
            f'{row["stop_name"]}, Point({row["stop_lat"]},{row["stop_lon"]})'
            f", mode {obs.mode}"
        )
        try:
            obs.save()
            print(f"Observation {i} saved to PostGIS")
        except Exception as e:  # TODO: make this more specific
            print(e)
            print("Skipping import of this observation\n")
    print("Ingestion complete")


def assign_mode(row, url: str) -> int:
    """Take in data about a transit stop and assign it the proper mode per
    GTFS standards (which isn't in the stops.txt). Is not super scalable
    if more cities are added.

    TODO: Think about how to redesign for easier scaling or perhaps redo with
    some creative joins"""

    LIGHT_RAIL = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    AERIAL_LIFT = 6

    if url == METRA_URL:
        return RAIL
    elif url in BUS_URLS:
        return BUS
    elif url == MTA_SUBWAY_URL:
        return SUBWAY
    elif url == CTA_URL:
        # stop_id is an integer. Bus stop_ids currently end at 18,709
        # El stop_ids currently start at 30,000
        # This may fail
        if int(row["stop_id"]) > 30000:
            return SUBWAY
        else:
            return BUS
    elif url == TRIMET_URL:
        if "MAX" in row["stop_name"]:
            return LIGHT_RAIL
        elif "WES" in row["stop_name"]:
            return RAIL
        elif "Tram Terminal" in row["stop_name"]:
            return AERIAL_LIFT  # there's an aerial tram!!
        else:
            return BUS  # other routes are buses


def handroll_multiline_routes(city: str, feed) -> gpd.GeoDataFrame:
    """Associate each route and its properties with an appropriate GEOS
    MultiLineString. Geometrizes all shapes, then uses pandas groupby
    and type conversion to turn each set of LineStrings into a MultiLineString.

    Note that this will not do anything to eliminate overlap between component
    LineStrings, so a route that branches into two will have a MultiLineString
    with four LineString components in it, for inbound and outbound directions
    on each branch of the route."""
    shapes = feed.geometrize_shapes()
    shapes.loc[:, "city"] = city
    gtfs_dict = get_gtfs_component_dfs(city, feed)
    routes = gtfs_dict["routes"]
    trips = gtfs_dict["trips"]

    # eliminate whitespace issues
    routes.loc[:, "route_id"] = routes.loc[:, "route_id"].str.strip()
    trips.loc[:, "route_id"] = trips.loc[:, "route_id"].str.strip()
    trips.loc[:, "shape_id"] = trips.loc[:, "shape_id"].str.strip()
    shapes.loc[:, "shape_id"] = shapes.loc[:, "shape_id"].str.strip()

    routes_trips = trips.merge(routes, how="left", on="route_id").drop_duplicates(
        "shape_id"
    )

    # TODO: consider method-chaining more
    shapes = shapes.merge(routes_trips, how="left", on="shape_id")

    grouped = (
        shapes.groupby("route_id", as_index=False)["geometry"].apply(list).reset_index()
    )
    gdf = gpd.GeoDataFrame(
        grouped, geometry=grouped.loc[:, "geometry"].apply(shapely_MLS)
    )
    gdf = gdf.merge(routes, how="left", on="route_id")
    gdf.loc[:, "city"] = city
    gdf = gdf.loc[
        :,
        [
            "geometry",
            "route_id",
            "route_type",
            "route_long_name",
            "route_color",
            "city",
        ],  # maybe do this earlier to reduce memory usage
    ]
    return gdf


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
    gtfs_dict = get_gtfs_component_dfs(city, feed)
    routes = gtfs_dict["routes"]
    trips = gtfs_dict["trips"]

    # Conversion of shapely/Geopandas linestrings to GEOSGeometry/Django LineStrings
    # https://stackoverflow.com/questions/56299888/how-can-i-efficiently-save-data-from-geopandas-to-django-converting-from-shapel

    # this might cause NaNs - check that these merges should be "left" and not "right"
    routes_trips = trips.merge(routes, how="left", on="route_id").drop_duplicates(
        ["route_id", "shape_id"]
    )
    # Merges were failing because whitespace in shape_id column differed between
    # tables. Remove all of it and merge should go through
    routes_trips.loc[:, "shape_id"] = routes_trips.loc[:, "shape_id"].str.strip()
    geom_shapes.loc[:, "shape_id"] = geom_shapes.loc[:, "shape_id"].str.strip()
    # TODO: Consider adding an equality check here

    geom_shapes = geom_shapes.merge(routes_trips, how="left", on="shape_id")
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
    print(geom_shapes)
    return geom_shapes


def ingest_transit_routes(geom_shapes: gpd.GeoDataFrame) -> None:
    """Ingest routes and their shapes to Postgres database."""
    # convert all geometries to a GEOS-compatible representation
    geom_shapes = geom_shapes.to_wkt()
    for i, row in geom_shapes.iterrows():
        print(f"Now ingesting route {i}...")
        print(row["route_id"])
        obs = TransitRoute(
            city=row["city"],
            route_id=row["route_id"],
            route_name=row["route_long_name"],  # TODO: switch to short name or
            # or truncate to 30 characters or raise 30 character max in PostGIS
            color=row["route_color"],
            geo_representation=GEOSGeometry(row["geometry"]),
            mode=row["route_type"],
        )
        print(
            f"Observation created: {obs.city}, {obs.route_id}, "
            f"{obs.route_name}, color #{obs.color}), "
            f", mode {obs.mode}"
        )
        try:
            obs.save()
        except Exception as e:
            print(e)
            print("Skipping ingestion of this observation\n")
    print("Ingestion complete")


def ingest_multiple_feeds(feed_url_list: list[str]) -> None:
    """
    Run the entire GTFS ingestion pipeline for multiple endpoint URLs.
    TODO: consider allowing this to take an arbitrary list of *args rather than
    a list.
    """

    for url in feed_url_list:
        print(f"Getting static GTFS transit feed from {url}...")
        city, agency, feed = get_gtfs_feed(url)
        print(f"{city} {agency} feed acquired from URL")
        gtfs_df_dict = get_gtfs_component_dfs(city, feed)

        stops = gtfs_df_dict["stops"]
        stops.loc[:, "city"] = city  # should be extraneous now
        print("Preparing shapes of routes for upload... THIS COULD TAKE A FEW MINUTES.")
        geom_shapes = handroll_multiline_routes(city, feed)
        # geom_shapes = handroll_geometrize_routes(city, feed)

        print(f"Starting ingestion of {city} {agency} stops into PostGIS...")
        ingest_transit_stations(stops, url)

        print(f"Starting test ingestion of {city} {agency} routes into PostGIS...")
        ingest_transit_routes(geom_shapes)

        # TODO: Consider doing an ingestion of transfers.txt if it exists
        # TODO: Consider reading out stdout to a log for inspection of ingestion errors


def run():
    """TODO: Build out into a script that gets GTFS feed for
    all three cities (all ten GTFS feeds), and ingests stops and routes for each"""
    ingest_multiple_feeds(ALL_PILOT_CITY_URLS)


if __name__ == "__main__":
    run()
