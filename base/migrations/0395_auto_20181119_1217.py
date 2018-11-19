# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-19 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0394_auto_20181119_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prerequisite',
            name='prerequisite',
            field=models.CharField(blank=True, default='', max_length=240),
        ),
        migrations.AlterUniqueTogether(
            name='prerequisiteitem',
            unique_together=set([('prerequisite', 'group_number', 'position')]),
        ),
    ]
