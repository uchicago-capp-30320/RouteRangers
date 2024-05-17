import pytest
from django.urls import reverse
import datetime
from parameterized import parameterized
from unittest import TestCase
from requests.exceptions import ReadTimeout

from app.scripts.extract_chi_ridership_data import extract_daily_data, DATASETS, CHI_TZ
from app.scripts.extract_nyc_data import DATASETS, NY_TZ, extract_daily_data


###################
## NY Extract tests
###################


class ExtractNYData(TestCase):
    @parameterized.expand(
        [
            [
                "BUS_RIDERSHIP",
                datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
                320,
                10_678,
            ],
            [
                "SUBWAY_RIDERSHIP",
                datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
                428,
                11_174,
            ],
            [
                "BUS_RIDERSHIP",
                datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
                320,
                10_868,
            ],
            [
                "SUBWAY_RIDERSHIP",
                datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
                428,
                10_532,
            ],
            [
                "BUS_RIDERSHIP",
                datetime.datetime(2022, 11, 5, tzinfo=NY_TZ),
                255,
                7_852,
            ],
            [
                "SUBWAY_RIDERSHIP",
                datetime.datetime(2022, 11, 5, tzinfo=NY_TZ),
                428,
                7_085,
            ],
        ]
    )
    def test_extract_daily_data(self, dataset, date, n_obs, first_station_ridership):
        try:
            results = extract_daily_data(dataset=dataset, date=date)
        except ReadTimeout as e:
            print(f"{e} request timed out, retry if critical")
        self.assertIs(len(results) == n_obs, True)
        self.assertIs(
            int(float(results[0]["total_ridership"])) == first_station_ridership, True
        )


##########################
# CHI Extract tests
##########################

from parameterized import parameterized


class ExtractChiData(TestCase):
    @parameterized.expand(
        [
            [
                "BUS_RIDERSHIP",
                datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
                320,
            ],
            [
                "BUS_RIDERSHIP",
                datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
                255,
            ],
            [
                "SUBWAY_RIDERSHIP",
                datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
                428,
            ],
            [
                "SUBWAY_RIDERSHIP",
                datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
                424,
            ],
        ]
    )
    def test_extract_daily_data(self, url, date, expected):
        try:
            resp = extract_daily_data(url, date)
        except ReadTimeout as e:
            print(f"{e} request timed out, retry if critical")
        self.assertIs(len(resp) == expected, True)
