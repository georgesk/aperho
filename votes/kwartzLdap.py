## Fonctions qui interacissent avec l'annuaire LDAP de Kwartz

from collections import OrderedDict
from django.shortcuts import render
from django.http import JsonResponse

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

def inscritClasse(gid, barrette, cn=""):
    """
    Interroge l'annuaire et inscrit les élèves d'une classe dans la BD.
    Remarque : un élève ne peut être inscrit qu'une seule fois dans la BDD
    à cause de la contrainte UNIQUE pour votes_etudiant.uidNumber
    @param gid l'identifiant d'une classe dans l'annuaire LDAP
    @param barrette une instance de Barrette
    @param cn un nom de classe (sans le "c" initial), qui prend
    la précédence sur gid quand il est donné
    @return une liste d'instance d'Etudiant
    """
    from .models import Etudiant
    
    eleves=[]
    if cn:
        ### récupération du groupe de la classe
        base_dn = 'cn=Users,dc=lycee,dc=jb'
        filtre  = '(&(cn=c{})(objectClass=kwartzGroup))'.format(cn)
        connection.search(
            search_base = base_dn,
            search_filter = filtre,
            attributes=["gidNumber" ]
            )
        for entry in connection.response:
            gid=nomClasse(entry['attributes']['gidNumber'])
    else:
        ### récupération du nom de la classe
        base_dn = 'cn=Users,dc=lycee,dc=jb'
        filtre  = '(&(gidNumber={})(objectClass=kwartzGroup))'.format(gid)
        connection.search(
            search_base = base_dn,
            search_filter = filtre,
            attributes=["cn" ]
            )
        for entry in connection.response:
            cn=nomClasse(entry['attributes']['cn'])
    ## à ce stade, cn est un nom de classe dans l'annuaire LDAP et
    ## gid est le numéro du groupe dans la base LDAP
    ## récupération des élèves inscrits dans la classe
    base_dn = 'cn=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(gidNumber={}))'.format(gid)
    # recherche des membres de la classe avec gidNumber==gid, avec leurs
    # noms et prénoms, et identifiants
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName", "cn" ]
        )
    for entry in connection.response:
        # si un élève est déjà dans la BDD, mais avec une barrette
        # ou une classe autres, on change classe et barrette.
        aChanger=Etudiant.objects.filter(uidNumber=entry['attributes']['uidNumber'])
        for e in aChanger: # en fait il y en a zéro ou un
            if e.classe!=cn or e.barrette!=barrette:
                e.classe=cn
                e.barrette=barrette
                e.save()
        # finalement on ramène l'élève de la base de données avec les
        # bons attributs
        e,status=Etudiant.objects.get_or_create(
            uidNumber=entry['attributes']['uidNumber'],
            uid=entry['attributes']['cn'],
            nom=entry['attributes']['sn'],
            prenom=entry['attributes']['givenName'],
            classe=cn,
            barrette=barrette,
        )
        eleves.append(e)
    return eleves
    
