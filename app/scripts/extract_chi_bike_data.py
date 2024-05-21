import os
from typing import List
import pytz
import pandas as pd
from dotenv import load_dotenv
from route_rangers_api.models import (
    BikeRidership,
    BikeStation,
)
from django.contrib.gis.geos import Point
from django.db import IntegrityError
from app.scripts.utils import (
    make_request,
    process_daily_ridership_data
)

#########################
# Load and define variables
#########################
load_dotenv()

DATA_PORTAL_APP_TOKEN = os.getenv("DATA_PORTAL_APP_TOKEN")
BIKE_DATA_DIR = os.getenv("BIKE_DATA_DIR")

REQUEST_DELAY = 0.2
RESULTS_PER_PAGE = 50000  # Max number of results for API
TIMEOUT = 30

CHI_TZ = pytz.timezone("America/Chicago")


def extract_bike_stations_api(app_token=DATA_PORTAL_APP_TOKEN) -> List:
    """
    Extract bike station data from Chicago API
    """
    params = {"$$APP_TOKEN": app_token}
    resp = make_request(
        url="https://data.cityofchicago.org/resource/bbyy-e7gq.json", params=params
    )
    results = resp.json()
    return results


def ingest_bike_stations() -> None:
    """
    Ingest bike station data into BikeStation table
    """
    bike_stations = extract_bike_stations_api()
    for station in bike_stations:
        try:
            print(f"ingesting CHI {station['id']}")
            obs = BikeStation(
                city="CHI",
                station_id=station["id"],
                station_name=station["station_name"],
                short_name=station["short_name"],
                n_docks=station["total_docks"],
                location=Point(station["location"]["coordinates"]),
            )
            obs.save()
        except KeyError:
            try:
                print(f"ingesting CHI {station['id']}, no short_name")
                obs = BikeStation(
                    city="CHI",
                    station_id=station["id"],
                    station_name=station["station_name"],
                    n_docks=station["total_docks"],
                    location=Point(station["location"]["coordinates"]),
                )
                obs.save()
            except IntegrityError:
                print(f"Observation{station['station_name']} already ingested")
            except Exception as e:
                print(f"Observation {station['station_name']} not ingested: {e}")
        except IntegrityError:
            print(f"Observation{station['station_name']} already ingested")
        except Exception as e:
            print(f"Observation {station['station_name']} not ingested: {e}")
        


def create_daily_ridership_month(filepath: str) -> pd.DataFrame:
    """
    Create a dataframe with daily information by station with the
    number of trips started and ended for one monthly file
    """
    monthly_df = pd.read_csv(filepath)
    ridership_df = process_daily_ridership_data(monthly_df)

    return ridership_df


def ingest_monthly_data(monthly_ridership_df: pd.DataFrame) -> None:
    """
    Ingest ridership at the daily level into the BikeRidership table
    """
    for row in monthly_ridership_df.itertuples():
        try:
            obs_station = (
                BikeStation.objects.filter(city="CHI", short_name=row.station_id)
                .first()
                .id
            )
            print(f"Observation Station: {obs_station}")
            obs = BikeRidership(
                station_id=obs_station,
                date=row.date,
                n_started=row.n_rides_started,
                n_ended=row.n_rides_ended,
            )
            obs.save()
        except IntegrityError:
            print(f"Observation Station: {obs_station} - {row.date} already ingested")
        except Exception as e:
            print(f"Observation Station {obs_station} - {row.date} not ingested: {e}")


def ingest_trip_data():
    """
    Ingest the divvy data into the BikeRidership table
    """
    for file in os.listdir(f"{BIKE_DATA_DIR}/2023-divvy-tripdata/"):
        if file != ".DS_Store":
            monthly_df = create_daily_ridership_month(
                f"{BIKE_DATA_DIR}/2023-divvy-tripdata/{file}"
            )
            ingest_monthly_data(monthly_df)


def run(data:str = "both"):
    ingest_bike_stations()
    ingest_trip_data()

    if data == "stations":
        ingest_bike_stations()
    elif data == "ridership":
        ingest_trip_data()
    elif data == "both":
        ingest_bike_stations()
        ingest_trip_data()
    else:
        print("Select one of the following options 'stations', 'ridership' or 'both'")
