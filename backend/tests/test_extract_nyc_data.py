import pytest
import datetime
from ingestion.extract_nyc_data import (
    extract_daily_data,
    create_daily_df,
    DATASETS,
    NY_TZ,
)


@pytest.mark.parametrize(
    "url,date,expected,dataset",
    [
        (
            DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
            320,
            "BUS_RIDERSHIP",
        ),
        (
            DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
            428,
            "SUBWAY_RIDERSHIP",
        ),
        (
            DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
            320,
            "BUS_RIDERSHIP",
        ),
        (
            DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
            428,
            "SUBWAY_RIDERSHIP",
        ),
    ],
)
def test_create_daily_weekday(url, date, dataset, expected):
    resp = extract_daily_data(url, date)
    df = create_daily_df(responses=resp, date=date, dataset=dataset)
    assert len(df) == expected
    assert df.iloc[0]["weekday"] == 1


@pytest.mark.parametrize(
    "url,date,expected,dataset",
    [
        # (DATASETS["BUS_RIDERSHIP"]["URL"],datetime.datetime(2023, 12, 2,tzinfo=NY_TZ), 257,"BUS_RIDERSHIP"),
        (
            DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 12, 2, tzinfo=NY_TZ),
            427,
            "SUBWAY_RIDERSHIP",
        ),
        (
            DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2022, 11, 5, tzinfo=NY_TZ),
            255,
            "BUS_RIDERSHIP",
        ),
    ],
)
def test_create_daily_weekend(url, date, dataset, expected):
    resp = extract_daily_data(url, date)
    df = create_daily_df(responses=resp, date=date, dataset=dataset)
    assert len(df) == expected
    assert df.iloc[0]["weekday"] == 0
