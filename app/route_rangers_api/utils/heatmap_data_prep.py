# Purpose: Query database to format and prepare demographic data
# for heatmaps
# Author: Jimena Salinas
# Date: Day 17th, 2024

import os
import sys
import django
from dotenv import load_dotenv
import pandas as pd
from shapely import wkt
import geopandas as gpd
from geopandas import GeoDataFrame
import json
from shapely.geometry import MultiPolygon


def setup_django() -> None:
    load_dotenv()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

    # parent directory to find route_rangers_api
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    sys.path.append(parent_dir)

    django.setup()


def fetch_demographics_data() -> pd.DataFrame:
    from route_rangers_api.models import Demographics

    demographics_queryset = Demographics.objects.all().values(
        "census_tract",
        "state",
        "county",
        "median_income",
        "work_commute_time_15_29",
        "work_commute_time_30_44",
        "work_commute_time_45_59",
        "work_commute_time_60_89",
        "work_commute_time_less_15",
        "work_commute_time_over_90",
        "transportation_to_work_public",
        "transportation_to_work_bus",
        "transportation_to_work_subway",
        "population",
        "geographic_delimitation",
    )
    return pd.DataFrame(demographics_queryset)


def preprocess_demographics_df(demographics_df) -> GeoDataFrame:
    """
    Takes in a Pandas dataframe with a demographic data from the datbase
    and a "geographic_delimitation" field and formats the
    "geographic_delimitation" into a valid geography for a geopandas df
    """
    # remove SRID prefix and edit null vals
    demographics_df["geographic_delimitation"] = (
        demographics_df["geographic_delimitation"]
        .astype(str)
        .str[10:]  # Remove the first 10 characters
        .fillna("")
    )
    print("AFTER FIRST PASS", demographics_df["geographic_delimitation"])
    # WKT strings to Shapely geometries
    demographics_df["geographic_delimitation"] = demographics_df[
        "geographic_delimitation"
    ].apply(lambda x: wkt.loads(x) if x else None)

    return demographics_df


def calculate_weighted_commute_times(demographics_df) -> GeoDataFrame:
    """
    Takes in a GeoDataFrame with commute time information by time
    category from the Census and returns a GeoDataFrame with a weighted
    average commute time
    """
    # weighted commute time for each category
    # the weighted_commute_... columns show number of people who take
    # between x and x minutes in their commute
    demographics_df["weighted_commute_15_29"] = (
        demographics_df["work_commute_time_15_29"] * 22
    ) / demographics_df["population"]
    demographics_df["weighted_commute_30_44"] = (
        demographics_df["work_commute_time_30_44"] * 37
    ) / demographics_df["population"]
    demographics_df["weighted_commute_45_59"] = (
        demographics_df["work_commute_time_45_59"] * 31.5
    ) / demographics_df["population"]
    demographics_df["weighted_commute_60_89"] = (
        demographics_df["work_commute_time_60_89"] * 74.5
    ) / demographics_df["population"]
    demographics_df["weighted_commute_less_15"] = (
        demographics_df["work_commute_time_less_15"] * 7.5
    ) / demographics_df["population"]
    demographics_df["weighted_commute_over_90"] = (
        demographics_df["work_commute_time_over_90"] * 104.5
    ) / demographics_df["population"]

    demographics_df["percentage_public_to_work"] = (
        demographics_df["transportation_to_work_public"] / demographics_df["population"]
    )
    demographics_df["percentage_bus_to_work"] = (
        demographics_df["transportation_to_work_bus"] / demographics_df["population"]
    )
    demographics_df["percentage_subway_to_work"] = (
        demographics_df["transportation_to_work_subway"] / demographics_df["population"]
    )

    # weighted average commute time
    demographics_df["total_weighted_commute_time"] = (
        demographics_df["weighted_commute_15_29"]
        + demographics_df["weighted_commute_30_44"]
        + demographics_df["weighted_commute_45_59"]
        + demographics_df["weighted_commute_60_89"]
        + demographics_df["weighted_commute_less_15"]
        + demographics_df["weighted_commute_over_90"]
    )

    return demographics_df


