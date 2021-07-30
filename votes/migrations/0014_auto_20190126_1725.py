# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-26 16:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0013_preinscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='preinscription',
            name='barrette',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
        ),
        migrations.AddField(
            model_name='preinscription',
            name='ouverture',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Ouverture'),
        ),
    ]