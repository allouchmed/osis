# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-21 13:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0103_auto_20170419_1030'),
    ]

    operations = [
         migrations.RunSQL(
            """
            DROP VIEW IF EXISTS app_scores_encoding;
            """
        ),
    ]
