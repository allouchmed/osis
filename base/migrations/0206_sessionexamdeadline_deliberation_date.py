# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-12-18 15:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0205_auto_20171218_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionexamdeadline',
            name='deliberation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
