import pandas as pd
import pytest


@pytest.fixture
def dataset():

    file_path = "/Users/jimenasalinas/Library/CloudStorage/Box-Box/Route Rangers/Transit dataset exploration/Portland Ridership Data/portland_ridership/PDX_ridership.json"

    data = pd.read_json(file_path)

    return data


def test_no_duplicates(dataset):

    dataset.reset_index(drop=True, inplace=True)

    duplicate_check = dataset.duplicated(subset=["location_id", "date"])

    duplicate_rows = dataset[duplicate_check]

    assert duplicate_rows.empty, "Duplicates found at ['location_id',  'date'] level."
