# Generated by Django 2.2.5 on 2019-12-24 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education_group', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='groupyear',
            name='uuid',
        ),
        migrations.AddField(
            model_name='groupyear',
            name='partial_acronym',
            field=models.CharField(db_index=True, max_length=15, null=True, verbose_name='Acronym/Short title'),
        ),
    ]
