# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-07-08 13:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0462_auto_20190626_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionexam',
            name='education_group_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.EducationGroupYear'),
        ),
    ]
