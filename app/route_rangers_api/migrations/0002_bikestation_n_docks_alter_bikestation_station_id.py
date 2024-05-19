# Generated by Django 5.0.4 on 2024-05-06 22:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("route_rangers_api", "0001_reset_models_pre_ingestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="bikestation",
            name="n_docks",
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name="bikestation",
            name="station_id",
            field=models.CharField(max_length=50),
        ),
    ]
