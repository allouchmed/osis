# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-15 17:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0012_migrate_fk_to_enum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='continent',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='uuid',
        ),
    ]
