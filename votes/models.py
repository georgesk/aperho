# -*- mode: python-mode; python-indent-offset: 4 -*-
from django.db import models
from aperho.settings import connection, LANGUAGE_CODE
from django.utils import timezone
import locale

class CoursOrientation(models.Model):
    """
    Définit une séance d'information par une conseillère d'orientation
    psychologue.
    """
    class Meta:
        verbose_name = "Séance d'orientation"
        verbose_name_plural = "Séances d'orientation"
    cop = models.ForeignKey('Cop')
    prof = models.ForeignKey('Enseignant', null=True, default=None)
    debut = models.DateTimeField()
    formation = models.IntegerField(choices=[
        (1,"Orientation en premières S, ES et L"),
        (2,"Orientation en premières STMG"),
        ], default=1)

    def __str__(self):
        return "{} {} {} avec {}".format(timezone.localtime(self.debut), self.cop, self.formation, self.prof)

class Cop(models.Model):
    """
    Définit une conseillère d'orientation psychologue
    """
    nom = models.CharField(max_length=50)
    salle = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.nom)

class InscriptionOrientation(models.Model):
    """
    Décrit l'affectation d'un étudiant à un cours d'orientation
    """
    etudiant = models.ForeignKey('Etudiant')
    cours    = models.ForeignKey('CoursOrientation')

    def __str__(self):
        return "{} {}".format(self.etudiant, self.cours)
    
class Orientation(models.Model):
    """
    Définit une ou plusieurs orientations associées à un étudiant,
pour un créneau d'ouverture de l'AP donné
    """
    choix = models.IntegerField(choices=[
        (1, "S, ES, L (scientifique, économique & social, littéraire)"),
        (2,"STMG (sciences et techniques de management & gestion)"),
    ], default=1)
    etudiant    = models.ForeignKey('Etudiant', null = True, default=None)
    ouverture   = models.ForeignKey('Ouverture')

    def __str__(self):
        return "{} {} {}".format(self.etudiant, self.choix, self.ouverture)

    def estOuvert(self):
        """
        Dit si l'inscription à l'orientation est ouverte
        @return vrai ou faux
        """
        return self.ouverture.estActive()

def rdvOrientation(inscription, ouverture=None):
    """
    Donne la liste des rendez-vous pour l'orientation d'un étudiant
    @param inscription une inscription d'étudiant
    @param ouverture une période d'ouverture des inscriptions. Valeur par
    défaut : None, ce qui provoque le choix de la plus récente ouverture
    @return une chaîne de caractères expliquant à l'élève la date et le lieu
    de son ou ses rendez-vous
    """
    if ouverture==None:
        ouverture=Ouverture.objects.last()
    if not ouverture:
        return ""
    ori=list(Orientation.objects.filter(
        etudiant=inscription.etudiant,
        ouverture=ouverture
    ))
    if not ori:
        return ""
    choices=Orientation._meta.get_field("choix").choices
    result=set()
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    for key, val in choices:
        ori=Orientation.objects.filter(
            etudiant=inscription.etudiant,
            ouverture=ouverture,
            choix=key).first()
        if ori:
            ## on recherche l'affectation si celle-ci existe
            ## dans la table InscriptionOrientation
            inscr=list(InscriptionOrientation.objects.filter(etudiant=inscription.etudiant))
            if len(inscr)>0:
                for i in inscr:
                    cop=str(i.cours.cop.nom)[:4]
                    salle=i.cours.prof.salle
                    prof=i.cours.prof.nom
                    t=timezone.localtime(i.cours.debut)
                    jour=t.strftime("%d/%m")
                    heure=t.strftime("%H:%M")
                    mentionCOP = "{j} {h} : {cop}/{prof} ({s})".format(
                        cop=cop, s=salle, j=jour, h=heure, prof=prof
                    )
                    if inscription.cours.horaire.heure.strftime("%H:%M")==heure or \
                      inscription.cours.formation.duree==2:
                        result.add(mentionCOP)                    
            else:
                cop="cop??"
                salle="A???"
                jour="??/??"
                heure="??:??"
                mentionCOP = "{j} {h} : {cop} ({s})".format(
                    cop=cop, s=salle, j=jour, h=heure
                )
                if inscription.cours.horaire.heure.strftime("%H:%M")==heure or \
                   inscription.cours.formation.duree==2:
                    result.add(mentionCOP)
    return ", ".join(list(result))
    
class Barrette(models.Model):
    """
    Définit un ensemble d'étudiants qui sont gérés ensemble
    et aux mêmes heures dans l'emploi du temps.
    """
    nom = models.CharField(max_length=50)

    def __str__(self):
        return "Barrette : {}".format(self.barrette)
    
