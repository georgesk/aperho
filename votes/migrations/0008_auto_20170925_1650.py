# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-25 14:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0007_auto_20170911_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='enseignant',
            name='indirects',
            field=models.ManyToManyField(related_name='i', to='votes.Barrette'),
        ),
        migrations.AlterField(
            model_name='enseignant',
            name='barrettes',
            field=models.ManyToManyField(related_name='b', to='votes.Barrette'),
        ),
    ]