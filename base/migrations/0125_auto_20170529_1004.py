# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-05-29 08:04
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0016_auto_20170410_1318'),
        ('base', '0124_entity_models_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='learningcontaineryear',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Language'),
        ),
        migrations.AddField(
            model_name='learningcontaineryear',
            name='title_english',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='learningunityear',
            name='title_english',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]