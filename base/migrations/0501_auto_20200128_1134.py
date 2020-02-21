# Generated by Django 2.2.5 on 2020-01-28 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0500_create_events_creation_and_end_date_proposition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='learningachievement',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='partial_title',
            field=models.CharField(blank=True, default='', max_length=240, verbose_name='Partial title in French'),
        ),
        migrations.AddField(
            model_name='educationgroupyear',
            name='partial_title_english',
            field=models.CharField(blank=True, default='', max_length=240, verbose_name='Partial title in English'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='title',
            field=models.CharField(max_length=240, verbose_name='Title in French'),
        ),
        migrations.AlterField(
            model_name='educationgroupyear',
            name='title_english',
            field=models.CharField(blank=True, default='', max_length=240, verbose_name='Title in English'),
        ),
    ]