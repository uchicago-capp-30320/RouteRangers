import unittest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../../"))
from ..utils.heatmap_data_prep import calculate_demographic_metrics


class TestCalculateDemographicMetrics(unittest.TestCase):
    def setUp(self):
        # create fake data
        data = {
            "census_tract": [1, 2],
            "state": ["XX", "YY"],
            "county": ["AA", "BB"],
            "median_income": [50000, 60000],
            "work_commute_time_15_29": [100, 200],
            "work_commute_time_30_44": [150, 250],
            "work_commute_time_45_59": [50, 150],
            "work_commute_time_60_89": [20, 80],
            "work_commute_time_less_15": [300, 400],
            "work_commute_time_over_90": [10, 20],
            "transportation_to_work_public": [200, 300],
            "transportation_to_work_bus": [100, 200],
            "transportation_to_work_subway": [50, 100],
            "population": [1000, 2000],
            "geographic_delimitation": [Point(1, 1), Point(2, 2)],
        }

        self.demographics_df = gpd.GeoDataFrame(
            data, geometry="geographic_delimitation"
        )
        self.demographics_df.set_crs("EPSG:4326", inplace=True)

    def test_calculate_demographic_metrics(self):
        """
        test calculate_demographic_metrics fuction which
        calculates the weighted avg commute time based on the Census
        fields which provide number of people by time category, check
        percentages for commute modes are correct too
        """
        result_df = calculate_demographic_metrics(self.demographics_df)

        # expected output
        expected_data = {
            "census_tract": [1, 2],
            "state": ["XX", "YY"],
            "county": ["AA", "BB"],
            "median_income": [50000, 60000],
            "work_commute_time_15_29": [100, 200],
            "work_commute_time_30_44": [150, 250],
            "work_commute_time_45_59": [50, 150],
            "work_commute_time_60_89": [20, 80],
            "work_commute_time_less_15": [300, 400],
            "work_commute_time_over_90": [10, 20],
            "transportation_to_work_public": [200, 300],
            "transportation_to_work_bus": [100, 200],
            "transportation_to_work_subway": [50, 100],
            "population": [1000, 2000],
            "weighted_commute_15_29": [2.20, 2.20],
            "weighted_commute_30_44": [5.55, 4.62],
            "weighted_commute_45_59": [1.58, 2.36],
            "weighted_commute_60_89": [1.49, 2.98],
            "weighted_commute_less_15": [2.25, 1.50],
            "weighted_commute_over_90": [1.04, 1.04],
            "percentage_public_to_work": [20.00, 15.00],
            "percentage_bus_to_work": [10.00, 10.00],
            "percentage_subway_to_work": [5.00, 5.00],
            "total_weighted_commute_time": [14.11, 14.71],
        }

        expected_df = pd.DataFrame(expected_data)

        # ignore checking for geo format, more worried about arithmetic
        # cals, will use map for geographies
        result_df = result_df.drop(columns=["geographic_delimitation"])

        result_columns = result_df.columns

        expected_df = expected_df[result_columns]

        pd.testing.assert_frame_equal(result_df, expected_df)


if __name__ == "__main__":
    unittest.main()
