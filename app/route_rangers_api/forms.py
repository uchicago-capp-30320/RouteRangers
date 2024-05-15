# ask JP why we're importing like this instead of:
# from django import forms
from django.contrib.gis import forms


MODES_OF_TRANIST = {
    "bus": "Bus",
    "train": "Train",
    "car": "Car",
    "bike": "Bike",
    "walking": "Walking",
    "rideshare": "Rideshare",
}

TRIP_FREQ = {
    "daily": "Everyday",
    "weekdays": "Weekdays",
    "weekends": "Weekends",
    "few_week": "A few times per week",
    "few_month": "A few times per month",
    "few_year": "A few times per year",
}

TIME_OF_DAY = {"peak": "Peak commute hours", "day": "Daytime", "night": "Nighttime"}

SATISFIED = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}

TRANSIT_IMPROVEMENT = {
    "frequent_service": "More frequent service",
    "accurate_schedule": "More accurate schedule times",
    "fewer_transfers": "Fewer transfers or a more direct route",
    "safety": "It feels safe at the station and onboard",
}

SWITCH_TO_TRANSIT = {
    "stops": "There are stops near you",
    "schedule": "There are many scheduled departures",
    "length": "It doesn't take significantly longer than driving",
    "seats": "There are enough seats for all riders",
    "safe": "It feels safe at the station and onboard",
    "cost": "It will save me money",
}

QUESTIONS = {
    "p1": {
        "frequent_transit": "Do you use public transit regularly?",
        "car_owner": "Do you own a car or other motorized vehicle?",
    },
    "p2": {
        "trip_freq": "When do you usually make this trip?",
        "trip_tod": "What time of day you usually make this trip?",
        "trip_time": "How long does this trip currently take in minutes?",
        "modes_of_transit": "What mode of transit do you usually use to make \
            this trip? Select all that apply",
    },
    "p3": {
        "satisfied": "How satisfied are you with the public transit options \
            for this route?",
        "transit_improvement": "How could this public transit route be \
              improved?",
    },
    "p4": {
        "switch": """Assuming that a new transit route is built connecting these \
            stops, what factor would most motivate you to choose to take \
                public transit?"""
    },
    "p5": {"feedback", "Any other feedback or comments:"},
}

BOOL_CHOICES = ((True, "Yes"), (False, "No"))


class RiderSurvey1(forms.Form):
    # Page 1: Intro
    frequent_transit = forms.ChoiceField(
        label=QUESTIONS["p1"]["frequent_transit"],
        choices=BOOL_CHOICES,
        widget=forms.RadioSelect,
    )
    car_owner = forms.ChoiceField(
        label=QUESTIONS["p1"]["car_owner"],
        choices=BOOL_CHOICES,
        widget=forms.RadioSelect,
    )


class RiderSurvey2(forms.Form):
    # Page 2: Rider Trips
    trip_frequency = forms.MultipleChoiceField(
        label=QUESTIONS["p2"]["trip_freq"], choices=TRIP_FREQ, widget=forms.RadioSelect
    )

    trip_tod = forms.MultipleChoiceField(
        label=QUESTIONS["p2"]["trip_tod"], choices=TIME_OF_DAY, widget=forms.RadioSelect
    )

    trip_time = forms.IntegerField(
        label=QUESTIONS["p2"]["trip_time"], min_value=0, widget=forms.NumberInput
    )
    modes_of_transit = forms.MultipleChoiceField(
        label=QUESTIONS["p2"]["modes_of_transit"],
        choices=MODES_OF_TRANIST,
        widget=forms.CheckboxSelectMultiple,
    )


class RiderSurvey3(forms.Form):
    # Page 3: Transit Questions
    satisfied = forms.ChoiceField(
        label=QUESTIONS["p3"]["satisfied"],
        choices=SATISFIED,
        widget=forms.RadioSelect,
    )
    transit_improvement = forms.MultipleChoiceField(
        label=QUESTIONS["p3"]["transit_improvement"],
        choices=TRANSIT_IMPROVEMENT,
        widget=forms.RadioSelect,
    )


class RiderSurvey4(forms.Form):
    # Page 4: Car Questions
    switch_to_transit = forms.MultipleChoiceField(
        label=QUESTIONS["p4"]["switch"],
        choices=SWITCH_TO_TRANSIT,
        widget=forms.RadioSelect(attrs={"class": "small-text"}),
    )
