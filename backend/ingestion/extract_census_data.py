import os
import sys
import csv
import logging
import requests
from typing import List, Dict
from dotenv import load_dotenv

########################################################################################
# SETUP
########################################################################################

# Enviornment variables
load_dotenv()
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Mappings
variable_ids = {"B01001_001E": "total_population"}
city_fips = {
    "nyc": {"state_fips": "36", "county_fips": ["061", "047", "081", "005", "085"]},
    "chicago": {"state_fips": "17", "county_fips": ["031"]},
    "portland": {"state_fips": "41", "county_fips": ["051"]},
}

########################################################################################
# HELPER FUNCTIONS
########################################################################################


def valid_command_args() -> str:
    """
    Validates command line use and extracts argument.

    Inputs:
        None

    Returns:
      A string refering to the city to pull data from.
    """
    # Check syntax
    if len(sys.argv) != 2:
        sys.exit("Retype command as 'python3 extract_census_data.py <city_name>'")
    # Check city
    city = sys.argv[1]
    if city not in city_fips:
        sys.exit(
            "Unrecognized city." + f"Available options: {', '.join(city_fips.keys())}"
        )
    return city


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
        "for": "block group:*",
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
        logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
        return []


def store_census_data(data: List[Dict], city: str) -> None:
    """
    Stores retrieved data in csv file.

    Inputs:
        - data (list of dicts): output from get_census_data() function
        - city (str): city of analysis

    Returns csv file of requested city data, with proper variable names.
    """
    output_dir = os.path.join(os.getcwd(), f"{sys.argv[1]}_data.csv")
    if data:
        with open(output_dir, "w", newline="") as file:
            fieldnames = [
                variable_ids.get(header, header.replace(" ", "_"))
                for header in data[0].keys()
            ]
            fieldnames = fieldnames[-4:] + fieldnames[:-4]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                row_renamed = {
                    variable_ids.get(k, k.replace(" ", "_")): v for k, v in row.items()
                }
                writer.writerow(row_renamed)
    else:
        logging.warning(f"No {city} data to store.")


def main():
    """
    Extracts US Census data and stores is locally.

    Inputs: None

    Returns:
        A csv file located in same directory.
    """
    city = valid_command_args()
    state_code = city_fips[city]["state_fips"]
    county_codes = city_fips[city]["county_fips"]
    for county_code in county_codes:
        data = get_census_data(variable_ids, state_code, county_code)
        if data:
            store_census_data(data, city)
        else:
            logging.warning(f"No data found for county {state_code}{county_code}.")
    logging.info(f"{city.upper()} data stored.")


########################################################################################
# MAIN EXECUTION
########################################################################################

if __name__ == "__main__":
    main()
