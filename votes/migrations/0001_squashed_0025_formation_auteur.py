# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-03 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('votes', '0001_initial'), ('votes', '0002_etudiant_classe'), ('votes', '0003_auto_20160923_1418'), ('votes', '0004_auto_20160925_0924'), ('votes', '0005_formation_designe'), ('votes', '0006_auto_20160925_1410'), ('votes', '0007_auto_20160925_1440'), ('votes', '0008_etudiant_uid'), ('votes', '0009_auto_20161007_1632'), ('votes', '0010_barrette'), ('votes', '0011_auto_20161130_1739'), ('votes', '0012_orientation'), ('votes', '0013_auto_20161204_1645'), ('votes', '0014_inscriptionorientation'), ('votes', '0015_coursorientation_prof'), ('votes', '0016_barrette_classesjson'), ('votes', '0017_auto_20170819_1405'), ('votes', '0018_auto_20170819_2321'), ('votes', '0019_auto_20170820_2142'), ('votes', '0020_enseignant_username'), ('votes', '0021_auto_20170828_1056'), ('votes', '0022_auto_20170828_1059'), ('votes', '0023_auto_20170828_1643'), ('votes', '0024_horaire_barrette'), ('votes', '0025_formation_auteur')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Enseignant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('salle', models.CharField(max_length=50)),
                ('prenom', models.CharField(default='', max_length=50)),
                ('uid', models.IntegerField(default=-1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.IntegerField(unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=80)),
                ('contenu', models.TextField()),
                ('duree', models.IntegerField(default=1)),
                ('public_designe', models.BooleanField(default=False, verbose_name='Public désigné')),
            ],
        ),
        migrations.CreateModel(
            name='Horaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heure', models.TimeField()),
                ('jour', models.IntegerField(choices=[(1, 'lundi'), (2, 'mardi'), (3, 'mercredi'), (4, 'jeudi'), (5, 'vendredi'), (6, 'samedi')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Cours')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Etudiant')),
            ],
        ),
        migrations.AddField(
            model_name='cours',
            name='enseignant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Enseignant'),
        ),
        migrations.AddField(
            model_name='cours',
            name='formation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Formation'),
        ),
        migrations.AddField(
            model_name='cours',
            name='horaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Horaire'),
        ),
        migrations.AddField(
            model_name='etudiant',
            name='classe',
            field=models.CharField(default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='cours',
            options={'verbose_name_plural': 'cours'},
        ),
        migrations.AddField(
            model_name='cours',
            name='capacite',
            field=models.IntegerField(default=18),
        ),
        migrations.RenameField(
            model_name='etudiant',
            old_name='uid',
            new_name='uidNumber',
        ),
        migrations.AddField(
            model_name='etudiant',
            name='uid',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Ouverture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debut', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('nom_session', models.CharField(default='Toussaint', max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='cours',
            name='ouverture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Ouverture'),
        ),
        migrations.CreateModel(
            name='Barrette',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True)),
                ('classesJSON', models.CharField(default="'[]'", max_length=500, verbose_name='classes')),
            ],
        ),
        migrations.AddField(
            model_name='cours',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
        ),
        migrations.AddField(
            model_name='enseignant',
            name='barrettes',
            field=models.ManyToManyField(to='votes.Barrette'),
        ),
        migrations.AddField(
            model_name='etudiant',
            name='barrette',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
        ),
        migrations.CreateModel(
            name='Orientation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choix', models.IntegerField(choices=[(1, 'S, ES, L (scientifique, économique & social, littéraire)'), (2, 'STMG (sciences et techniques de management & gestion)')], default=1)),
                ('etudiant', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Etudiant')),
                ('ouverture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Ouverture')),
            ],
        ),
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
                'verbose_name': "Séance d'orientation",
                'verbose_name_plural': "Séances d'orientation",
            },
        ),
        migrations.CreateModel(
            name='InscriptionOrientation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cours', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.CoursOrientation')),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votes.Etudiant')),
            ],
        ),
        migrations.AddField(
            model_name='coursorientation',
            name='prof',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Enseignant'),
        ),
        migrations.AddField(
            model_name='coursorientation',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formation',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ouverture',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='enseignant',
            name='uid',
            field=models.IntegerField(),
        ),
        migrations.AddField(
            model_name='enseignant',
            name='username',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='enseignant',
            unique_together=set([('uid', 'salle')]),
        ),
        migrations.AlterUniqueTogether(
            name='ouverture',
            unique_together=set([('nom_session', 'barrette')]),
        ),
        migrations.AddField(
            model_name='horaire',
            name='barrette',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='votes.Barrette'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formation',
            name='auteur',
            field=models.ForeignKey(blank=True, help_text='le dernier prof à avoir modifié le titre ou le contenu', null=True, on_delete=django.db.models.deletion.CASCADE, to='votes.Enseignant'),
        ),
    ]