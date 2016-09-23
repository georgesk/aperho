from django.db import models

class Enseignant(models.Model):
    uid    = models.IntegerField(unique=True)
    nom   = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    salle = models.CharField(max_length=50)

    def __str__(self):
        return "{} ({})".format(self.nom, self.salle)
    
class Formation(models.Model):
    titre   = models.CharField(max_length=80)
    contenu = models.TextField()
    duree   = models.IntegerField(default=1)

    def __str__(self):
        result="{} heure(s) : {} --- {}".format(self.duree, self.titre, self.contenu)
        if len(result) > 40:
            result=result[:37]+" ..."
        return result
    
class Horaire(models.Model):
    heure = models.TimeField()

    def __str__(self):
        return str(self.heure)

class Etudiant(models.Model):
    uid    = models.IntegerField(unique=True)
    nom    = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    classe = models.CharField(max_length=10)

    def __str__(self):
        return "{} {} {}".format(self.nom, self.prenom, self.uid)
    
class Cours(models.Model):
    class Meta:
        verbose_name_plural = "cours"
    enseignant = models.ForeignKey('Enseignant')
    horaire    = models.ForeignKey('Horaire')
    formation  = models.ForeignKey('Formation')

    def __str__(self):
        return "{} {} {}".format(self.horaire, self.enseignant, self.formation)

class Inscription(models.Model):
    etudiant   = models.ForeignKey('Etudiant')
    cours      = models.ForeignKey('Cours')

    def __str__(self):
        return "{} {}".format(self.etudiant, self.cours)
