# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-23 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0002_etudiant_classe'),
    ]

    operations = [
        migrations.AddField(
            model_name='enseignant',
            name='prenom',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='enseignant',
            name='uid',
            field=models.IntegerField(default=-1, unique=True),
            preserve_default=False,
        ),
    ]
