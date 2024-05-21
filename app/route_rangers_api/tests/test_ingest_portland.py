import pandas as pd
import pytest
import os
from unittest import TestCase, skip


class ExtractPortland(TestCase):
    def setUp(self):
        self.file_path = os.path.join(
            os.path.dirname(__file__), "data", "pdx_ridership_sample.json"
        )

        self.dataset = pd.read_json(self.file_path)

    def test_no_duplicates(self):
        """
        This tests makes sure that the data is at the
        location_id + date level in order to avoid double counting
        location ids
        """
        self.dataset.reset_index(drop=True, inplace=True)

        duplicate_check = self.dataset.duplicated(subset=["location_id", "date"])

        duplicate_rows = self.dataset[duplicate_check]

        assert (
            duplicate_rows.empty
        ), "Duplicates found at ['location_id',  'date'] level."

    def test_location_id_prefix(self):
        """
        This test makes sure that the values in the
        "location_id" field start with "Portland-"
        """
        assert (
            self.dataset["location_id"].str.startswith("Portland-").all()
        ), "Not all location_id values start with 'Portland-'"

    def test_column_count(self):
        """
        This test checks that the file has 3 fields: "location_id",
        "date", riders
        """
        expected_columns = {"location_id", "date", "riders"}
        actual_columns = set(self.dataset.columns)

        assert (
            actual_columns == expected_columns
        ), f"Expected columns: {expected_columns}, Actual columns: {actual_columns}"
