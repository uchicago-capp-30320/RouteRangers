import os
import sys
import django
from dotenv import load_dotenv
import pandas as pd
from shapely import wkt
import geopandas as gpd
from shapely.geometry import Polygon
import re
from shapely.wkt import loads


load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

# parent directory to find route_rangers_api
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(parent_dir)

django.setup()

# import models
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


# Convert queryset to DataFrame
demographics_df = pd.DataFrame(demographics_queryset)

# Remove SRID prefix from WKT strings
demographics_df["geographic_delimitation"] = (
    demographics_df["geographic_delimitation"].str.replace(r"^SRID=\d+;", "").fillna("")
)

# Convert WKT strings to Shapely geometries
demographics_df["geographic_delimitation"] = demographics_df[
    "geographic_delimitation"
].apply(lambda x: wkt.loads(x) if x else None)

# Create GeoDataFrame
demographics_df = gpd.GeoDataFrame(
    demographics_df, geometry="geographic_delimitation", crs="EPSG:4326"
)

# Calculate weighted commute time for each category
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
# weighted average commute time for each group

demographics_df["total_weighted_commute_time"] = (
    demographics_df["weighted_commute_15_29"]
    + demographics_df["weighted_commute_30_44"]
    + demographics_df["weighted_commute_45_59"]
    + demographics_df["weighted_commute_60_89"]
    + demographics_df["weighted_commute_less_15"]
    + demographics_df["weighted_commute_over_90"]
)

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

demographics_df1 = demographics_df.drop(columns=columns_to_drop)

demographics_df1 = demographics_df1.copy()

print(demographics_df1.head(1))

print(demographics_df1.columns)

print(type(demographics_df1))
