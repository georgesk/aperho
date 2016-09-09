from django.db import models

class Enseignant(models.Model):
    nom   = models.CharField(max_length=50)
    salle = models.CharField(max_length=50)
    
class Formation(models.Model):
    titre   = models.CharField(max_length=80)
    contenu = models.TextField()
    duree   = models.IntegerField(default=1)

class Horaire(models.Model):
    heure = models.TimeField()

class Cours(models.Model):
    enseignant = models.ForeignKey('Enseignant')
    horaire    = models.ForeignKey('Horaire')
    formation  = models.ForeignKey('Formation')

class Inscription(models.Model):
    uid   = models.IntegerField()
    cours = models.ForeignKey('Cours')
