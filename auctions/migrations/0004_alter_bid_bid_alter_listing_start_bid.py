# Generated by Django 4.1.7 on 2023-05-01 17:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_bid_bid_alter_listing_start_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bid',
            field=models.DecimalField(decimal_places=2, max_digits=40, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='listing',
            name='start_bid',
            field=models.DecimalField(decimal_places=2, max_digits=40, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
