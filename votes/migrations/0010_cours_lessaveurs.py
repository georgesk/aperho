# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-21 11:17
from __future__ import unicode_literals

from django.db import migrations
import votes.saveurField


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0009_auto_20170926_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='cours',
            name='lessaveurs',
            field=votes.saveurField.SaveurDictField(blank=True, saveurDict=votes.saveurField.SaveurDict(0, {})),
        ),
    ]
