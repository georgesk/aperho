# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-25 14:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0007_auto_20160925_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='etudiant',
            name='uid',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]
