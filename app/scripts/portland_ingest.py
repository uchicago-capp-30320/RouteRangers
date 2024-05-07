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
    - ID (int): this ID is the foreign key from the TransitStations table,
    it can be obtained using city = 'PDX' and station_id
    - station_id: (str) a stop_id (GTFS)
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
from typing import List
from django.db.utils import IntegrityError

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(parent_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geodjango.settings")

django.setup()


from route_rangers_api.models import TransitStation, RidershipStation


def get_transit_station_ids() -> list:
    """
    Get a list of all id values from the TransitStation table
    """
    return list(TransitStation.objects.values_list("id", flat=True))


def get_list_of_stations() -> list:
    """
    Get a list of all id values from the TransitStation table as strings
    """
    return [
        str(station_id)
        for station_id in TransitStation.objects.values_list("station_id", flat=True)
    ]


def ingest_pdx_ridership_data(
    json_file_path: str, list_of_db_ids: List, list_of_stations: List
) -> None:
    """
    Ingest portland ridership data from extracted JSON file
    into Django database
    """
    stations_not_matched = []

    RidershipStation.objects.all().delete()
    with open(json_file_path, "r") as file:
        data = json.load(file)

    for record in data:
        try:
            # Get the id from TransitStation using station_id + city = 'PDX'
            foreign_key = TransitStation.objects.get(
                station_id=str(record["station_id"]), city="PDX"
            ).id

            station_id = str(record["station_id"])

            # print(f"FOREIGN_key '{station_id}', {foreign_key}")

            # Check if foreign key exists in the list of TransitStation ids
            if (foreign_key in list_of_db_ids) and (station_id in list_of_stations):

                print(f"Ingesting ridership data for station {record['station_id']}...")

                #     # For each row, create a RidershipStation object
                timestamp_seconds = int(record["date"]) / 1000
                date_obj = datetime.datetime.fromtimestamp(timestamp_seconds)
                # date formatting to match model

                ridership_obj = RidershipStation.objects.create(
                    id=foreign_key,
                    date=date_obj,
                    ridership=record["ridership"],
                    station_id=station_id,
                )
                print(ridership_obj)
                ridership_obj.save()
            else:
                print(
                    f"Skipping ingestion for station {record['station_id']}, foreign key not found in TransitStation."
                )

        except TransitStation.DoesNotExist:
            stations_not_matched.append(record["station_id"])
            print(
                f"Skipping ingestion for station {record['station_id']}, no matching TransitStation found."
            )
            continue

        except IntegrityError as e:
            # foreign key db rule violation
            print(
                f"Skipping ingestion for station {record['station_id']} due to foreign key constraint violation"
            )
            continue

    print("Ingestion complete")

    # Print the station IDs that didn't match
    if stations_not_matched:
        print("The following station IDs did not match any TransitStation:")
        print(", ".join(stations_not_matched))


def run():
    """
    Ingest PDX ridership data into Django db
    """
    json_file_path = "/Users/jimenasalinas/Library/CloudStorage/Box-Box/Route Rangers/Transit dataset exploration/Portland Ridership Data/portland_ridership/Portland_ridership.json"
    transit_station_ids = get_transit_station_ids()
    list_of_stations = get_list_of_stations()
    ingest_pdx_ridership_data(json_file_path, transit_station_ids, list_of_stations)


if __name__ == "__main__":
    run()
