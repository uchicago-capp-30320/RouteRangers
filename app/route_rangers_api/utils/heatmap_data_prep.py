import os
import sys
import django
from dotenv import load_dotenv
import pandas as pd


load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

# parent directory to find route_rangers_api
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(parent_dir)

django.setup()

# import models
from route_rangers_api.models import Demographics


demographics = Demographics.objects.all().values(
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
)

data = list(demographics.values())

demographics_df = pd.DataFrame(data)


# Calculate weighted avg commute time


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
    "id",
    "transportation_to_work",
    "transportation_to_work_car",
]

demographics_df1 = demographics_df.drop(columns=columns_to_drop)

# Print the DataFrame
print(demographics_df1.head(10))

print(demographics_df1.columns)
