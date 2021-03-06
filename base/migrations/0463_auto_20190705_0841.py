# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-07-05 08:41
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import base.models.learning_unit_year


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0462_auto_20190626_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccalendar',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear'),
        ),
        migrations.AlterField(
            model_name='educationgrouplanguage',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reference.Language'),
        ),
        migrations.AlterField(
            model_name='educationgrouporganization',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Organization'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear', verbose_name='validity'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='administration_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='administration_entity', to='base.Entity', verbose_name='Administration entity'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='enrollment_campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='enrollment', to='base.Campus', verbose_name='Enrollment campus'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='main_domain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.Domain', verbose_name='main domain'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='main_teaching_campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='teaching', to='base.Campus', verbose_name='Learning location'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='management_entity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='management_entity', to='base.Entity', verbose_name='Management entity'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='primary_language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.Language', verbose_name='Primary language'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='publication_contact_entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Entity', verbose_name='Publication contact entity'),
        ),
        migrations.AlterField(
            model_name='entity',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.Country'),
        ),
        migrations.AlterField(
            model_name='entitymanager',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Entity'),
        ),
        migrations.AlterField(
            model_name='entitymanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='examenrollment',
            name='learning_unit_enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.LearningUnitEnrollment'),
        ),
        migrations.AlterField(
            model_name='examenrollmenthistory',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='externallearningunityear',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='externaloffer',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reference.Domain'),
        ),
        migrations.AlterField(
            model_name='externaloffer',
            name='grade_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.GradeType'),
        ),
        migrations.AlterField(
            model_name='externaloffer',
            name='offer_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.OfferYear'),
        ),
        migrations.AlterField(
            model_name='learningcontaineryear',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear'),
        ),
        migrations.AlterField(
            model_name='learningunitenrollment',
            name='offer_enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.OfferEnrollment'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='academic_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.AcademicYear', validators=[base.models.learning_unit_year.academic_year_validator], verbose_name='Academic year'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='campus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Campus', verbose_name='Learning location'),
        ),
        migrations.AlterField(
            model_name='learningunityear',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.Language', verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='mandatary',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='offerenrollment',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Student'),
        ),
        migrations.AlterField(
            model_name='person',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='personaddress',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reference.Country'),
        ),
        migrations.AlterField(
            model_name='personentity',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='programmanager',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person', verbose_name='person'),
        ),
        migrations.AlterField(
            model_name='proposallearningunit',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
        migrations.AlterField(
            model_name='student',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.Person'),
        ),
    ]
