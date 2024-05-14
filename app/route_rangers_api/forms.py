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

SATISFIED = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5}

TRANSIT_IMPROVEMENT = {
    "frequent_service": "More frequent service",
    "accurate_schedule": "More accurate schedule times",
    "fewer_transfers": "Fewer transfers or a more direct route",
    "safety": "Safety",
}

QUESTIONS = {
    "p1": {
        "frequent_transit": "Do you use public transit regularly?",
        "car_owner": "Do you own a car or other motorized vehicle?",
    },
    "p2": {
        "trip_frequency": "",
        "trip_time": "How long does this trip take currently in minutes?",
        "modes_of_transit": "What mode of transit do you usually use to make this trip? Select all that apply",
    },
    "p3": {
        "satisfied": "How satisfied are you with the public transit options for this route?",
        "transit_improvement": "How could this public transit route be improved?",
    },
    "p4": {
        "": """Assuming that a new transit route is built connecting these stops,
            what factor would most motivate you to choose to take public transit?"""
    },
    "p5": {"feedback", "Any other feedback or relevant information?"},
}

BOOL_CHOICES = ((True, "Yes"), (False, "No"))


class RiderSurvey(forms.Form):
    # Django example
    # your_name = forms.CharField(label="Your name", max_length=100)

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

    # Page 2: Rider Trips
    # start_point = forms.PointField()
    # end_point = forms.PointField()
    trip_frequency = forms.MultipleChoiceField(label=QUESTIONS["p2"]["trip_frequency"])
    trip_time = forms.IntegerField(
        label=QUESTIONS["p2"]["trip_time"], min_value=0, widget=forms.NumberInput
    )
    modes_of_transit = forms.MultipleChoiceField(
        label=QUESTIONS["p2"]["modes_of_transit"],
        widget=forms.CheckboxSelectMultiple,
        choices=MODES_OF_TRANIST,
    )

    # Page 3: Transit Questions
    satisfied = forms.ChoiceField(
        label=QUESTIONS["p3"]["satisfied"],
        widget=forms.CheckboxInput,
        choices=SATISFIED,
    )
    transit_improvement = forms.MultipleChoiceField(
        label=QUESTIONS["p3"]["transit_improvement"],
        widget=forms.CheckboxSelectMultiple,
    )

    # Page 4: Car Questions
    car_question = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    # # Page 5: Feedback
    # comment = forms.CharField(
    #     label=QUESTIONS["p5"]["feedback"], widget=forms.Textarea, max_length=300
    # )
