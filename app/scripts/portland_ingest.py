"""
OBJECTIVE: Ingest Portland Ridership Data into our Database
AUTHOR: Jimena Salinas
DATE: 05/06/2024

SOURCES: the data sets were obtained by a direct request to the 
TriMet Public Records department. This is the link to the form
to request data sets for Tri Met: 
https://trimet.org/publicrecords/recordsrequest.htm
The  Receipt ID for this Public Records Request is PRR 2024-254.

VARIABLES:
    - station_id: (str) combines the city "Portland" with a given stop_id
    - date: (datetime) represents a day in the format yyyy-mm-dd, only includes
    values for 2023
    - ridership: (int) represents the average number of bus and light rail Tri Met
    riders. The riders value was originally provided as an average by season 
    and day type (Saturday, Sunday, and Weekday). In order to fit the data model
    for the project which is at the datetime level, the data has been mapped to dates in 2023.
"""
