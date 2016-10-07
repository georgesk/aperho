from django.db import models
from aperho.settings import connection
from django.utils import timezone

class Ouverture(models.Model):
    debut = models.DateTimeField()
    fin   = models.DateTimeField()

    def __str__(self):
        return "{} ↦ {}".format(self.debut, self.fin)

    def estActive(self):
        """
        décide si un objet "ouverture" est actif
        @return vrai ou faux
        """
        now = timezone.now()
        return self.debut <= now <= self.fin
    
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
    public_designe = models.BooleanField(default=False, verbose_name="Public désigné")

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
    uidNumber = models.IntegerField(unique=True)
    uid       = models.CharField(max_length=50)
    nom       = models.CharField(max_length=50)
    prenom    = models.CharField(max_length=50)
    classe    = models.CharField(max_length=10)

    def __str__(self):
        return "{nom} {prenom} {classe} {uid}".format(**self.__dict__)
    
class Cours(models.Model):
    class Meta:
        verbose_name_plural = "cours"
    enseignant = models.ForeignKey('Enseignant')
    horaire    = models.ForeignKey('Horaire')
    formation  = models.ForeignKey('Formation')
    capacite   = models.IntegerField(default=18)
    ouverture  = models.ForeignKey('Ouverture', null=True, blank=True)

    def __str__(self):
        return "{} {} {} (max={})".format(self.horaire, self.enseignant, self.formation, self.capacite)

    def estOuvert(self):
        """
        Dit si l'inscription au cours est ouverte
        @return vrai ou faux
        """
        return self.ouverture.estActive()

class Inscription(models.Model):
    etudiant   = models.ForeignKey('Etudiant')
    cours      = models.ForeignKey('Cours')

    def __str__(self):
        return "{} {}".format(self.etudiant, self.cours)

def estProfesseur(user):
    """
    Vérifie si un utilisateur (au sens ldap) est un professeur
    de la table Enseignant
    @param user un objet django de type User
    @return un statut: "non", "prof" ou "profAP", selon que c'est un
    non-enseignant, un enseignant extérieur à l'AP, ou un prof de la table
    Enseignant.
    """
    result="non"
    nom=user.last_name
    prenom=user.first_name
    login=user.username
    #### récupération du numéro du groupe des profs
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre  = '(cn=profs)'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["gidNumber" ]
        )
    gid=connection.response[0]['attributes']["gidNumber" ][0]
    #### d'abord, user est-il prof ?
    base_dn = 'ou=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(gidNumber={0})(uid={1}))'.format(gid, login)
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName" ]
        )
    if len(connection.response) > 0: # on a affaire à un prof.
        if len(Enseignant.objects.filter(nom=nom, prenom=prenom))==0:
            result="prof"
        else:
            result="profAP"
    return result

