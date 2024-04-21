import os 
from typing import List, Dict
from collections.abc import Callable
import requests
import time
import pandas as pd
from pathlib import Path 
from sodapy import Socrata
import os
from dotenv import load_dotenv

load_dotenv()

NYC_DATA_PORTAL_APP_TOKEN = os.getenv('NYC_DATA_PORTAL_APP_TOKEN')
NYC_DATA_PORTAL_USERNAME = os.getenv('NYC_DATA_PORTAL_USERNAME')
NYC_DATA_PORTAL_PASSWORD = os.getenv('NYC_DATA_PORTAL_PASSWORD')
TEST_DATA_DIR = os.getenv("TEST_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000 #Max number of results for API
TIMEOUT = 30

ENDPOINTS = {
    "TURNSTILE_2020" : "py8k-a8wg",
    "TURNSTILE_2021" : "uu7b-3kff",
    "TURNSTILE_2022" : "k7j9-jnct",
    "BUS_RIDERSHIP" : "kv7t-n8in",
    "SUBWAY_RIDERSHIP" : "wujg-7c2s"  
}

CLIENT = Socrata("data.ny.gov",
                  NYC_DATA_PORTAL_APP_TOKEN,
                  username = NYC_DATA_PORTAL_USERNAME,
                  password = NYC_DATA_PORTAL_PASSWORD,
                  timeout = TIMEOUT)

#This function should be moved to a utils.py file 
def make_request(url: str, session: Callable):
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is
    expected and that the rate limit is obeyed.
    """
    # check if URL starts with an allowed domain name
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    if session:
        resp = session.get(url)
    else:
        resp = requests.get(url)
    return resp

def make_nyc_api_request(table_name:str, client:Callable) -> List[Dict]:
    """
    Makes a call to the NYC Data Portal API to retrieve information 
    from an endpoint
    
    Inputs:
    -table_name(str): Name of the table being retrieved
    -client(Socrata client object): Object for the NYC Socrata API

    """
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {table_name} endpoint")
    resp = client.get(ENDPOINTS[table_name], limit=RESULTS_PER_PAGE)
    return resp

def nyc_request_to_csv(api_results:List[Dict],table_name:str,path:str) -> None:
    """
    Converts a request from the NYC Data Portal to a csv file
    """
    table_df = pd.DataFrame.from_records(api_results)
    #Export top csv
    filepath = Path(f'{path}/{table_name.lower()}.csv')  
    print(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    table_df.to_csv(filepath)  

def extract_mta_table(table_name:str,path:str,client:Callable) -> None:
    """
    Extract an MTA table and store it in one or multiple csv files
    
    Inputs:
    -table_name(str): Name of the table being retrieved
    -client(Socrata client object): Object for the NYC Socrata API
    """
    resp = make_nyc_api_request(table_name,client)
    if resp:
        nyc_request_to_csv(resp,table_name,path)

def extract_mta_tables(client:Callable,path:str) -> None:
    """
    Extract all the tables required for the project from the NYC data portal
    """
    for table_name in ENDPOINTS:
        extract_mta_table(table_name,path,client)

if __name__ == "__main__":
    resp = CLIENT.get_metadata("kv7t-n8in")
    #print(resp)
    print(resp["columns"][0]["cachedContents"]["non_null"])
