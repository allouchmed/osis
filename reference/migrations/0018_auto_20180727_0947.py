# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-07-27 07:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0017_language_changed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='reference',
        ),
        migrations.AddField(
            model_name='domain',
            name='code',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
