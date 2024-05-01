# Datamodel prototype 

A visual representation of the datamodel can be found in the following [lucidchart link](https://lucid.app/lucidchart/acedfe58-359d-42ba-8dc9-b9421517ead9/edit?invitationId=inv_a9fee266-b5b0-4243-bfa8-ccf7f44afd22&referringApp=slack&page=0_0#)

Relationships between tables are specified by the lines connecting multiple tables. In the diagram its specified the type of matching expected, where 1:1 represents a one to one matching, m:1 many to one, and m:m many to many. 

We datamodel is composed of the following tables:
- Demographics
- TransitStation
- TransitRidership
- BikeStation
- BikeRidership
- Survey
- SurveyAnswer
- PlannedRoute

The **Demographics** table contains demographic information at the Census Tract level, containing information for the following variables: Population, Median Household Income, Means of Transportation to Work, Time of Departure to Go to Work, Travel Time to Work, Vehicles Available and Disability Status. The table is structured in the following way: 

| Name                           | Type                 | Description                                          |
| ------------------------------ | -------------------- | -----------------------------------------------------|
| census_tract                   | string               | Census tract at which demographic data is aggregated |
| state                          | string               | State the census tract is part of                    |
| county                         | string               | County the census tract is part of                   |
| population                     | integer              | Population in census tract                           |
| median_income                  | integer              | Median income in census tract                        |
| transportation_to_work_total   | integer              | Total number of people considered for mean of transportation to work question  |
| transportation_to_work_car     | integer              | Number of people that use cars as mean of transportation to work |
| transportation_to_work_public  | integer              | Number of people that use public transportation as mean of transportation to work |
| work_commute_time              | integer              | Average time for work commute in census tract        |
| vehicles_available             | integer              | Number of vehicles available in census tract         |
| disability status              | integer              | Number of people with a disability in the census tract |

The public transportation information from each city is stored in the **TransitStation** and **TransitRidership** tables. The TransitStation represent each bus stop and subway station while the TransitRidership table represents daily ridership information for each subway station and bus route. The **TransitStation** is structured of the following way:

| Name                | Type                 | Description                                          |
| -------------------  | -------------------- | ---------------------------------------------------- |
| station_id          | string               | Station identificator for bus stop or subway station |
| transportation_mode | string               | Mode of transportation (bus, subway, train)          |
| location            | geometric point      | Location of the station/bus stop                     |
| route               | string               | Bus route or subway line the station is part of      |
| census_tract        | string               | Census tract in which the station is located in      |

The **TransitRidership** table is represented by the following table:

| Name                | Type                 | Description                                    |
| ------------------- | -------------------- | --------------------------------------------   |
| transit_unit        | string               | Bus route or subway stop identificator         |
| transportation_mode | string               | Mode of transportation (bus, subway, train)    |
| date                | Datetime object      | Date of the reported ridership                 |
| ridership           | integer              | Number of daily riders in the station or route |


The **BikeStations** and **BikeRidership** represent the stations and ridership data for publicly available bikes for rent (CitiBikes,Divvy and BIKETOWN). The **BikeStation** table is represented in the following way:

| Name              | Type                 | Description                                          |
| ----------------- | -------------------- | ---------------------------------------------------- |
| station_id        | string               | ID of the bike docking station                       |
| location          | geometric point      | Location of the bike docking station                 |
| census_tract      | string               | Census tract in which the bike station is located in |

The **BikeRidership** table is structured in the following way:

| Name              | Type                 | Description                                  |
| ----------------- | -------------------- | -------------------------------------------- |
| station           | string               | Bike station for which ridership is reported |
| date              | Datetime object      | Date of the reported ridership               |
| n_started         | integer              | Number of trips started at the station       |
| n_ended           | integer              | Number of trips ended at the station         |

For the survey information there are two tables that represent the necessary information **Survey** and **SurveyAnswer**. Survey stores every survey that has been deployed in the platform while SurveyAnswer represents a users survey answer.

The **Survey** table is represented by the following structure:

| Name              | Type                 | Description                                                                         |
| ----------------- | -------------------- | ----------------------------------------------------------------------------------- |
| name              | string               | Name of the survey                                                                  |
| created_at        | Datetime object      | Date the survey was created                                                         |
| questionnaire     | JSON                 | JSON object with representation of the different questions and its possible answers |

The **SurveyAnswer** table is structured in the following way:

| Name                 | Type                 | Description                                     |
| -------------------- | -------------------- | ----------------------------------------------- |
| user_id              | string               | Id of the user answering the survey             |
| city                 | string               | City of residence of the user                   |
| survey               | ForeignKey(Survey)   | Survey that the user is answering               |
| response_date        | Datetime object      | Date and time of when the answer was submitted  |
| answer               | JSON                 | JSON object containing the users answers        |