import os
import logging
import requests
import pandas as pd
from typing import List, Dict
from dotenv import load_dotenv
from django.db import IntegrityError
from route_rangers_api.models import Demographics
from route_rangers_api.utils.city_mapping import CITY_FIPS

###############################################################################
# SETUP
###############################################################################

# Enviornment variables
load_dotenv()
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Mappings
variable_ids = {
    "B01001_001E": "population",
    "B19013_001E": "med_hhi_2022",
    "B08301_001E": "transp_to_work_total",
    "B08301_002E": "transp_to_work_car",
    "B08301_010E": "transp_to_work_public",
    "B08301_011E": "transp_to_work_bus",
    "B08301_012E": "transp_to_work_subway",
    "B08303_001E": "work_commute_time_total",
    "B08303_002E": "work_commute_time_00_to_04",
    "B08303_003E": "work_commute_time_05_to_09",
    "B08303_004E": "work_commute_time_10_to_14",
    "B08303_005E": "work_commute_time_15_to_19",
    "B08303_006E": "work_commute_time_20_to_24",
    "B08303_007E": "work_commute_time_25_to_29",
    "B08303_008E": "work_commute_time_30_to_34",
    "B08303_009E": "work_commute_time_35_to_39",
    "B08303_010E": "work_commute_time_40_to_44",
    "B08303_011E": "work_commute_time_45_to_59",
    "B08303_012E": "work_commute_time_60_to_89",
    "B08303_013E": "work_commute_time_90_or_more",
}

min_to_work = {
    "work_commute_time_less_15": [
        "work_commute_time_00_to_04",
        "work_commute_time_05_to_09",
        "work_commute_time_10_to_14",
    ],
    "work_commute_time_15_29": [
        "work_commute_time_15_to_19",
        "work_commute_time_20_to_24",
        "work_commute_time_25_to_29",
    ],
    "work_commute_time_30_44": [
        "work_commute_time_30_to_34",
        "work_commute_time_35_to_39",
        "work_commute_time_40_to_44",
    ],
    "work_commute_time_45_59": ["work_commute_time_45_to_59"],
    "work_commute_time_60_89": ["work_commute_time_60_to_89"],
    "work_commute_time_over_90": ["work_commute_time_90_or_more"],
}

###############################################################################
# HELPER FUNCTIONS
###############################################################################


def get_census_data(
    variable_ids: Dict[str, str], state_code: str, county_code: str
) -> List[Dict]:
    """
    Fetches data from US Census API.

    Inputs:
        variable_ids (dict): Unique variable IDs and their names
        state_code (str): State-level FIPS code
        county_code (str): County-level FIPS code

    Returns:
        A list of dictionaries with function inputs as key, value pairs.
    """
    # Request parameters
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": ",".join(variable_ids.keys()),
        "for": "tract:*",
        "in": f"state:{state_code}+county:{county_code}",
        "key": CENSUS_API_KEY,
    }
    # API call
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        headers = data[0]
        rows = data[1:]
        formatted_data = [dict(zip(headers, row)) for row in rows]
        return formatted_data
    else:
        logging.error(
            f"Failed to retrieve data. \
            Status code: {response.status_code}"
        )
        return []


def clean_census_data(data: List[Dict]) -> pd.DataFrame:
    """
    Cleans fetched data from Census API.

    Inputs:
        - data (list of dicts): output from get_census_data() function

    Returns:
        Dataframe ready for database ingestion.
    """
    # Create dataframe
    df = pd.DataFrame(data)
    df.rename(columns=variable_ids, inplace=True)
    df.columns = [col.replace(" ", "_") for col in df.columns]
    # Set column types
    str_columns = ["state", "county", "tract"]
    for col in df.columns:
        if col not in str_columns:
            df[col] = pd.to_numeric(df[col])
    # Build commute time windows
    for new_column, old_columns in min_to_work.items():
        df[new_column] = df[old_columns].sum(axis=1)
    cols_to_drop = [col for sublist in min_to_work.values() for col in sublist]
    df.drop(cols_to_drop, axis=1, inplace=True)
    # Clean values
    df["med_hhi_2022"] = df["med_hhi_2022"].mask(df["med_hhi_2022"] < 0)
    return df


def upload_census_data(city_df: pd.DataFrame) -> None:
    """
    Ingest clean Census data.

    Input:
        - city_data (DataFrame): demographic data of city.

    Returns:
        Nothing.
    """
    for _, row in city_df.iterrows():
        try:
            obs = Demographics(
                state=row["state"],
                county=row["county"],
                census_tract=row["tract"],
                population=row["population"],
                transportation_to_work=row["transp_to_work_total"],
                transportation_to_work_car=row["transp_to_work_car"],
                transportation_to_work_public=row["transp_to_work_public"],
                transportation_to_work_bus=row["transp_to_work_bus"],
                transportation_to_work_subway=row["transp_to_work_subway"],
                work_commute_time_less_15=row["work_commute_time_less_15"],
                work_commute_time_15_29=row["work_commute_time_15_and_29"],
                work_commute_time_30_44=row["work_commute_time_30_and_44"],
                work_commute_time_45_59=row["work_commute_time_45_and_59"],
                work_commute_time_60_89=row["work_commute_time_60_and_89"],
                work_commute_time_over_90=row["work_commute_time_over_90"],
            )
            if row["med_hhi_2022"] >= 0:
                obs.median_income = row["med_hhi_2022"]
            obs.save()
        except IntegrityError as e:
            print(f"Duplicated observation {obs} in model: {e}")


###############################################################################
# RUN
###############################################################################


def run():
    """
    Extracts US Census data and stores it in database.
    """
    supported_cities = ["portland", "chicago", "nyc"]
    for city in supported_cities:
        state_code = CITY_FIPS[city]["state"]
        county_codes = CITY_FIPS[city]["county"]
        for county_code in county_codes:
            raw_data = get_census_data(variable_ids, state_code, county_code)
            clean_data = clean_census_data(raw_data)
            upload_census_data(clean_data)
        logging.info(f"{city.upper()} data ingested.")


if __name__ == "__main__":
    run()
