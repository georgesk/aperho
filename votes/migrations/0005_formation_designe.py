# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-25 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0004_auto_20160925_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='formation',
            name='designe',
            field=models.BooleanField(default=False),
        ),
    ]