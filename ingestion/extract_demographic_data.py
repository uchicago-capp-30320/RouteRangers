"""
OBJECTIVE: Extract socio-demographic data at the census tract and block level.
AUTHOR: Benjamin Leiva
DATE: 04/17/2024

QUERY LIMITS: 50 variables per query, 500 queries per day

CITIES (County, FIPS):
    - New York:
        - Manhattan (New York, 36061)
        - Brooklyn (Kings, 36047)
        - Queens (Queens, 36081)
        - Bronx (The Bronx, 36005)
        - Staten Island (Richmond, 36085)
    - Chicago:
        - Chicago (Cook, 17031)
    - Portland:
        - Portland (Multnomah, 41051)

SOURCES (Geography Level, Hierarchy):
    - Census 2020 (state > county > tract)
        - https://api.census.gov/data/2020/dec/ddhca.html
        - Variables: Total population, sex, age (by groups is available)
    - ACS 2022 5Y: (150, state > county > tract > block group)
        - https://api.census.gov/data/2022/acs/acs5/geography.html   
        - https://api.census.gov/data/2022/acs/acs5/variables.html
    - PDB 2022 : (_, state > county > tract > block group)
        - http://api.census.gov/data/2022/pdb/tract
        - https://api.census.gov/data/2022/pdb/blockgroup/variables.html
    - Census Documentation:
        - https://census-docs.com/#get_function

VARIABLES (ID, source):
    - Total Population:
        - B01003_001E, ACS 2022 5Y
    - Median Household Income in the Past 12 Months (2022 Inflation Adj.):
        - B29004_001E, ACS 2022 5Y
    - Bachelor's Degree:
        - B15003_022E, ACS 2022 5Y
    - Age (???) -> Thinking about walking distance to bus stops for the elderly
    - Disability (???) -> Accessibility issues, as above
        
"""

################################################################################
# SETUP
################################################################################

# Dependencies
import os
import sys
import csv
import logging
import requests

# import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Tuple

# Environment variables, logging
load_dotenv()
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# FIPS code mappings
city_fips = {
    "nyc": {"state_fips": "36", "county_fips": ["061", "047", "081", "005", "085"]},
    "chicago": {"state_fips": "17", "county_fips": ["031"]},
    "portland": {"state_fips": "41", "county_fips": ["051"]},
}

# Socioeconomic variable ID mappings for 2020 Census
variable_ids = {
    "B01001_001E": "Total_Population"
    # 'DP05_0001E': 'Total_Population'
}

################################################################################
# HELPER FUNCTIONS
################################################################################


def valid_command_args() -> Tuple[str, str]:
    """
    Validates command line use and extracts arguments.
    """
    # Check syntax, store arguments if correct
    if len(sys.argv) != 3:
        sys.exit(
            "Retype command as "
            + "'python3 extract_census_data.py <city_name> <geography_unit>'"
        )
    city, geography_unit = sys.argv[1], sys.argv[2]
    # Check city
    if city not in city_fips:
        sys.exit(
            "Unrecognized city." + f"Available options: {', '.join(city_fips.keys())}"
        )
    # Check geography unit
    geography_unit = sys.argv[2]
    geography_units = ["census_tract", "block_group"]
    if geography_unit not in geography_units:
        sys.exit(
            "Unrecogniced geography unit."
            + f"Available options: {', '.join(geography_units)}"
        )
    return city, geography_unit.replace("census_tract", "tract").replace(
        "block_group", "block group"
    )


def get_census_data(
    variable_ids: Dict[str, str], geography_unit: str, state_code: str, county_code: str
) -> List[Dict]:
    """
    Fetches data US Census API.

    Inputs:
        - variable_ids (dict): Unique variable IDs and their names
        - geography_unit (str): 'tract' or 'block group' level
        - state_code (str): State-level FIPS code
        - county_code (str): County-level FIPS code

    Returns a dictionary with function inputs as key, value pairs.
    """
    # Request parameters
    url = "https://api.census.gov/data/2022/acs/acs5"
    params = {
        "get": ",".join(variable_ids.keys()),
        "for": f"{geography_unit}:*",
        "in": f"state:{state_code}+county:{county_code}",
        "key": CENSUS_API_KEY,
    }
    # url = 'https://api.census.gov/data/2020/dec/ddhca'
    # params = {
    #     'get': ','.join(variable_ids.keys()),
    #     'for': f'{geography_unit}:*',
    #     'in': f'state:{state_code} county:{county_code}',
    #     'key': CENSUS_API_KEY
    # }
    # API call
    response = requests.get(url, params=params)
    logging.debug(f"Request URL: {response.url} - Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        headers = data[0]
        rows = data[1:]
        formatted_data = [dict(zip(headers, row)) for row in rows]
        return formatted_data
    else:
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
        return []


def store_census_data(data: List[Dict], city: str, geography_unit: str) -> None:
    """
    Stores ACS city data in csv file.

    Inputs:
        - data (list of dicts): output from get_censys_data() function

    Returns csv file of input as a dataframe, with proper variable names.
    """

    # Define output directory TODO
    output_dir = os.path.join(os.getcwd(), f"{sys.argv[1]}_{sys.argv[2]}_data.csv")
    # '/Users/bleiva/Documents/GitHub/RouteRangers/backend/ingestion/data.csv'

    # Save data
    if data:
        with open(output_dir, "w", newline="") as file:
            fieldnames = [variable_ids.get(header, header) for header in data[0].keys()]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                row_renamed = {variable_ids.get(k, k): v for k, v in row.items()}
                writer.writerow(row_renamed)
        logging.info(f"Data stored in {output_dir}")
    else:
        logging.warning(f"No data found to store for {city} in {geography_unit}")


################################################################################
# MAIN EXECUTION
################################################################################

if __name__ == "__main__":
    city, geography_unit = valid_command_args()
    state_code = city_fips[city]["state_fips"]
    county_codes = city_fips[city]["county_fips"]
    for county_code in county_codes:
        data = get_census_data(variable_ids, geography_unit, state_code, county_code)
        if data:
            store_census_data(data, city, geography_unit)
            logging.info(
                f"Data for {city} at {geography_unit} level successfully stored."
            )
        else:
            logging.warning(f"No data found for county {county_code}.")
