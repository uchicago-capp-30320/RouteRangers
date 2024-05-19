import os
import sys
from parameterized import parameterized
import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import patch, mock_open
from unittest import TestCase, skip
from app.scripts.ingest_census_data import (
    get_census_data,
    # store_census_data,
    upload_census_data,
    city_fips,
)


@pytest.fixture(scope="class")
def supported_cities():
    return list(city_fips.keys())


########################################################################################
# COMMAND LINE TESTS
########################################################################################


@pytest.mark.usefixtures("supported_cities")
class ExtractCensusData(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    # @pytest.mark.skip("no longer command line args for ingestion")
    # def test_valid_command_line_arg_correct_input(self):
    #     self.monkeypatch.setattr("sys.argv", ["extract_census_data.py", "portland"])
    #     assert valid_command_line_arg(supported_cities) == "portland"

    # def test_valid_command_line_arg_incorrect_input(monkeypatch, supported_cities):
    #     monkeypatch.setattr("sys.argv", ["extract_census_data.py", "miami"])
    #     with pytest.raises(SystemExit) as excinfo:
    #         valid_command_line_arg(supported_cities)
    #     assert "Unsupported city. Available options: nyc, chicago, portland" == str(
    #         excinfo.value
    #     )

    # @pytest.mark.parametrize(
    #     "argv", [(["extract_census_data.py"]), (["extract_census_data.py", "nyc", "miami"])]
    # )
    # def test_valid_command_line_arg_incorrect_number_inputs(
    #     monkeypatch, supported_cities, argv
    # ):
    #     monkeypatch.setattr("sys.argv", argv)
    #     with pytest.raises(SystemExit) as excinfo:
    #         valid_command_line_arg(supported_cities)
    #     assert "Retype command as 'python3 extract_census_data.py <city_name>'" == str(
    #         excinfo.value
    #     )

    # ########################################################################################
    # # DATA SCRAPING TESTS
    # ########################################################################################

    @patch("requests.get")
    def test_get_census_data_successful_api_call(self, mock_get):
        mock_data = [
            ["state_code", "county_code", "B01001_001E", "block_group"],
            ["36", "061", "1000", "1"],
            ["36", "047", "2000", "2"],
        ]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_data

        expected = [
            {
                "state_code": "36",
                "county_code": "061",
                "B01001_001E": "1000",
                "block_group": "1",
            },
            {
                "state_code": "36",
                "county_code": "047",
                "B01001_001E": "2000",
                "block_group": "2",
            },
        ]
        actual = get_census_data({"B01001_001E": "total_population"}, "36", "061")
        assert actual == expected

    @parameterized.expand([400, 401, 404, 429, 500, 503])
    @patch("requests.get")
    def test_get_census_data_api_failure(self, status_code, mock_get):
        mock_get.return_value.status_code = status_code
        mock_get.return_value.json.return_value = {"error": "Something went wrong"}
        assert get_census_data({"B01001_001E": "total_population"}, "36", "061") == []


class StoreCensusData(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()
        self.monkeypatch.setattr(os, "getcwd", lambda: "/fake/dir")
        self.monkeypatch.setattr(sys, "argv", ["script.py", "nyc"])

    # ########################################################################################
    # # DATA STORING TESTS
    # ########################################################################################

    # def mock_env(se):
    #     self.monkeypatch.setattr(os, "getcwd", lambda: "/fake/dir")
    #     self.monkeypatch.setattr(sys, "argv", ["script.py", "nyc"])

    @skip("no longer saving to csv")
    def test_store_census_data_with_valid_data(self):
        """
        Test
        """
        with patch(
            "builtins.open", mock_open(read_data="data"), create=True
        ) as mock_file:
            data = [
                {
                    "state_code": "36",
                    "county_code": "061",
                    "total_population": "1000",
                    "block_group": "1",
                },
                {
                    "state_code": "36",
                    "county_code": "047",
                    "total_population": "2000",
                    "block_group": "2",
                },
            ]
            upload_census_data(data)
            mock_file.assert_called_once_with("/fake/dir/nyc_data.csv", "w", newline="")
            handle = mock_file()
            assert handle.write.call_count > 2

    @skip("no longer writing to csv")
    def test_store_census_data_with_invalid_data(self):
        """
        Test
        """
        invalid_data = [
            {
                "state_code": "36",
            },
            {
                "county_code": "047",
            },
        ]
        with patch(
            "builtins.open", mock_open(read_data="data"), create=True
        ) as mock_file:
            upload_census_data(invalid_data)
            mock_file.assert_called_once_with("/fake/dir/nyc_data.csv", "w", newline="")
            handle = mock_file()
            assert handle.write.call_count == 3
