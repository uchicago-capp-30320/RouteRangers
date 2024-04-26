
# Welcome to Our Community Planning Tool! 
The transit planning tool aims to revitalize public interest and participation in transit, driving increased ridership and creating more efficient networks that meet urban community needs. Learn about the City Transit Ecosystem! Show us routes that you would like in your neighborhood! Currently, we are working in New York, Chicago and Portland.

This tool will help City Planners and Locals alike as they:
-	Utilize data analytics to help facilitate a data informed transit planning process.
-	Collect feedback to gain insights into rider preferences.
-	Provide increased transparency in the route planning process.

## How to run the App?

Go to _____

## Project Structure

- `documentation/`: Contains relevant project implementation standards, design and planning information.
    - [coding standards](./documentation/code-standards.md)
    - [data model](./documentation/datamodel.md)
    - [frontend design](./documentation/design.md)
    - [endpoints](./documentation/endpoints.md)

- `app/`: Contains the django app which is composed of
    - `app/geodjango` is the web app orchestration where settings and app orchestration is done
    - `app/route_rangers_api` is the primary space for django app work
        - `app/route_rangers_api/models.py` defines the db table schemas and creates an ORM for ingestion and views to interact with
        - `app/route_rangers_api/views.py` define ways that the data is pulled from the tables and prepped for frontend visibility
        - `app/route_rangers_api/templates/` html templates for frontend pages
        - `app/route_rangers_api/static/` folder for frontend css and javascript files 
        - `app/route_rangers_api/tests.py`tests for testing the database, models, views (django stuff)
        - `app/route_rangers_api/urls.py` defined routes from the route rangers app that get put under the banner of `<weburl>:<port>/app/` so for example, if the route `/map` is defined within this file, then it would be called `<weburl>:<port>/app/map`

- `ingestion`: python scripts to pull transit and demographic data to prep db loading
- `tests`: pytests, primarily for testing ingestion


## Coding Practices

The following manual outlines the steps required to get started:
- [Check out our coding practices!](./documentation/code-standards.md)

## How was this data collected?
We pulled data from various city open data portals, City APIs, and scraped live GTFS data to create a robust picture of local transit. 

**Interested in hearing more?** Learn more about the App Architecture and Project Goals  [here](www.example.com)


## Authors

- Megan Moore
- Benjamin Leiva
- Lisette Solís
- JP Martínez
- Katherine Dumais
- Matt Jackson
- Jimena Salinas
