# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-04 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0012_orientation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('salle', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CoursOrientation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debut', models.DateTimeField()),
                ('formation', models.IntegerField(choices=[(1, 'Orientation en premières S, ES et L'), (2, 'Orientation en premières STMG')], default=1)),
                ('cop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Cop')),
            ],
            options={
                'verbose_name_plural': "Séances d'orientation",
                'verbose_name': "Séance d'orientation",
            },
        ),
        migrations.AlterField(
            model_name='orientation',
            name='etudiant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Etudiant'),
        ),
    ]
