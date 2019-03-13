# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-02-20 15:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0430_auto_20190211_1043'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='educationgroupyear',
            options={'ordering': ('academic_year',), 'verbose_name': 'Education group year'},
        ),
        migrations.AlterUniqueTogether(
            name='educationgroupyear',
            unique_together=set([('education_group', 'academic_year'), ('partial_acronym', 'academic_year')]),
        ),
    ]