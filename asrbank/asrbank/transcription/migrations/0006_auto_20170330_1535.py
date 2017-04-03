# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-30 13:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0005_auto_20170330_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='descriptor',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]