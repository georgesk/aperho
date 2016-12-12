from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json

from aperho.settings import connection
from .models import Etudiant, Enseignant, Formation, Inscription, Cours,\
    estProfesseur, Ouverture, Orientation, InscriptionOrientation, \
    CoursOrientation, Cop
from .csvResult import csvResponse
from .odfResult import odsResponse, odtResponse
from collections import OrderedDict

def index(request):
    return HttpResponse("Hello, voici l'index des votes.")


def nomClasse(s):
	"""
	Correction des noms des classes ;
	dans notre annuaire, toutes les classes sont préfixées par "c"
	"""
	if s[0]=="c":
		return s[1:]
	else:
		return s

def cop (request):
    """
    Affecte les élèves aux formations des Conseillères d'Orientation
    Psychologues (COP) et affiche un feedback
    """
    ori=list(Orientation.objects.all())
    ori1=[]
    for o in ori:
        ## on recopie seulement les cas où l'étudiant n'est pas NULL
        ## c'est un peu compliqué car l'accès à l'étudiant n'est pas
        ## garanti sans lever une exception.
        try:
            if o.etudiant:
                ori1.append(o)
        except:
            pass
    ## on catégorise les orientations par les choix
    orientations=OrderedDict()
    choices=Orientation._meta.get_field("choix").choices
    ## on met en place un ordre prédéfini pour les clés, d'abord les formations
    ## générales
    for c in choices:
        orientations[c[1]]=[]
    ## on replit le dictionnaire ordonné avec les orientations
    for o in ori1:
        titre=choices[o.choix-1][1]
        orientations[titre].append(o)
     ## on efface toutes les inscriptions aux séances des COPs
    InscriptionOrientation.objects.all().delete()
    ## on compte le nombre de séances possibles pour les cops
    seances=list(CoursOrientation.objects.all().order_by("debut","cop"))
    nbseances=len(seances)
    ## on en déduit la répartition des élèves, sans mixer les
    ## choix d'orientation
    moyenne=(len(ori1)/nbseances)+1 # nombre moyen d'élèves à placer par séance, un peu majoré
    total=0
    decalages={} # type d'orientation => décalage dans la liste des séances
    for titre in orientations:
        decalages[titre]=total
        nb=len(orientations[titre])
        nbcours=int(0.5+nb/moyenne)
        total+=nbcours
    affectations=OrderedDict() # seance => liste des élèves affectés
    for s in seances:
        affectations[s]={"formation": choices[s.formation-1][1], "orientations": []}
    for o in ori1:
        ## pour chaque inscription à un cours d'orientation
        titre=choices[o.choix-1][1]
        decalage=decalages[titre]
        ## on trouve la bonne séance et on y ajoute l'inscription
        s=seances[decalage]
        affectations[s]["orientations"].append(o)
        ## on inscrit ça dans la base de données
        inscr=InscriptionOrientation(etudiant=o.etudiant, cours=s)
        inscr.save()
        ## on s'assure que le formation correspondra au choix de l'élève
        s.formation=o.choix
        ## si la séance est pleine, on passe à la suivante
        if len(affectations[s]["orientations"]) > moyenne:
            decalages[titre] += 1
            
    return render(
        request, "cop.html",
        context={
            "orientations": orientations,
            "nbseances":    nbseances,
            "seances":      seances,
            "affectations": affectations,
        }
    )
    
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
    classesDansDb.sort()
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
    orData=request.GET.get("orientations")
    if orData:
        orientations=[int(o) for o in orData.split(":")]
    else:
        orientations=[]
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
        ###############################################################
        ## on met à jour les orientations
        ## ça ne fait rien du tout en l'absence de champ d'orientations.
        ouverture=[o for o in Ouverture.objects.all() if o.estActive()]
        # ouverture[0] est l'ouverture active si la liste n'est pas vide
        if ouverture and orientations:
            choices=Orientation._meta.get_field("choix").choices
            for key, val in choices:
                ## l'élève a peut-être déjà choisi cette orientation
                dejaChoisi=Orientation.objects.filter(etudiant=etudiant, ouverture=ouverture[0], choix=key).first()
                if key in orientations:
                    if not dejaChoisi:
                        # s'il ne l'a pas déjà on la crée
                        ori=Orientation(etudiant=etudiant, ouverture=ouverture[0], choix=key)
                        ori.save()
                else:
                    ## l'élève ne veut pas de cette orientation
                    if dejaChoisi:
                        dejaChoisi.delete()
        ######################################################################
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
    csv=request.GET.get("csv","")
    ods=request.GET.get("ods","")
    odt=request.GET.get("odt","")
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
    cops=list(Cop.objects.all().order_by("nom"))
    horaires=set([c.horaire for c in cours])
    cci=OrderedDict() ## dictionnaire cop -> coursOrientation -> inscriptionOrientations
    for c in cops:
        cc=[co for co in CoursOrientation.objects.all().order_by("debut") if co.cop==c]
        cci[c]=OrderedDict()
        choices=Orientation._meta.get_field("choix").choices
        for co in cc:
            co.choice=choices[co.formation-1][1]
            io=InscriptionOrientation.objects.filter(cours=co)
            cci[c][co]=list(io.order_by('etudiant__nom','etudiant__prenom'))
    eci=OrderedDict() ## dictionnaire enseignant -> cours -> inscriptions
    for e in enseignants:
        ec=[c for c in cours if c.enseignant==e]
        eci[e]={}
        i=0
        for c in ec:
            inscriptions=Inscription.objects.filter(cours=c)
            eci[e][c]=list(inscriptions.order_by('etudiant__nom','etudiant__prenom'))
            i+=len(eci[e][c])
        e.nbEtudiants=i
    if csv:
        response=csvResponse(Inscription.objects.all(), noninscrits)
        return response
    elif ods:
        response=odsResponse(Inscription.objects.all(), noninscrits)
        return response
    elif odt:
        response=odtResponse(eci, horaires, noninscrits)
        return response
    else:
        return render(
            request, "lesCours.html",
            context={
                "prof":  prof,
                "eci":   eci,
                "cops": cops,
                "cci" : cci,
                "horaires": horaires,
                "estprof": estProfesseur(request.user),
                "username": request.user.username,
                "noninscrits": noninscrits,
            }
        ) 

