from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

from aperho.settings import connection
from .models import Etudiant, Enseignant, Formation, Inscription, Cours,\
    estProfesseur

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
                attributes=["uidNumber", "sn", "givenName", "uid" ]
                )
            for entry in connection.response:
                eleves.append(
                    {
                        "uidNumber":entry['attributes']['uidNumber'][0],
                        "uid":entry['attributes']['uid'][0],
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
                etudiant=Etudiant(uidNumber=e["uidNumber"],uid=e["uid"],
                                  nom=e["nom"], prenom=e["prenom"],
                                  classe=e["classe"])
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

def addInscription(request):
    """
    ajoute une inscription à un cours
    renvoie un en-tête json, et des données de feedback
    """
    message=""
    ok=True
    uid=request.GET.get("uid")
    clData=request.GET.get("classes")
    if clData:
        classes=[int(c) for c in clData.split(":")]
    else:
        classes=[]
    ## on retire les classes à public désigné de celles où il est possible
    ## de s'inscrire
    classesOk=[]
    for c in classes:
        if not Cours.objects.filter(pk=c)[0].formation.public_designe:
            classesOk.append(c)
    classes=classesOk
    etudiants=list(Etudiant.objects.filter(uid=uid))
    if not etudiants:
        message="ERREUR : {} ne fait pas partie des élèves qui peuvent s'inscrire".format(uid)
        ok=False
    else:
        etudiant=etudiants[0]
        ## effacement des inscriptions précédentes
        ## !!! il faudrait prendre en compte une période des AP
        Inscription.objects.filter(etudiant=etudiant, cours__formation__public_designe=False).delete()
        if clData == "": # cas d'un effacement demandé
            message="Effacement terminé."
        else:
            message="Inscriptions : "
            for c in classes:
                classe=Cours.objects.filter(pk=c)[0]
                inscription=Inscription(etudiant=etudiant, cours=classe)
                inscription.save()
                message+="« {}, {}...» ".format(classe.formation.titre, classe.formation.contenu[:20])
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })
   
def lesCours(request):
    """
    affiche les cours d'un prof
    """
    prof=estProfesseur(request.user)
    pourqui=request.GET.get("uid","")
    cours=Cours.objects.all()
    noninscrits=set([])
    if pourqui:
        ### on ne garde que les cours du seul prof qui demande
        nom=request.user.last_name
        prenom=request.user.first_name
        cours=cours.filter(enseignant__nom=nom, enseignant__prenom=prenom)
    else:
        ## calcul des non-inscrits
        eleves=set([e for e in Etudiant.objects.all()])
        inscrits=set([i.etudiant for i in Inscription.objects.all()])
        noninscrits=eleves-inscrits
    cours=list(cours.order_by("enseignant__nom","horaire",))
    enseignants=[c.enseignant for c in cours]
    horaires=set([c.horaire for c in cours])
    eci={} ## dictionnaire enseignant -> cours -> inscriptions
    for e in enseignants:
        ec=[c for c in cours if c.enseignant==e]
        eci[e]={}
        i=0
        for c in ec:
            inscriptions=Inscription.objects.filter(cours=c)
            eci[e][c]=list(inscriptions.order_by('etudiant__nom','etudiant__prenom'))
            i+=len(eci[e][c])
        e.nbEtudiants=i
    return render(
            request, "lesCours.html",
            context={
                "prof":  prof,
                "eci":   eci,
                "horaires": horaires,
                "estprof": estProfesseur(request.user),
                "username": request.user.username,
                "noninscrits": noninscrits,
            }
        ) 
