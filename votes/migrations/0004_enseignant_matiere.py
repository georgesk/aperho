# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-05 21:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0003_auto_20170903_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='enseignant',
            name='matiere',
            field=models.CharField(default='??', max_length=50),
            preserve_default=False,
        ),
    ]
