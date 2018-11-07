# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-05 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0035_attributionchargenew_changed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributionnew',
            name='function',
            field=models.CharField(choices=[('COORDINATOR', 'COORDINATOR'), ('HOLDER', 'HOLDER'), ('CO_HOLDER', 'CO_HOLDER'), ('DEPUTY', 'DEPUTY'), ('DEPUTY_AUTHORITY', 'DEPUTY_AUTHORITY'), ('DEPUTY_SABBATICAL', 'DEPUTY_SABBATICAL'), ('DEPUTY_TEMPORARY', 'DEPUTY_TEMPORARY'), ('PROFESSOR', 'PROFESSOR'), ('INTERNSHIP_SUPERVISOR', 'INTERNSHIP_SUPERVISOR'), ('INTERNSHIP_CO_SUPERVISOR', 'INTERNSHIP_CO_SUPERVISOR')], db_index=True, max_length=35, verbose_name='function'),
        ),
        migrations.AlterField(
            model_name='attributionnew',
            name='start_year',
            field=models.IntegerField(blank=True, null=True, verbose_name='start'),
        ),
    ]
