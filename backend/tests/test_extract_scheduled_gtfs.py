import pytest

from ingestion.extract_scheduled_gtfs import (
    ingest_gtfs_feed,
    CTA_URL,
    METRA_URL,
    get_gtfs_component_dfs,
    add_extra_columns,
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


def test_feed_ingest(metra_feed):
    feed_city, feed_agency, feed = metra_feed
    assert feed_city == "Chicago"
    assert feed_agency == "Metra"
    assert feed is not None
    # TODO: assert that feed object is well-formed


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


def test_add_extra_columns(metra_feed):
    # TODO: test whether city and unique_id columns are added properly
    feed_city, feed_agency, feed = metra_feed
    component = feed.routes
    assert len(component.loc[:, "city"].unique()) == 1
    assert len(component.loc[:, "agency"].unique()) == 1
    assert component.loc[:, "city"].unique()[0] == "Chicago"
    assert component.loc[:, "agency"].unique()[0] == "Metra"