def addEleves(request):
    """
    Une page pour ajouter des élèves à une barrette d'AP
    """
    from .models import Barrette, Etudiant
    from aperho.home import dicoBarrette

    eleves=[]
    wantedClasses = request.POST.getlist("classes")
    barrette = request.POST.get("barrette")
    if not barrette:
        barrette=request.session.get("barrette")
    ######################################
    # affichage des élèves ajoutés
    ######################################
    if wantedClasses:
        for gid in wantedClasses:
            b=Barrette.objects.get(nom=barrette)
            nouveaux=inscritClasse(gid,b)
            if nouveaux:
                eleves+=nouveaux
                b.addClasse(nouveaux[0].classe)
        eleves.sort(key=lambda e: "{classe} {nom} {prenom}".format(classe=e.classe, nom=e.nom, prenom=e.prenom))
    #### le cas où wantedClasses est non-nul est traité.
    ### Liste des classes déjà connues dans la base de données
    barrette=request.session.get("barrette")
    b=Barrette.objects.get(nom=barrette)
    etudiants=list(Etudiant.objects.filter(barrette=b))
    classesDansDb=OrderedDict()
    for e in etudiants:
        nom=nomClasse(e.classe)
        if nom in classesDansDb:
            classesDansDb[nom].append("%s %s" %(e.nom,e.prenom))
        else:
            classesDansDb[nom]=["%s %s" %(e.nom,e.prenom)]
    sortedClasses=sorted(list(classesDansDb.keys()))
    classesDansDb=OrderedDict(("%s (%s)" %(key,len(classesDansDb[key])), ", ".join(sorted(classesDansDb[key]))) for key in sortedClasses)

    classes=[]
    base_dn = 'cn=Users,dc=lycee,dc=jb'
    filtre = '(&(cn=c*)(!(cn=*smbadm))(objectclass=kwartzGroup))'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes = ['cn', 'gidNumber'],
    )
    for entry in connection.response:
        nom=nomClasse(entry['attributes']['cn'])
        if nom in classesDansDb.keys() or not classeValide(nom):
            # ne pas mettre les classes déjà présentes dans la barrette
            # ni les noms contenant "test", "cuisine", etc.
            continue
        classes.append({
            'gid':entry['attributes']['gidNumber'],
            'classe': nom,
        })
    classes=sorted(classes, key=lambda d: d["classe"])
    context={
        "classes": classes,
        "eleves":  eleves,
        "classesDansDb" : classesDansDb,
    }
    context.update(dicoBarrette(request))
    return render(request, "addEleves.html", context)

def getProfsLibres(barrette):
    """
    fait la liste de tous les profs de l'annuaire et absents de la
    barrette
    @param barrette un nom de barrette
    """
    from .models import Barrette, Enseignant
    
    profs=[]
    ### récupération des profs
    base_dn = 'cn=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(memberOf=CN=profs,CN=Users,DC=lycee,DC=jb))'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName", "cn" ]
        )
    ## liste des uids de profs déjà dans la barrette
    b=Barrette.objects.filter(nom=barrette)[0]
    uids=[p.uid for p in Enseignant.objects.filter(barrettes__in=[b.pk])]
    for entry in connection.response:
        if int(entry['attributes']['uidNumber']) not in uids:
            ## on n'ajoute le prof que s'il n'est pas encore dans la barrette
            try:
                profs.append(
                    {
                        "uid": entry['attributes']['uidNumber'],
                        "nom": entry['attributes']['sn'],
                        "prenom": entry['attributes']['givenName'],
                        "username": entry['attributes']['cn'],
                    }
                )
            except:
                pass # par exemple s'il n'y a pas d'attribut givenName
    profs.sort(key=lambda e: "{nom} {prenom}".format(**e))
    return profs

def addUnProf(request):
    """
    fonction de rappel pour inscrire un prof
    """
    from .models import Enseignant, Barrette
    
    ok="ok"
    prof=request.POST.get("prof")
    salle=request.POST.get("salle")
    matiere=request.POST.get("matiere")
    barrette=request.POST.get("barrette")
    libres=getProfsLibres(barrette)
    trouve=[p for p in libres if "{nom} {prenom}".format(**p) == prof]
    if trouve:
        prof=trouve[0]
        try:
            enseignant=Enseignant.objects.filter(
                nom=prof["nom"],
                prenom=prof["prenom"],
                username=prof["username"],
            ).first()
            if enseignant:
                if enseignant.salle!=salle or enseignant.matiere!=matiere:
                    enseignant.salle=salle
                    enseignant.matiere=matiere
                    enseignant.save()
            else:
                enseignant=Enseignant(
                    uid=prof["uid"],
                    nom=prof["nom"],
                    prenom=prof["prenom"],
                    username=prof["username"],
                    salle=salle,
                    matiere=matiere,
                )
                enseignant.save()

            # b__in fait référence au champ "barrettes" du prof
            bb=[b.nom for b in list(Barrette.objects.filter(b__in=[enseignant.pk]))]
            if barrette in bb:
                pass # pas besoin d'ajouter la barrette pour cet enseignant
            else:
                b=Barrette.objects.get(nom=barrette)
                enseignant.barrettes.add(b)
            message="%s est enregistré(e)" %prof
        except Exception as e:
            message="Erreur %s" %e
            ok="ko"
    else:
        message="Le professeur n'a pas été trouvé"
        ok="ko"
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })

