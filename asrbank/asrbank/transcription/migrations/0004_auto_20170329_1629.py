# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 14:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0003_auto_20170329_1410'),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='0', help_text='Sorry, no help available for annotation.type', max_length=5, verbose_name='Kind of annotation')),
                ('mode', models.CharField(blank=True, help_text='Sorry, no help available for annotation.mode', max_length=5, verbose_name='Annotation mode')),
                ('format', models.CharField(blank=True, help_text='Sorry, no help available for annotation.format', max_length=5, verbose_name='Annotation format')),
            ],
        ),
        migrations.CreateModel(
            name='Anonymisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='0', help_text='Sorry, no help available for anonymisation', max_length=5, verbose_name='Anonymisation level of the transcription')),
            ],
            options={
                'verbose_name_plural': 'Anonymisation levels',
            },
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='0', help_text='Sorry, no help available for interview.availability', max_length=5, verbose_name='Availability')),
            ],
            options={
                'verbose_name_plural': 'Availability descriptions',
            },
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='0', help_text='Sorry, no help available for interview.format', max_length=5, verbose_name='Format of audio/video file')),
            ],
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='0', help_text='Sorry, no help available for interview.genre', max_length=5, verbose_name='Genre of this transcription')),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='0', help_text='Sorry, no help available for interview.language', max_length=5, verbose_name='Language in collection')),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='Sorry, no help available for participant.code', max_length=255, verbose_name='Code for this person')),
                ('name', models.CharField(help_text='Sorry, no help available for participant.name', max_length=255, verbose_name='Name of the person')),
                ('gender', models.CharField(default='0', help_text='Sorry, no help available for participant.gender', max_length=5, verbose_name='Gender of the person')),
                ('age', models.CharField(help_text='Sorry, no help available for participant.age', max_length=255, verbose_name='Age of the person')),
            ],
        ),
        migrations.CreateModel(
            name='SpatialCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(default='0', help_text='Sorry, no help available for coverage.spatial.country', max_length=5, verbose_name='Country included in this spatial coverage')),
                ('place', models.CharField(blank=True, help_text='Sorry, no help available for coverage.spatial.city', max_length=80, verbose_name='Place (city) for this spatial coverage')),
            ],
            options={
                'verbose_name_plural': 'Spatial coverages',
            },
        ),
        migrations.CreateModel(
            name='TemporalCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startYear', models.CharField(default='2017', max_length=20, verbose_name='First year covered by the transcription')),
                ('endYear', models.CharField(default='2017', max_length=20, verbose_name='Last year covered by the transcription')),
            ],
            options={
                'verbose_name_plural': 'Spatial coverages',
            },
        ),
        migrations.AddField(
            model_name='descriptor',
            name='copyright',
            field=models.TextField(blank=True, help_text='Sorry, no help available for interview.copyright', verbose_name='Copyright for this transcription'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='interviewDate',
            field=models.DateField(blank=True, default=datetime.datetime.today, help_text='Sorry, no help available for interview.date', verbose_name='Date of the interview'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='interviewId',
            field=models.CharField(default='-', help_text='Sorry, no help available for interview.id', max_length=255, verbose_name='Interview ID'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='interviewLength',
            field=models.TimeField(blank=True, default='00:00:00', help_text='Sorry, no help available for interview.length', verbose_name='Length in time of the interview'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='modality',
            field=models.CharField(default='0', help_text='Sorry, no help available for interview.modality', max_length=5, verbose_name='Transcription modality'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='owner',
            field=models.CharField(default='-', max_length=255, verbose_name='Unique short descriptor identifier (10 characters max)'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='projectTitle',
            field=models.CharField(default='-', help_text='Sorry, no help available for project.title', max_length=255, verbose_name='Project title'),
        ),
        migrations.AddField(
            model_name='descriptor',
            name='topicList',
            field=models.TextField(blank=True, help_text='Sorry, no help available for interview.topiclist', verbose_name='List of topics for this transcription'),
        ),
        migrations.AlterField(
            model_name='descriptor',
            name='identifier',
            field=models.CharField(default='-', max_length=10, verbose_name='Unique short descriptor identifier (10 characters max)'),
        ),
        migrations.CreateModel(
            name='Interviewee',
            fields=[
                ('participant_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='transcription.Participant')),
                ('descriptor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='interviewees', to='transcription.Descriptor')),
            ],
            options={
                'verbose_name_plural': 'Persons that were interviewed',
            },
            bases=('transcription.participant',),
        ),
        migrations.CreateModel(
            name='Interviewer',
            fields=[
                ('participant_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='transcription.Participant')),
                ('descriptor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='interviewers', to='transcription.Descriptor')),
            ],
            options={
                'verbose_name_plural': 'Interviewers',
            },
            bases=('transcription.participant',),
        ),
        migrations.AddField(
            model_name='temporalcoverage',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='temporalcoverages', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='spatialcoverage',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='spatialcoverages', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='language',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='genre',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='genres', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='fileformats', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='availability',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='anonymisation',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='anonymisations', to='transcription.Descriptor'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='descriptor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='transcription.Descriptor'),
        ),
    ]
