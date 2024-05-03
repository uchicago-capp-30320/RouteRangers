import pytest
import datetime
from ingestion.extract_chi_ridership_data import extract_daily_data, DATASETS, CHI_TZ

#########################
# Extract daily data tests
#########################


@pytest.mark.parametrize(
    "url,date,expected",
    [
        (
            DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
            125,
        ),
        (
            DATASETS["BUS_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
            94,
        ),
        (
            DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
            143,
        ),
        (
            DATASETS["SUBWAY_RIDERSHIP"]["URL"],
            datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
            143,
        ),
    ],
)
def test_extract_daily_data(url, date, expected):
    resp = extract_daily_data(url, date)
    assert len(resp) == expected
