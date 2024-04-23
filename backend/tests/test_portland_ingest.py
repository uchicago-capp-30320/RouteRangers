import pandas as pd
import pytest
import os


@pytest.fixture
def dataset():

    file_path = os.path.join(
        os.path.dirname(__file__), "data", "pdx_ridership_sample.json"
    )

    data = pd.read_json(file_path)

    return data


def test_no_duplicates(dataset):
    """
    This tests makes sure that the data is at the
    location_id + date level in order to avoid double counting
    location ids
    """
    dataset.reset_index(drop=True, inplace=True)

    duplicate_check = dataset.duplicated(subset=["location_id", "date"])

    duplicate_rows = dataset[duplicate_check]

    assert duplicate_rows.empty, "Duplicates found at ['location_id',  'date'] level."


def test_location_id_prefix(dataset):
    """
    This test makes sure that the values in the
    "location_id" field start with "Portland-"
    """
    assert (
        dataset["location_id"].str.startswith("Portland-").all()
    ), "Not all location_id values start with 'Portland-'"


def test_column_count(dataset):
    """
    This test checks that the file has 3 fields: "location_id",
    "date", riders
    """
    expected_columns = {"location_id", "date", "riders"}
    actual_columns = set(dataset.columns)

    assert (
        actual_columns == expected_columns
    ), f"Expected columns: {expected_columns}, Actual columns: {actual_columns}"
