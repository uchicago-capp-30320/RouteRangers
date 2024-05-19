# Generated by Django 5.0.4 on 2024-05-07 23:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("route_rangers_api", "0004_alter_bikestation_station_id_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="demographics",
            old_name="census_block",
            new_name="block_group",
        ),
        migrations.RemoveField(
            model_name="demographics",
            name="disability_status",
        ),
        migrations.RemoveField(
            model_name="demographics",
            name="vehicles_available",
        ),
        migrations.RemoveField(
            model_name="demographics",
            name="work_commute_time",
        ),
        migrations.AddField(
            model_name="demographics",
            name="census_tract",
            field=models.CharField(default="None", max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_15_29",
            field=models.IntegerField(
                null=True,
                verbose_name="N° of people that commute between 15 and 30 minutes",
            ),
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_30_44",
            field=models.IntegerField(
                null=True,
                verbose_name="N° of people that commute between 30 and 45 minutes",
            ),
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_45_59",
            field=models.IntegerField(
                null=True,
                verbose_name="N° of people that commute between 45 and 60 minutes",
            ),
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_60_89",
            field=models.IntegerField(
                null=True,
                verbose_name="N° of people that commute between 60 and 90 minutes",
            ),
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_less_15",
            field=models.IntegerField(
                null=True, verbose_name="N° of people that commute less than 15 minutes"
            ),
        ),
        migrations.AddField(
            model_name="demographics",
            name="work_commute_time_over_90",
            field=models.IntegerField(
                null=True, verbose_name="N° of people that commute more than 90"
            ),
        ),
        migrations.AlterField(
            model_name="demographics",
            name="median_income",
            field=models.IntegerField(
                null=True, verbose_name="Median household income"
            ),
        ),
        migrations.AlterField(
            model_name="demographics",
            name="transportation_to_work",
            field=models.IntegerField(
                null=True, verbose_name="Means of Transportation to Work Total"
            ),
        ),
        migrations.AddConstraint(
            model_name="demographics",
            constraint=models.UniqueConstraint(
                fields=("block_group", "census_tract", "county", "state"),
                name="demographic_uniqueness",
            ),
        ),
    ]
