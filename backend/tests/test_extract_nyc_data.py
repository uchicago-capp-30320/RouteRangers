import os
import sys
import pytest
import datetime
from dotenv import load_dotenv
from unittest.mock import patch, mock_open
from ingestion.extract_nyc_data import (
    make_request,
    extract_daily_data,
    create_daily_df,
    crawl,
    DATASETS,
)

#1. Check that it returns the correct number of responses given by:
# ceil(rows/50,000) 

@pytest.mark.parametrize(
    "url,date,expected",
    [
        (DATASETS["BUS_RIDERSHIP"]["URL"], datetime.datetime(2023, 9, 7), 1),
        (DATASETS["SUBWAY_RIDERSHIP"]["URL"], datetime.datetime(2023, 9, 7), 2),
    ],
)
def test_extract_daily(url, date, expected):
    resp = extract_daily_data(url,date)
    assert len(resp) == expected


#2. Check that it returns the correct n of rows and returning correct weekday/weekend classification
    

@pytest.mark.parametrize(
    "url,date,expected,weekday,dataset",
    [
        (DATASETS["BUS_RIDERSHIP"]["URL"],datetime.datetime(2023, 9, 7), 320,1,"BUS_RIDERSHIP"),
        (DATASETS["SUBWAY_RIDERSHIP"]["URL"], datetime.datetime(2023, 9, 7), 428,1,"SUBWAY_RIDERSHIP"),
        (DATASETS["BUS_RIDERSHIP"]["URL"],datetime.datetime(2023, 12, 2), 257,0,"BUS_RIDERSHIP"),
        (DATASETS["SUBWAY_RIDERSHIP"]["URL"], datetime.datetime(2023, 12, 2), 427,0,"SUBWAY_RIDERSHIP")
    ],
)

def test_create_daily_df_bus(url,date,dataset,expected,weekday):
    resp = extract_daily_data(url,date)
    df = create_daily_df(responses=resp,date=date,dataset=dataset)
    assert len(df) == expected
    assert df.iloc[0]["weekday"] == weekday
