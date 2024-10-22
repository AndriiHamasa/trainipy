# Generated by Django 5.1.2 on 2024-10-13 09:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("station", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="latitude",
            field=models.FloatField(
                validators=[
                    django.core.validators.MinValueValidator(-90),
                    django.core.validators.MaxValueValidator(90),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="station",
            name="longitude",
            field=models.FloatField(
                validators=[
                    django.core.validators.MinValueValidator(-180),
                    django.core.validators.MaxValueValidator(180),
                ]
            ),
        ),
    ]
