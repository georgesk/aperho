# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-28 14:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0022_auto_20170828_1059'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ouverture',
            unique_together=set([('nom_session', 'barrette')]),
        ),
    ]