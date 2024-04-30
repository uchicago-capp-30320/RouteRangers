from django.contrib.gis.db import models

##TODO: Update function that can extract the census tract from the location
## using the Census API


def get_census_tract(location) -> str:
    pass


#################################
######## TRANSIT MODELS #########
#################################


class Demographics(models.Model):
    """
    Class to represent demographic data pulled from the ACS Survey
    """

    census_tract = models.CharField(
        max_length=15
    )  # Check length of census tract if its uniform to enforce it here
    state = models.CharField(
        max_length=15
    )  # Check if it's worth to keep or if we should add a method
    county = models.CharField(max_length=15)  # Same as above
    median_income = models.IntegerField()
    transportation_to_work = models.CharField(
        verbose_name="Means of Transportation to Work"
    )
    work_commute_time = models.FloatField(verbose_name="Time of commuto to work")
    vehicles_available = models.IntegerField()
    disability_status = models.IntegerField(
        verbose_name="Number of people with disability"
    )


class TransitStation(models.Model):
    """
    Class that represent subway stations and bus stops
    """

    station_id = models.CharField(max_length=30, primary_key=True)
    route = models.ForeignKey(TransitRoute, on_delete=models.PROTECT)
    location = models.PointField()
    census_tract = models.CharField(max_length=30, null=True)

    def get_census_tract(self):
        self.census_tract = get_census_tract(self.location)


class TransitRoute(models.Model):
    """
    Class that represent subway lines and bus routes
    """

    route_id = models.CharField(max_length=30, primary_key=True)
    geo_representation = models.LineStringField()
    mode = models.CharField(max_length=10)


class TransitRidership(models.Model):
    """
    Class that represent subway and bus ridership
    """

    station = models.CharField(max_length=30)
    date = models.DateField()
    ridership = models.IntegerField()


class BikeStation(models.Model):
    """
    Class that represent bike sharing docking stations
    """

    station_id = models.CharField(max_length=30, primary_key=True)
    location = models.PointField()
    census_tract = models.CharField(max_length=30, null=True)

    def get_census_tract(self):
        self.census_tract = get_census_tract(self.location)


class BikeRidership(models.Model):
    """
    Class that represent bike sharing ridership
    """

    station = models.ForeignKey(BikeStation, on_delete=models.PROTECT)
    date = models.DateField()
    n_started = models.IntegerField()
    n_ended = models.IntegerField()


#################################
######## SURVEY MODELS ##########
#################################


class Survey(models.Model):
    """
    Class that represents surveys deployed
    """

    name = models.CharField(max_length=30)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    questionnaire = models.JSONField()


class SurveyAnswer(models.Model):
    """
    Class that represents answers to surveys
    """

    user_id = models.CharField(max_length=30)
    response_date = models.DateTimeField("Survey response date", auto_now_add=True)
    city = models.CharField(max_length=30)
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    answers = models.JSONField()


class PlannedRoute(models.Model):
    """
    Class that represents answers to 'Plan your route' feature
    """

    user_id = models.CharField(max_length=30)
    response_date = models.DateTimeField("Survey response date", auto_now_add=True)
    route = models.LineStringField()
