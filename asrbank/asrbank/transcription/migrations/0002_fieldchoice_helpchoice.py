# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-29 12:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=50)),
                ('english_name', models.CharField(max_length=100)),
                ('dutch_name', models.CharField(max_length=100)),
                ('machine_value', models.IntegerField(help_text='The actual numeric value stored in the database. Created automatically.')),
            ],
            options={
                'ordering': ['field', 'machine_value'],
            },
        ),
        migrations.CreateModel(
            name='HelpChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=200)),
                ('searchable', models.BooleanField(default=False)),
                ('display_name', models.CharField(max_length=50)),
                ('help_url', models.URLField(default='')),
            ],
        ),
    ]
