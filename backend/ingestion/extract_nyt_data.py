import os
from typing import List
import requests
from lxml.html import html_parser
import json

# def create_nyt_client()


def extract_table_mta_json(end_point: str, api_key=None) -> str:
    """
    Extracts the json response from a API request to the NYC Data portal
    """
    resp = requests.get(end_point)
    resp_json = json.loads(resp.text)
    return resp_json


if __name__ == "__main__":
    resp = extract_table_mta_json(
        end_point="https://data.ny.gov/resource/uu7b-3kff.json"
    )
    print(resp)
