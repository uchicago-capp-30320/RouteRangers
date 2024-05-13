from django.contrib.gis.db import models
from app.route_rangers_api.utils.city_mapping import CITIES_CHOICES

#################################
###### DEMOGRAPHIC MODELS #######
#################################


class Demographics(models.Model):
    """
    Class to represent demographic data pulled from the ACS Survey
    """

    block_group = models.CharField(max_length=64)
    census_tract = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    county = models.CharField(max_length=64)
    median_income = models.IntegerField(
        verbose_name="Median household income", null=True
    )
    transportation_to_work = models.IntegerField(
        verbose_name="Means of Transportation to Work Total", null=True
    )
    transportation_to_work_car = models.IntegerField(
        verbose_name="Means of Transportation to Work: Car", null=True
    )
    transportation_to_work_public = models.IntegerField(
        verbose_name="Means of Transportation to Work: Public Transportation", null=True
    )
    transportation_to_work_bus = models.IntegerField(
        verbose_name="Means of Transportation to Work: Bus", null=True
    )
    transportation_to_work_subway = models.IntegerField(
        verbose_name="Means of Transportation to Work: subway", null=True
    )
    work_commute_time_less_15 = models.IntegerField(
        verbose_name="N° of people that commute less than 15 minutes", null=True
    )
    work_commute_time_15_29 = models.IntegerField(
        verbose_name="N° of people that commute between 15 and 30 minutes", null=True
    )
    work_commute_time_30_44 = models.IntegerField(
        verbose_name="N° of people that commute between 30 and 45 minutes", null=True
    )
    work_commute_time_45_59 = models.IntegerField(
        verbose_name="N° of people that commute between 45 and 60 minutes", null=True
    )
    work_commute_time_60_89 = models.IntegerField(
        verbose_name="N° of people that commute between 60 and 90 minutes", null=True
    )
    work_commute_time_over_90 = models.IntegerField(
        verbose_name="N° of people that commute more than 90", null=True
    )
    population = models.IntegerField(null=True)

    # geographic_delimitation = models.PolygonField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["block_group", "census_tract", "county", "state"],
                name="demographic_uniqueness",
            )
        ]


#################################
######## TRANSIT MODELS #########
#################################


class TransitModes(models.IntegerChoices):
    LIGHT_RAIL = 0, "Tram, Streetcar, Light rail."
    SUBWAY = 1, "Subway, Metro"
    RAIL = 2, "Rail"
    BUS = 3, "Bus"
    FERRY = 4, "Ferry"
    CABLE_TRAM = 5, "Cable car"
    AERIAL_LIFT = 6, " Aerial lift, suspended cable car"
    FUNICULAR = 7, "Funicular"
    TROLLEYBUS = 11, "Trolleybus"
    MONORAIL = 12, "Monorail"


class TransitRoute(models.Model):
    """
    Class that represent subway lines and bus routes
    """

    city = models.CharField(max_length=30, choices=CITIES_CHOICES)
    route_id = models.CharField(max_length=64)
    route_name = models.CharField(max_length=64)
    color = models.CharField(max_length=30, null=True)
    geo_representation = models.MultiLineStringField()
    mode = models.IntegerField(
        verbose_name="Mode of transportation", choices=TransitModes.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["city", "route_id"], name="city route id")
        ]


class TransitStation(models.Model):
    """
    Class that represents bus stops and station complex
    (i.e. CTA - Roosevelt)
    """

    city = models.CharField(max_length=30, choices=CITIES_CHOICES)
    station_id = models.CharField(max_length=64)
    station_name = models.CharField(max_length=64)
    location = models.PointField(null=True)
    mode = models.IntegerField(
        verbose_name="Mode of transportation", choices=TransitModes.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["city", "station_id"], name="city station")
        ]


class StationRouteRelation(models.Model):
    """
    Class that represent relationship between Bus Stops/Subway Stations
    and the routes it serve.
    (i.e. row 1: CTA Roosevelt - Green Line
     row 2: CTA Roosevelt - Red Line)
    """

    station = models.ForeignKey(TransitStation, on_delete=models.PROTECT)
    route = models.ForeignKey(TransitRoute, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["station", "route"], name="station_route")
        ]


class RidershipRoute(models.Model):
    """
    Class that represent ridership at the route level
    """

    route = models.ForeignKey(TransitRoute, on_delete=models.PROTECT)
    date = models.DateField()
    ridership = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["route_id", "date"], name="route_ridership")
        ]


class RidershipStation(models.Model):
    """
    Class that represent ridership at the station level
    """

    station = models.ForeignKey(TransitStation, on_delete=models.PROTECT)
    date = models.DateField()
    ridership = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["station_id", "date"], name="station_ridership"
            )
        ]


class BikeStation(models.Model):
    """
    Class that represent bike sharing docking stations
    """

    city = models.CharField(max_length=30, choices=CITIES_CHOICES)
    station_id = models.CharField(max_length=64)
    station_name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=30, null=True)
    location = models.PointField()
    n_docks = models.IntegerField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["city", "station_id"], name="city_station_bike"
            )
        ]


class BikeRidership(models.Model):
    """
    Class that represent bike sharing ridership
    """

    station = models.ForeignKey(BikeStation, on_delete=models.PROTECT)
    date = models.DateField()
    n_started = models.IntegerField()
    n_ended = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["station_id", "date"], name="bike_ridership"
            )
        ]


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
