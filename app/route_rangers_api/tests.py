import pytest
from django.urls import reverse


def test_fake():
    assert 1 == 1


@pytest.mark.django_db
def test_hello_view(client):
    url = reverse("/")

    response = client.get(url)
    assert response.status_code == 200


import pytest

from app.scripts.extract_scheduled_gtfs import (
    # ingest_gtfs_feed,
    CTA_URL,
    METRA_URL,
    get_gtfs_component_dfs,
    # add_extra_columns,
    # combine_different_feeds,
)


# use a fixture to pre_load some relevant feed ingestions
# https://docs.pytest.org/en/6.2.x/fixture.html
# https://stackoverflow.com/questions/17801300/how-to-run-a-method-before-all-tests-in-all-classes
@pytest.fixture(scope="session", autouse=True)
def metra_feed():
    feed_city, feed_agency, feed = ingest_gtfs_feed(METRA_URL)
    return feed_city, feed_agency, feed


@pytest.fixture(scope="session")
def cta_feed():
    """
    Because CTA shapes.txt file is so large, this will take several seconds,
    and should not be called until a test needs it.
    """
    feed_city, feed_agency, feed = ingest_gtfs_feed(CTA_URL)
    return feed_city, feed_agency, feed


@pytest.mark.skip(reason="refactor currently breaking test")
def test_feed_ingest(metra_feed):
    feed_city, feed_agency, feed = metra_feed
    assert feed_city == "Chicago"
    assert feed_agency == "Metra"
    assert feed is not None
    # TODO: assert that feed object is well-formed


@pytest.mark.skip(reason="refactor currently breaking test")
def test_get_gtfs_component_dfs_metra(metra_feed):
    # Metra feed has neither transfers.txt nor geometrizable routes
    feed_city, feed_agency, feed = metra_feed
    components_dict = get_gtfs_component_dfs(feed_city, feed_agency, feed)
    components = components_dict.keys()
    assert "routes" in components
    assert "trips" in components
    assert "stops" in components
    assert "stop_times" in components
    assert "shapes" in components
    assert "transfers" not in components
    assert "shape_geometries" not in components


@pytest.mark.skip(reason="refactor currently breaking test")
def test_get_gtfs_component_dfs_cta(cta_feed):
    """TODO: refactor this so it is DRY"""
    feed_city, feed_agency, feed = cta_feed
    components_dict = get_gtfs_component_dfs(feed_city, feed_agency, feed)
    components = components_dict.keys()
    assert "routes" in components
    assert "trips" in components
    assert "stops" in components
    assert "stop_times" in components
    assert "shapes" in components
    # CTA has BOTH transfers.txt AND geometrizable routes
    assert "transfers" in components
    assert "shape_geometries" in components


@pytest.mark.skip(reason="refactor currently breaking test")
def test_add_extra_columns(metra_feed):
    feed_city, feed_agency, feed = metra_feed
    component = add_extra_columns(feed_city, feed_agency, feed.routes)
    assert len(component.loc[:, "city"].unique()) == 1
    assert len(component.loc[:, "agency"].unique()) == 1
    assert component.loc[:, "city"].unique()[0] == "Chicago"
    assert component.loc[:, "agency"].unique()[0] == "Metra"
    assert component.loc[:, "uniq_route_id"].str.startswith("Chicago_Metra_").all()


@pytest.mark.skip(reason="refactor currently breaking test")
def test_combine_different_feeds(cta_feed, metra_feed):
    # TODO: consider making this a fixture
    chicago_combined_dfs = combine_different_feeds([CTA_URL, METRA_URL])
    assert "routes" in chicago_combined_dfs
    assert "shapes" in chicago_combined_dfs
    assert "trips" in chicago_combined_dfs
    assert "stops" in chicago_combined_dfs
    assert "stop_times" in chicago_combined_dfs
    assert "transfers" in chicago_combined_dfs
    # TODO: more detailed testing to make sure "Chicago_CTA_" and "Chicago_Metra_"
    # are represented in the uniq_id column for each sub-sheet (for now, that
    # seems minimally tested by test above this one)


import datetime
from app.scripts.extract_chi_ridership_data import extract_daily_data, DATASETS, CHI_TZ
from unittest import TestCase

##########################
# Extract daily data tests
##########################

from parameterized import parameterized


class ExtractChiData(TestCase):
    @parameterized.expand(
        [
            [
                DATASETS["BUS_RIDERSHIP"]["URL"],
                datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
                125,
            ],
            [
                DATASETS["BUS_RIDERSHIP"]["URL"],
                datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
                94,
            ],
            [
                DATASETS["SUBWAY_RIDERSHIP"]["URL"],
                datetime.datetime(2023, 2, 28, tzinfo=CHI_TZ),
                143,
            ],
            [
                DATASETS["SUBWAY_RIDERSHIP"]["URL"],
                datetime.datetime(2023, 3, 4, tzinfo=CHI_TZ),
                143,
            ],
        ]
    )
    def test_extract_daily_data(self, url, date, expected):
        resp = extract_daily_data(url, date)
        self.assertIs(len(resp), expected)
