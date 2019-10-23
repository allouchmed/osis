# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-21 09:39
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0009_auto_20160921_1139'),
        ('base', '0066_person_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('adhoc', models.BooleanField(default=True)),
                ('national', models.BooleanField(default=False)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Domain')),
                ('grade_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.GradeType')),
                ('offer_year', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
