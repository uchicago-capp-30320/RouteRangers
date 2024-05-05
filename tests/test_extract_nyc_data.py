import pytest
import datetime
from app.scripts.extract_nyc_data import (
    extract_daily_data,
    NY_TZ,
)


@pytest.mark.parametrize(
    "dataset,date,n_obs,first_station_ridership",
    [
        (
            "BUS_RIDERSHIP",
            datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
            320,
            10_678,
        ),
        (
            "SUBWAY_RIDERSHIP",
            datetime.datetime(2023, 9, 7, tzinfo=NY_TZ),
            428,
            11_174,
        ),
        (
            "BUS_RIDERSHIP",
            datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
            320,
            10_868,
        ),
        (
            "SUBWAY_RIDERSHIP",
            datetime.datetime(2023, 2, 28, tzinfo=NY_TZ),
            428,
            10_532,
        ),
        (
            "BUS_RIDERSHIP",
            datetime.datetime(2022, 11, 5, tzinfo=NY_TZ),
            255,
            7_852,
        ),
        (
            "SUBWAY_RIDERSHIP",
            datetime.datetime(2022, 11, 5, tzinfo=NY_TZ),
            428,
            7_085,
        ),

    ],
)
def test_create_daily_weekday(dataset,date,n_obs,first_station_ridership):
    results = extract_daily_data(dataset=dataset, date=date)
    assert len(results) == n_obs
    assert int(float(results[0]["total_ridership"])) == first_station_ridership



