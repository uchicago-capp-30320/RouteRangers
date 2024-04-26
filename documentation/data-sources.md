# Data Source Documentation

### GTFS Data Overview

For stop, routes, and scheduling data our project utilizes GTFS data obtained from the different cities’ transit authorities. GTFS (General Transit Feed Specification) is a standardized format for public transportation schedules and associated geographic information. It's widely used by transit agencies and developers to share and consume transit data, and it greatly simplifies the process working with data from across cities. Here's a brief overview of the GTFS data obtained for New York City, Chicago, and Portland (Oregon):

  - New York City: The data obtained from MTA includes subway and bus information. Subway data is available as a single feed, while bus data is divided by borough, with separate feeds for Bronx, Brooklyn, Manhattan, Queens, Staten Island, and the MTA Bus Company.

  - Chicago: The data encompasses both the CTA (Chicago Transit Authority) and Metra (commuter rail) systems.

  - Portland: Trimet provides the transit data for Portland, including bus, light rail, and commuter rail services.


### Demographic Data Overview

The project currently supports socio-demographic data extraction at the census tract and block group level from the US Census for New York (NYC), Chicago, and Portland, along with their corresponding FIPS codes. Key variables extracted include total population, median household income, educational attainment, age demographics, and disability statistics.

#### Query Limits

The data ingestion process is subject to the following query limits imposed by the U.S. Census API:

Variables per Query: 50 variables

Queries per Day: 500 queries

#### Cities and FIPS Codes

The script supports data extraction for the following cities along with their corresponding FIPS codes:

New York (NYC):

    - Manhattan (New York County, FIPS: 36061)
    
    - Brooklyn (Kings County, FIPS: 36047)
    
    - Queens (Queens County, FIPS: 36081)
    
    - Bronx (Bronx County, FIPS: 36005)
    
    - Staten Island (Richmond County, FIPS: 36085)

Chicago:

    - Chicago (Cook County, FIPS: 17031)

Portland:

    - Portland (Multnomah County, FIPS: 41051)

#### Data Sources and Geography Levels

The demographic data ingestion scripts utilize data from the following sources:

- Census 2020:

Provides data at the state, county, and census tract levels.

- ACS 2022 5-Year Estimates:

Provodes data at the state, county, census tract, and block group levels.

- PDB 2022:

Provides data at the state, county, census tract, and block group levels.

#### Variables

The demographic data ingestion script extracts the following key variables:

- Total Population (ID: B01001_001E): Represents the total population count.

- Median Household Income (2022 Inflation Adjusted) (ID: B29004_001E): Represents the median household income for the specified area.

- Bachelor's Degree (ID: B15003_022E): Represents the count of individuals holding a bachelor's degree.

- Age: Represents demographic breakdowns by age groups.

- Disability: Represents data related to individuals with disabilities.


### Ridership Data Overview

Unlike GTFS, ridership data is not standardized across different transit authorities, and the level of granularity and format varies across cities.

- New York City:

Ridership data from the MTA is pulled from the New York State Data Portal from two different sources (i) Bus Ridership dataset and (ii) Subway Ridership dataset which are extracted using the State of New York API.

Each row of the MTA Bus Ridership dataset counts the total number of people who ride anywhere along each bus line at the hourly level disaggregating by different kinds of fares.  To fit into the data model the data is aggregated at the daily level to obtain the total number of riders at the daily level on a bus route.  The information publicly available on this dataset dates back to February 2022.

Each observation of the MTA Subway Ridership dataset counts the total number of people who enters a station at the hour level disaggregating by the different kinds of fares. To fit into the data model the data is aggregated at the daily level to obtain the total number of riders at the daily level on the subway station. The information publicly available on this dataset dates back to February 2022.


- Chicago:

Ridership data for CTA buses and trains (last updated: Jan. 25, 2024) is accessible via point-and-click download on the City of Chicago Open Data Portal, or via API endpoint with valid API key (which we have yet to set up).

Each row of data for CTA bus routes counts the total number of people who (tap in to?) ride anywhere along each bus line on each day dating back to Jan. 1, 2001 (i.e. specific stop of bus entry and exit is not recorded). Each row designates whether the day was a weekday, a Saturday, or a Sunday/Holiday. The routes are identified only by route number.

Each row of data for CTA train stations counts the total number of people who tappedin to ride at that station on each day dating back to Jan. 1, 2001; CTA does not record station of exit. Each row designates whether the day was a weekday, a Saturday, or a Sunday/Holiday. The stops are identified by the same five-digit stop_id number as appears in stops.txt.

As far as we know, daily Metra ridership data on a per-stop basis is not readily available; total ridership of each line per year is available here, and it may be possible to obtain monthly ridership figures by line with some complicated web scraping (e.g. of pages like this one). The latest per-station boarding data we could find is from 2018 (i.e. a pre-COVID year, when ridership was much higher and thus unreliable for present-day use) and would need to be web scraped or extracted from PDF. Given the effort-to-reward ratio of getting Metra data of any quality, doing so is a lower priority for us.


- Portland:

The ridership data for Portland is not openly available through an API. In order to obtain ridership data, our team reached out to the TriMet Public Records department. The department answered our request, PRR 2024-254, with a set of 6 csv files with ridership data aggregated at the Saturday, Sunday, Weekday level by season for 2023 for each route. However, the department only provided records for spring and summer. For future inquiries, the TriMet public records department can be reached using this link: https://trimet.org/publicrecords/recordsrequest.htm

In order to match the data model, the aggregated data sets were reformatted to expand the data aggregated at the Saturday, Sunday, Weekday level by season for 2023 into data at the date and route level.

