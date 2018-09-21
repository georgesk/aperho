## Fonctions qui interacissent avec l'annuaire LDAP de Kwartz

from aperho.settings import connection

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
    #### d'abord, user est-il prof ?
    base_dn = 'cn=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(cn={}))'.format(login)
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName", "memberOf",]
        )
    if len(connection.response) > 0 and \
          "CN=profs,CN=Users,DC=lycee,DC=jb" in \
          connection.response[0]["attributes"]["memberOf"]: # c'est un prof.
        if len(Enseignant.objects.filter(nom=nom, prenom=prenom))==0:
            result="prof"
        else:
            result="profAP"
    #### par défaut : ce n'est pas un prof
    return result

def lesClasses():
    """
    Renvoie les classes connues par l'annuaire LDAP
    @return une liste de noms de classes, sans le préfixe "c"
    """
    base_dn = 'cn=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzGroup)(cn=c*))'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["cn" ]
    )
    classes=[entry['attributes']['cn'] for entry in connection.response]
    classes=[nomClasse(c) for c in classes if classeValide(c)]
    return classes

def classeValide(c):
    """
    décide si un nom de classe peut effectivement servir à des élèves
    @param c nom de classe
    @return un booléen
    """
    notclasses=[ 'cdtower', 'cuisine',  'college', 'cdi' ]
    return c not in notclasses and \
        "c"+c not in notclasses and \
        'smbadm' not in c and \
        'test' not in c

def nomClasse(s):
	"""
	Correction des noms des classes ;
	dans notre annuaire, toutes les classes sont préfixées par "c"
	"""
	if s[0]=="c":
		return s[1:]
	else:
		return s