def drop_columns(demographics_df) -> GeoDataFrame:
    columns_to_drop = [
        "work_commute_time_15_29",
        "work_commute_time_30_44",
        "work_commute_time_45_59",
        "work_commute_time_60_89",
        "work_commute_time_less_15",
        "work_commute_time_over_90",
        "transportation_to_work_public",
        "transportation_to_work_bus",
        "transportation_to_work_subway",
        "weighted_commute_15_29",
        "weighted_commute_30_44",
        "weighted_commute_45_59",
        "weighted_commute_60_89",
        "weighted_commute_less_15",
        "weighted_commute_over_90",
    ]
    return demographics_df.drop(columns=columns_to_drop)


def main():
    setup_django()
    demographics_df = fetch_demographics_data()
    demographics_df = preprocess_demographics_df(demographics_df)
    demographics_df = calculate_weighted_commute_times(demographics_df)
    demographics_df = drop_columns(demographics_df)

    demographics_gdf = gpd.GeoDataFrame(
        demographics_df, geometry="geographic_delimitation", crs="EPSG:4326"
    )

    print("ORGINAL GDFFFF", demographics_gdf["geographic_delimitation"])
    print(demographics_gdf.columns)
    print(type(demographics_gdf))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    sys.path.append(parent_dir)

    static_folder = os.path.join(parent_dir, "route_rangers_api/static")

    chicago_geojson_path = os.path.join(static_folder, "ChicagoCensus.geojson")
    newyork_geojson_path = os.path.join(static_folder, "newyork.geojson")
    portland_geojson_path = os.path.join(static_folder, "portland.geojson")

    with open(chicago_geojson_path, "r") as chicago_file:
        chicago_data = gpd.read_file(chicago_file)

    with open(newyork_geojson_path, "r") as newyork_file:
        newyork_data = gpd.read_file(newyork_file)

    with open(portland_geojson_path, "r") as portland_file:
        portland_data = gpd.read_file(portland_file)

    # split gdfs by city
    chicago_gdf = demographics_gdf[demographics_gdf["state"] == "17"]
    # convert geo to multipolygon to match geojson
    chicago_gdf["geographic_delimitation"] = chicago_gdf[
        "geographic_delimitation"
    ].apply(lambda x: MultiPolygon([x]) if x.geom_type == "Polygon" else x)

    newyork_gdf = demographics_gdf[demographics_gdf["state"] == "36"]
    portland_gdf = demographics_gdf[demographics_gdf["state"] == "41"]

    print("PORTLAND GDF", portland_gdf.head(1))

    # merge geojsons with geopandas dfs (spatial join)
    print("crs 1", chicago_gdf.crs)
    print("crs 2", chicago_data.crs)

    print("CHICAGO DATAAA", chicago_data["geometry"].head())
    print("CHHICAGO GEOPANDASS", chicago_gdf["geographic_delimitation"].head())

    chicago_merged = gpd.sjoin(
        chicago_data, chicago_gdf, how="left", predicate="intersects"
    )

    newyork_merged = gpd.sjoin(
        newyork_data, newyork_gdf, how="left", predicate="intersects"
    )

    portland_merged = gpd.sjoin(
        portland_data, portland_gdf, how="left", predicate="intersects"
    )

    print("CHICAGO MERGED", chicago_merged)
    print("NY MERGED", newyork_merged)
    print("PDX MERGED", portland_merged)

    chicago_merged_path = os.path.join(static_folder, "ChicagoCensus_merged.geojson")
    chicago_merged.to_file(chicago_merged_path, driver="GeoJSON")

    newyork_merged_path = os.path.join(static_folder, "NewYorkCensus_merged.geojson")
    newyork_merged.to_file(newyork_merged_path, driver="GeoJSON")

    portland_merged_path = os.path.join(static_folder, "PortlandCensus_merged.geojson")
    portland_merged.to_file(portland_merged_path, driver="GeoJSON")


if __name__ == "__main__":
    main()
