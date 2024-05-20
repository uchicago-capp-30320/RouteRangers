import pytest
from parameterized import parameterized
from unittest import TestCase, skip

from app.route_rangers_api.utils.metric_processing import (
    dashboard_metrics,
    get_ridership,
    get_routes,
    get_pct_riders,
)


@skip("skipping until we can run tests differently locally vs on github")
class testDash(TestCase):
    # access database settings to actually connect
    @parameterized.expand(["Chicago", "NewYork", "Portland"])
    def test_ridership(self, city):
        all, bus, train = get_ridership(city)
        self.assertIs((bus != 0), True)
        self.assertIs((bus <= all), True)
        # seems like sometimes train is 0 (for nyc)

    @parameterized.expand(["Chicago", "NewYork"])
    def test_routes(self, city):
        all, bus, train = get_routes(city)
        self.assertIs(
            bus + train == all, True
        )  # not valid for portalnd with transit mode 6

    @parameterized.expand(["Chicago", "NewYork", "Portland"])
    def test_commuters(self, city):
        all, bus, train = get_pct_riders(city)
        self.assertIs(bus < all, True)
        self.assertIs(train < all, True)
        self.assertIs(all < 100, True)
