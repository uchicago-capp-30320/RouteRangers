import pandas as pd
import pytest
import os


@pytest.fixture
def dataset():

    file_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "pdx_ridership.json"
    )

    data = pd.read_json(file_path)

    return data


def test_no_duplicates(dataset):

    dataset.reset_index(drop=True, inplace=True)

    duplicate_check = dataset.duplicated(subset=["location_id", "date"])

    duplicate_rows = dataset[duplicate_check]

    assert duplicate_rows.empty, "Duplicates found at ['location_id',  'date'] level."
