from django.contrib.gis.db import models
#from django.db import models 


##TODO: Update function that can extract the census tract from the location
## using the Census API

def get_census_tract(location) -> str:
    pass

#################################
######## TRANSIT MODELS #########
#################################

class Demographics(models.Model):
    census_tract = models.CharField(
        max_length=15
    )  # Check length of census tract if its uniform to enforce it here
    state = models.CharField(
        max_length=15
    )  # Check if it's worth to keep or if we should add a method
    county = models.CharField(max_length=15)  # Same as above
    population = models.IntegerField()
    age = models.IntegerField()
    median_income = models.IntegerField()
    transportation_to_work = models.CharField(
        verbose_name="Means of Transportation to Work"
    )
    work_commute_time = models.FloatField(verbose_name="Time of commuto to work")
    vehicles_available = models.IntegerField()
    disability_status = models.IntegerField()  #Check the type


class TransitStation(models.Model):
    station_id = models.CharField(max_length=30, primary_key=True)
    location = models.PointField()
    route = models.CharField(max_length=30)
    census_tract = models.CharField(max_length=30, null=True)

    def get_census_tract(self):
        self.census_tract = get_census_tract(self.location)


class TransitRidership(models.Model):
    station = models.ForeignKey(TransitStation, on_delete=models.PROTECT)
    date = models.DateField()
    ridership = models.IntegerField()


class BikeStation(models.Model):
    station_id = models.CharField(max_length=30, primary_key=True)
    location = models.PointField()
    census_tract = models.CharField(max_length=30, null=True)

    def get_census_tract(self):
        self.census_tract = get_census_tract(self.location)


class BikeRidership(models.Model):
    station = models.ForeignKey(BikeStation, on_delete=models.PROTECT)
    date = models.DateField()
    ridership = models.IntegerField()

#################################
######## SURVEY MODELS ##########
#################################
    
class Survey(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField("Created at",auto_now_add=True)
    questionnaire = models.JSONField()

class SurveyAnswer(models.Model):
    user_id = models.CharField(max_length=30)
    response_date = models.DateTimeField("Survey response date",auto_now_add=True)
    city = models.CharField(max_length=30)
    survey = models.ForeignKey(Survey,on_delete=models.PROTECT)
    answers = models.JSONField()

class PlannedRoute(models.Model):
    user_id = models.CharField(max_length=30)
    response_date = models.DateTimeField("Survey response date",auto_now_add=True)
    route = models.JSONField()