def enroler(request):
    """
    Les profs du groupe d'AP peuvent enrôler des élèves non-inscrits
    grâce à cette page
    """
    cours=list(Cours.objects.all().order_by("enseignant__nom", "horaire"))
    for c in cours:
        # on ajout l'attribut n, remplissage du cours
        c.n= len(Inscription.objects.filter(cours=c))
    ## calcul des non-inscrits
    eleves=set([e for e in Etudiant.objects.all()])
    inscrits=set([i.etudiant for i in Inscription.objects.all()])
    noninscrits=list(eleves-inscrits)
    noninscrits.sort(key=lambda e: e.nom)
    return render(
            request, "enroler.html",
            context={
                "prof":        estProfesseur(request.user),
                "estprof":     estProfesseur(request.user),
                "username":    request.user.username,
                "cours":       cours,
                "noninscrits": noninscrits,
            }
        )

def enroleEleveCours(request):
    """
    enrole un élève dans un cours request.POST doit contenir deux variables,
    uid et cours.
    """
    uid=request.GET.get("uid","")
    cours=request.GET.get("cours","")
    cours2=request.GET.get("cours2","")
    possible="je ne peux pas enrôler"
    if "profAP" == estProfesseur(request.user):
        possible="je peux enrôler"
    msg=""
    ok=True
    if possible:
        lesCours=list(Cours.objects.all())
        c1=[c for c in lesCours if c.id==int(cours)]
        c2=[c for c in lesCours if c.id==int(cours2)]
        ## test de durée
        duree=0
        for c in c1+c2:
            duree+=c.formation.duree
        if duree != 2:
            msg="ERREUR : la durée totale des cours choisis est {} heures, il faut 2 heures exactement.".format(duree)
            ok=False
        ## test d'exclusion
        if len(c1+c2)==2 : ##deux cours différents
            if c1[0].horaire==c2[0].horaire:
                msg="ERREUR : Il est impossible d'enrôler pour deux cours à la même heure ({}).".format(c1[0].horaire)
                ok=False
        ## test de remplissage
        if c1:
            r1=len(Inscription.objects.filter(cours=c1[0]))
            if r1 >= c1[0].capacite:
                msg="ERREUR : Le cours {} à {} accueille déjà {} élèves, il est plein.".format(c1[0].formation.titre, c1[0].horaire, r1)
                ok=False
        if c2:
            r2=len(Inscription.objects.filter(cours=c2[0]))
            if r2 >= c2[0].capacite:
                msg="ERREUR : Le cours {} à {} accueille déjà {} élèves, il est plein.".format(c2[0].formation.titre, c2[0].horaire, r2)
                ok=False
        if ok:
            eleve=list(Etudiant.objects.filter(uid=uid))
            if len(eleve)==0:
                msg="ERREUR : Élève inconnu."
            else:
                eleve=eleve[0]
                ## vérifie que l'élève n'est pas déjà inscrit
                inscr=len(Inscription.objects.filter(etudiant=eleve))
                if inscr:
                    msg="ERREUR : {} {} {} est déjà inscrit.". format(eleve.nom, eleve.prenom, eleve.classe)
                else:
                    if c1:
                        inscription=Inscription(etudiant=eleve,cours=c1[0])
                        inscription.save()
                    if c2:
                        inscription=Inscription(etudiant=eleve,cours=c2[0])
                        inscription.save()
                    msg="OK : {} {} {} a été inscrit dans {} cours.".format(
                        eleve.nom, eleve.prenom, eleve.classe, len(c1+c2),
                    )
    else:
        msg="ERREUR : Impossible de faire l'inscription, il faut être professeur dans cette barrette d'AP."    
    return JsonResponse({
        "msg" : msg,
    })
