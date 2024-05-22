## Frontend/Client endpoints
These are the endpoints that users will engage with via the web app. Since we are using django these will directly interface with the django views and ORM so that we do not create a separate API to surface data from the database to the web app. 

* `/`
    * returns: home page for user to select city of focus

* `/dashboard/<city>/`
    * returns: city specific dashboard with metrics + map

* `/responses/<city>/`
    * returns: rider survey results for the given city of interest for policymakers and cityplanners to engage with

* `/survey/<city>/`
    * returns: survey form for riders to fill out and map to provide routes they would use

* `/about/`
    * returns: description of the project and listing of project members with cute pictures


## Backend Endpoints (likely not to be implemented for now)
The following routes are RESTful routes scoped for if the web app was built/deployed separately from the django app and was ingesting the data via WebAPI routes instead of directly from views (the way it is now)

#### Transit (bus/subway)
* GET:
    * `transit/<city>/stops/?transit-type=<bus/subway>`
        * returns: point data of stops for given city and transit type (default returns bus and subway)
    * `transit/<city>/routes?transit-type=<bus/subway/all>`
        * returns: route data for given city and transit type (default returns bus and subway)
    * `transit/<city>/scheduled-service/?transit-type=<bus/subway>`
        * returns: scheduled service to each transit stop for given city and transit type (default returns bus and subway)
    * `transit/<city>/ridership/?transit-type=<bus/subway>`
        * returns: ridership data for each stop location for given city and transit type (default returns bus and subway)

#### Bikes

* GET

    * bikes/<city>/stops
        * returns: point data of docking station for given city
    * bikes/<city>/ridership
        * returns: ridership for a given docking station in a given city

#### Demographics

* GET
    * `demographics/<city>/?type=<demographic-type`
        * returns: demographic metric at city level of certain type (ex. avg commute time, cars owned per household, etc.)

#### Users
For transit usage feedback

* POST/PUT if updating
    * `users/<city>/<user_id>/survey-submission`
        * returns: success code if successfully uploaded user survey data
    * `users/<city>/<user_id>/route-submission`
        * returns: success  code if successfully uploaded user route submission

* GET
    * `users/<city>/surveys`
        * returns: aggregate user feedback about transit for policymakers to use for a given city
    * `users/<city>/routes`
        * returns: aggregate user feedback about transit route demand to inform policymakers in a given city