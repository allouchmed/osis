# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-06-26 10:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0461_auto_20190617_1042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offertype',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='learningcomponentyear',
            name='planned_classes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]