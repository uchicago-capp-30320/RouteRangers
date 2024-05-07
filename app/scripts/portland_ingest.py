"""
OBJECTIVE: Ingest Portland Ridership Data into our Database
AUTHOR: Jimena Salinas
DATE: 05/06/2024

SOURCES: the data sets were obtained by a direct request to the 
TriMet Public Records department. This is the link to the form
to request data sets for Tri Met: 
https://trimet.org/publicrecords/recordsrequest.htm
The  Receipt ID for this Public Records Request is PRR 2024-254.

VARIABLES:
    - station_id: (str) combines the city "Portland" with a given stop_id
    - date: (datetime) represents a day in the format yyyy-mm-dd, only includes
    values for 2023
    - ridership: (int) represents the average number of bus and light rail Tri Met
    riders. The riders value was originally provided as an average by season 
    and day type (Saturday, Sunday, and Weekday). In order to fit the data model
    for the project which is at the datetime level, the data has been mapped to dates in 2023.
"""

import json
import sys
import os
from requests.models import Response
import django
import datetime
import pytz

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

django.setup()


from route_rangers_api.models import TransitStation, RidershipStation


def ingest_pdx_ridership_data(json_file_path: str) -> None:
    """
    Ingest portland ridership data from extracted JSON file
    into Django database
    """
    with open(json_file_path, "r") as file:
        data = json.load(file)

    for record in data:
        # Get the id from TransitStation using station_id + city = 'PDX'
        foreign_key = TransitStation.objects.get(
            station_id=record["station_id"], city="PDX"
        ).id

        print(f"ingesting ridership data for station {record['station_id']}...")
        # For each row, create a RidershipStation object
        timestamp_seconds = int(record["date"]) / 1000
        date_obj = datetime.datetime.fromtimestamp(timestamp_seconds)
        # to match model

        ridership_obj = RidershipStation.objects.create(
            id=foreign_key,
            date=date_obj,
            ridership=record["ridership"],
            station_id=record["station_id"],
        )
        print(ridership_obj)
    print("Ingestion complete")


def run():
    """
    Ingest PDX ridership data into Django db
    """
    json_file_path = "/Users/jimenasalinas/Library/CloudStorage/Box-Box/Route Rangers/Transit dataset exploration/Portland Ridership Data/portland_ridership/Portland_ridership.json"
    ingest_pdx_ridership_data(json_file_path)


if __name__ == "__main__":
    run()