class Ouverture(models.Model):
    """
    Ouverture des votes, pour une barrette d'AP. Les élèves ne pouront
    "voter" dans cette barrette qu'entre une date de début et une date
    de fin. Entre les deux, le vote ne leur sera pas proposé (mais
    pourrait éventuellement leur être montré)
    """
    debut = models.DateTimeField()
    fin   = models.DateTimeField()
    nom_session = models.CharField(max_length=50, default="Toussaint")
    
    def __str__(self):
        return "{} ↦ {}".format(self.debut, self.fin)

    def estActive(self):
        """
        décide si un objet "ouverture" est actif au moment précis
        de l'invocation de la méthode.
        @return vrai ou faux
        """
        now = timezone.now()
        return self.debut <= now <= self.fin
    
class Enseignant(models.Model):
    """
    Désigne un professeur ou un autre membre de l'équipe éducative.
    le champ "uid" correspond à l'identifiant de ce professeur dans 
    l'annuaire LDAP de l'établissement.
    Le champ "salle" correspond à une désignation plus ou moins
    précise du lieu où il donnera ses cours (ça peut être une salle
    ou alors un groupe de salles, voire tout un étage de bâtiment).
    """
    uid    = models.IntegerField(unique=True)
    nom   = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    salle = models.CharField(max_length=50)
    barrettes= models.ManyToManyField(Barrette)

    def __str__(self):
        return "{} ({})".format(self.nom, self.salle)
    
class Formation(models.Model):
    """
    Désigne une "granule" de formation, qui peut être réutilisée
    plus d'une fois si nécessaire. Elle n'est pas attachée à un
    enseignant /a priori/.
    """
    titre   = models.CharField(max_length=80)
    contenu = models.TextField()
    duree   = models.IntegerField(default=1)
    public_designe = models.BooleanField(default=False, verbose_name="Public désigné")

    def __str__(self):
        cours=Cours.objects.filter(formation=self)
        profs="/".join([c.enseignant.nom for c in cours])
        result="{} heure(s) : {} -- {} --- {}".format(self.duree, self.titre, profs, self.contenu)
        max=120
        if len(result) > max:
            result=result[:max-4]+" ..."
        return result
    
class Horaire(models.Model):
    """
    Désigne une heure du jour : 14:00 ou 15:00 par exemple.
    """
    heure = models.TimeField()
    jour  = models.IntegerField(choices=[
        (1, "lundi"),
        (2,"mardi"),
        (3, "mercredi"),
        (4, "jeudi"),
        (5, "vendredi"),
        (6, "samedi"),
    ], default=1)

    def __str__(self):
        return str(self.heure)

class Etudiant(models.Model):
    """
    Représente un étudiant qui peut "voter". Les champs "uidNumber" et
    "uid" identifient l'étudiant dans l'annuaire LDAP de 
    l'établissement.
    """
    uidNumber = models.IntegerField(unique=True)
    uid       = models.CharField(max_length=50)
    nom       = models.CharField(max_length=50)
    prenom    = models.CharField(max_length=50)
    classe    = models.CharField(max_length=10)
    barrette   = models.ForeignKey('Barrette', null=True, blank=True)

    def __str__(self):
        return "{nom} {prenom} {classe} {uid}".format(**self.__dict__)
    
class Cours(models.Model):
    """
    Représente un cours, c'est à dire décrit les caractéristiques
    complètes d'un cours d'AP : l'enseignant qui intervient, la granule
    de formation que l'enseignant dispensera, l'heure de début, la
    capacité (nombre maximal d'élèves qui peuvent voter pour ce cours),
    et les dates de début/fin d'ouverture des votes	pour s'y inscrire.
    """
    class Meta:
        verbose_name_plural = "cours"
    enseignant = models.ForeignKey('Enseignant')
    horaire    = models.ForeignKey('Horaire')
    formation  = models.ForeignKey('Formation')
    capacite   = models.IntegerField(default=18)
    ouverture  = models.ForeignKey('Ouverture')
    barrette   = models.ForeignKey('Barrette', null=True, blank=True)

    def __str__(self):
        return "{} {} {} (max={})".format(self.horaire, self.enseignant, self.formation, self.capacite)

    def estOuvert(self):
        """
        Dit si l'inscription au cours est ouverte
        @return vrai ou faux
        """
        return self.ouverture.estActive()

class Inscription(models.Model):
    """
    La relation binaire entre un utudiant et un cours, qui résulte de
    son vote.
    """
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

