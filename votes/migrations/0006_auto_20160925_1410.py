# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-25 14:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0005_formation_designe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formation',
            old_name='designe',
            new_name='public_designe',
        ),
    ]