# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-19 14:06
from __future__ import unicode_literals

import uuid

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0391_auto_20181116_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationgroup',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='educationgrouptype',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_draft',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_final',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='score_reencoded',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0, message='Les notes doivent être comprises entre 0 et 20'), django.core.validators.MaxValueValidator(20, message='Les notes doivent être comprises entre 0 et 20')]),
        ),
    ]
