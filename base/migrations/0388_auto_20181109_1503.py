# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-09 15:03
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0387_auto_20181112_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offeryearcalendar',
            name='offer_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
    ]
