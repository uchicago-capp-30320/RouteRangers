# Generated by Django 5.0.4 on 2024-05-17 17:19

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "route_rangers_api",
            "0007_remove_demographics_demographic_uniqueness_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="survey",
            name="id",
        ),
        migrations.RemoveField(
            model_name="survey",
            name="questionnaire",
        ),
        migrations.RemoveField(
            model_name="surveyanswer",
            name="answers",
        ),
        migrations.RemoveField(
            model_name="surveyanswer",
            name="id",
        ),
        migrations.RemoveField(
            model_name="surveyanswer",
            name="survey",
        ),
        migrations.AddField(
            model_name="plannedroute",
            name="end_point",
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
        migrations.AddField(
            model_name="plannedroute",
            name="starting_point",
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="car_owner",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="frequent_transit",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="modes_of_transit",
            field=models.IntegerField(
                choices=[
                    (1, "Bus"),
                    (2, "Train"),
                    (3, "Car"),
                    (4, "Bike"),
                    (5, "Walking"),
                    (6, "Rideshare"),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="satisfied",
            field=models.IntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")], null=True
            ),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="switch_to_transit",
            field=models.IntegerField(
                choices=[
                    (1, "There are stops near you"),
                    (2, "There are many scheduled departures"),
                    (3, "It doesn't take significantly longer than driving"),
                    (4, "There are enough seats for all riders"),
                    (5, "It feels safe at the station and onboard"),
                    (6, "It will save me money"),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="transit_improvement_safety",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="transit_improvement_schedule",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="transit_improvement_service",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="transit_improvement_transfers",
            field=models.IntegerField(choices=[(1, "Yes"), (2, "No")], null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="trip_frequency",
            field=models.IntegerField(
                choices=[
                    (1, "Everyday"),
                    (2, "Weekdays"),
                    (3, "Weekends"),
                    (4, "A few times per week"),
                    (5, "A few times per month"),
                    (6, "A few times per year"),
                ],
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="trip_time",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="surveyanswer",
            name="trip_tod",
            field=models.IntegerField(
                choices=[(1, "Peak commute hours"), (2, "Daytime"), (3, "Nighttime")],
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="survey",
            name="name",
            field=models.CharField(max_length=64, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="surveyanswer",
            name="city",
            field=models.CharField(
                choices=[("CHI", "Chicago"), ("NYC", "New York"), ("PDX", "Portland")],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="surveyanswer",
            name="user_id",
            field=models.CharField(max_length=128, primary_key=True, serialize=False),
        ),
    ]
