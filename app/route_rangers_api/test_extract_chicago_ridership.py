import pytest
import datetime
from app.scripts.extract_chi_ridership_data import extract_daily_data, DATASETS, CHI_TZ
from unittest import TestCase

##########################
# Extract daily data tests
##########################

from parameterized import parameterized

class ExtractChiData(TestCase):
    @parameterized.expand([
        [DATASETS["BUS_RIDERSHIP"]["URL"],
        datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
        125],
        [DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
            94,],
        [DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
            143],
        [DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
            143]
    ])
    
    def test_extract_daily_data(self,url, date, expected):
        resp = extract_daily_data(url, date)
        self.assertIs(len(resp),expected)