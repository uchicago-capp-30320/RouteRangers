import pytest
import datetime
from parameterized import parameterized
from unittest import TestCase

from app.scripts.extract_scheduled_gtfs import (
    get_gtfs_feed,
    CTA_URL,
    METRA_URL,
    get_gtfs_component_dfs,
)


def metra_feed():
    feed_city, feed_agency, feed = get_gtfs_feed(METRA_URL)
    return feed_city, feed_agency, feed


def cta_feed():
    """
    Because CTA shapes.txt file is so large, this will take several seconds,
    and should not be called until a test needs it.
    """
    feed_city, feed_agency, feed = get_gtfs_feed(CTA_URL)
    return feed_city, feed_agency, feed


class ExtractGTFS(TestCase):

    # I think this is the django version of fixtures?
    def setUp(self):
        self.metra_feed = metra_feed()
        self.cta_feed = cta_feed()

    def test_feed_ingest(self):
        feed_city, feed_agency, feed = self.metra_feed
        assert feed_city == "CHI"
        assert feed_agency == "Metra"
        assert feed is not None
        # TODO: assert that feed object is well-formed

    def test_get_gtfs_component_dfs_metra(self):
        # Metra feed has neither transfers.txt nor geometrizable routes
        feed_city, _ , feed = self.metra_feed
        components_dict = get_gtfs_component_dfs(feed_city, feed)
        components = components_dict.keys()
        assert "routes" in components
        assert "trips" in components
        assert "stops" in components
        assert "stop_times" in components
        assert "shapes" in components
        assert "transfers" not in components

    def test_get_gtfs_component_dfs_cta(self):
        """TODO: refactor this so it is DRY"""
        feed_city, _ , feed = self.cta_feed
        components_dict = get_gtfs_component_dfs(feed_city, feed)
        components = components_dict.keys()
        assert "routes" in components
        assert "trips" in components
        assert "stops" in components
        assert "stop_times" in components
        assert "shapes" in components
        # CTA has BOTH transfers.txt AND geometrizable routes
        assert "transfers" in components

    # add extra cols no longer exists
    # def test_add_extra_columns(self):
    #     feed_city, feed_agency, feed = self.metra_feed
    #     component = add_extra_columns(feed_city, feed_agency, feed.routes)
    #     assert len(component.loc[:, "city"].unique()) == 1
    #     assert len(component.loc[:, "agency"].unique()) == 1
    #     assert component.loc[:, "city"].unique()[0] == "Chicago"
    #     assert component.loc[:, "agency"].unique()[0] == "Metra"
    #     assert component.loc[:, "uniq_route_id"].str.startswith("Chicago_Metra_").all()

    # these don't seem to be functions anymore
    # def test_combine_different_feeds(self):
    #     # TODO: consider making this a fixture
    #     chicago_combined_dfs = combine_different_feeds([CTA_URL, METRA_URL])
    #     assert "routes" in chicago_combined_dfs
    #     assert "shapes" in chicago_combined_dfs
    #     assert "trips" in chicago_combined_dfs
    #     assert "stops" in chicago_combined_dfs
    #     assert "stop_times" in chicago_combined_dfs
    #     assert "transfers" in chicago_combined_dfs
    #     # TODO: more detailed testing to make sure "Chicago_CTA_" and "Chicago_Metra_"
    #     # are represented in the uniq_id column for each sub-sheet (for now, that
    #     # seems minimally tested by test above this one)
