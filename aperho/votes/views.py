from django.shortcuts import render
from django.http import HttpResponse

from aperho.settings import connection
from .models import Etudiant, Enseignant, Formation

def index(request):
    return HttpResponse("Hello, voici l'index des votes.")

def nomClasse(s):
	"""
	Correction des noms des classes ;
	dans notre annuaire, toutes les classes sont préficées par "c"
	"""
	if s[0]=="c":
		return s[1:]
	else:
		return s
		
def addEleves(request):
    """
    Une page pour ajouter des élèves à une barrette d'AP
    """
    eleves=[]
    wantedClasses = request.POST.getlist("classes")
    ######################################
    # affichage des élèves ajoutés
    ######################################
    if wantedClasses:
        for gid in wantedClasses:
            ### récupération du nom de la classe
            base_dn = 'ou=Groups,dc=lycee,dc=jb'
            filtre  = '(gidNumber={})'.format(gid)
            connection.search(
                search_base = base_dn,
                search_filter = filtre,
                attributes=["cn" ]
                )
            for entry in connection.response:
                cn=nomClasse(entry['attributes']['cn'][0])
            ### récupération des élèves inscrits dans la classe
            base_dn = 'ou=Users,dc=lycee,dc=jb'
            filtre  = '(&(objectClass=kwartzAccount)(gidNumber={}))'.format(gid)
            connection.search(
                search_base = base_dn,
                search_filter = filtre,
                attributes=["uidNumber", "sn", "givenName" ]
                )
            for entry in connection.response:
                eleves.append(
                    {
                        "uid":entry['attributes']['uidNumber'][0],
                        "nom":entry['attributes']['sn'][0],
                        "prenom":entry['attributes']['givenName'][0],
                        "classe": cn,
                    }
                )
        eleves.sort(key=lambda e: "{classe} {nom} {prenom}".format(**e))
        for e in eleves:
            etudiant=Etudiant.objects.filter(uid=e["uid"])
            if not etudiant:
                ## création d'un nouvel enregistrement
                etudiant=Etudiant(uid=e["uid"], nom=e["nom"],
                                  prenom=e["prenom"], classe=e["classe"])
                etudiant.save()
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre = '(&(cn=c*)(!(cn=*smbadm))(objectclass=kwartzGroup))'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes = ['cn', 'gidnumber'],
    )
    classes=[]
    for entry in connection.response:
        classes.append({
            'gid':entry['attributes']['gidNumber'][0],
            'classe':nomClasse(entry['attributes']['cn'][0]),
        })
    ### Liste des classes déjà connues dans la base de données
    etudiants=list(Etudiant.objects.all())
    classesDansDb=list(set([nomClasse(e.classe) for e in Etudiant.objects.all()]))
    return render(
        request, "addEleves.html",
        context={
            "classes": classes,
            "eleves":  eleves,
            "classesDansDb" : classesDansDb,
        }
    )

def getAllProfs():
    """
    fait la liste de tous les profs de l'annuaire et absents de la
    barrette
    """
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre  = '(cn=profs)'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["gidNumber" ]
        )
    gid=connection.response[0]['attributes']["gidNumber" ][0]
    profs=[]
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre  = '(gidNumber={})'.format(gid)
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["cn" ]
        )
    for entry in connection.response:
        cn=nomClasse(entry['attributes']['cn'][0])
    ### récupération des profs
    base_dn = 'ou=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(gidNumber={}))'.format(gid)
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName" ]
        )
    ## liste des uids de profs déjà dans la barrette
    uids=[p.uid for p in Enseignant.objects.all()]
    for entry in connection.response:
        if int(entry['attributes']['uidNumber'][0]) not in uids:
            ## on n'ajoute le prof que s'il n'est pas encore dans la barrette
            profs.append(
                {
                    "uid":entry['attributes']['uidNumber'][0],
                    "nom":entry['attributes']['sn'][0],
                    "prenom":entry['attributes']['givenName'][0],
                }
            )
    profs.sort(key=lambda e: "{nom} {prenom}".format(**e))
    return profs

def getProfs(uids):
    """
    récupère une liste de profs étant donné la liste de leurs uids
    """
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre  = '(cn=profs)'
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["gidNumber" ]
        )
    gid=connection.response[0]['attributes']["gidNumber" ][0]
    profs=[]
    base_dn = 'ou=Users,dc=lycee,dc=jb'
    filtre  = '(&(objectClass=kwartzAccount)(gidNumber={gid})(|{uids}))'.format(
        gid=gid,
        uids=" ".join(["(uidNumber={})".format(uid) for uid in uids]),
    )
    connection.search(
        search_base = base_dn,
        search_filter = filtre,
        attributes=["uidNumber", "sn", "givenName" ]
    )
    for entry in connection.response:
        profs.append(
            {
                "uid":entry['attributes']['uidNumber'][0],
                "nom":entry['attributes']['sn'][0],
                "prenom":entry['attributes']['givenName'][0],
            }
        )
    profs.sort(key=lambda e: "{nom} {prenom}".format(**e))
    return profs

def addProfs(request):
    """
    Une page pour ajouter des profs à une barrette d'AP
    """
    ajout=request.POST.get("ajout", "")
    ajout1=request.POST.get("ajout1", "")
    if ajout:
        # on a sélectionné des profs pas encore dans la barrette
        uids=[int(key) for key, val in request.POST.items() if val=="on"]
        profs=getProfs(uids)
        return render(
            request, "addProfs1.html",
            context={
                "profs":  profs,
                "uids": uids,
            }
        )
    elif ajout1:
        # on a renseigné les salles des profs choisis
        uids=eval(request.POST.get("uids","[]"))
        profs=getProfs(uids)
        for p in profs:
            p["salle"]=request.POST.get(p["uid"],"")
            e, created = Enseignant.objects.update_or_create(
                uid=p["uid"],
                defaults=p
            )
        return render(
            request, "addProfs2.html",
            context={
                "profs":  profs,
                "uids": uids,
            }
        )        
    ############### pas d'ajout en cours. on affiche une liste de profs
    profs=getAllProfs()
    return render(
        request, "addProfs.html",
        context={
            "profs":  profs,
        }
    )

def addFormation(request):
    """
    ajout d'une formation dans la barrette
    """
    if request.POST.get("ok",""):
        # on a validé la formation, il faut l'enregistrer
        f=Formation(
            titre=request.POST.get("titre",""),
            contenu=request.POST.get("contenu",""),
            duree=int(request.POST.get("duree",1)),
        )
        f.save()
        return render(
            request, "addFormation1.html",
            context={
                "f": f,
            }
        )
    ### pas encore de formation à valider : on demande
    return render(
        request, "addFormation.html",
    )
