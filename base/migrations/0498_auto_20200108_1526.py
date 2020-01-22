# Generated by Django 2.2.5 on 2020-01-08 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0497_auto_20200108_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academiccalendar',
            name='reference',
            field=models.CharField(
                choices=[('DELIBERATION', 'Deliberation'), ('DISSERTATION_SUBMISSION', 'Dissertation submission'),
                         ('EXAM_ENROLLMENTS', 'Exam enrollments'), ('SCORES_EXAM_DIFFUSION', 'Scores exam diffusion'),
                         ('SCORES_EXAM_SUBMISSION', 'Scores exam submission'),
                         ('TEACHING_CHARGE_APPLICATION', 'Teaching charge application'),
                         ('COURSE_ENROLLMENT', 'Course enrollment'),
                         ('SUMMARY_COURSE_SUBMISSION', 'Summary course submission'),
                         ('EDUCATION_GROUP_EDITION', 'Education group edition'),
                         ('LEARNING_UNIT_EDITION_CENTRAL_MANAGERS', 'Learning unit edition by central managers'),
                         ('LEARNING_UNIT_EDITION_FACULTY_MANAGERS', 'Learning unit edition by faculty managers'),
                         ('CREATION_OR_END_DATE_PROPOSAL_CENTRAL_MANAGERS', 'Creation or end date proposal by central managers'),
                         ('CREATION_OR_END_DATE_PROPOSAL_FACULTY_MANAGERS', 'Creation or end date proposal by faculty managers'),
                         ('MODIFICATION_OR_TRANSFORMATION_PROPOSAL_CENTRAL_MANAGERS', 'Modification or transformation proposal by central managers'),
                         ('MODIFICATION_OR_TRANSFORMATION_PROPOSAL_FACULTY_MANAGERS', 'Modification or transformation proposal by faculty managers'),
                         ('TESTING', 'Testing'),
                         ('RELEASE', 'Release')], max_length=70),
        ),
    ]
