from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.utils.timezone import datetime
from django.forms import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist

import json, re

from aperho.home import dicoBarrette
from .models import Etudiant, Enseignant, Formation, Inscription, Cours,\
    estProfesseur, Ouverture, Orientation, \
    InscriptionOrientation, CoursOrientation, Cop, Horaire, Barrette, \
    classeCourante
from .csvResult import csvResponse
from .odfResult import odsResponse, odtResponse
from .forms import editeCoursForm
from .kwartzLdap import lesClasses, inscritClasse, addElevesLdap, \
    getProfsLibres, addUnProfLdap, etudiantsDeClasse

from collections import OrderedDict

def index(request):
    return HttpResponse("Hello, voici l'index des votes.")


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
    ## à ce stade ori1 contient les orientations avec étudiant non null
    ###################################################################
    ## on catégorise les orientations par les choix
    orientations=OrderedDict()
    choices=Orientation._meta.get_field("choix").choices
    ## on met en place un ordre prédéfini pour les clés, d'abord les formations
    ## générales, tout comme dans la liste choices
    for c in choices:
        orientations[c[0]]=[]
    ## on replit le dictionnaire ordonné avec les orientations
    for o in ori1:
        orientations[o.choix].append(o)
     ## on efface toutes les inscriptions aux séances des COPs
    InscriptionOrientation.objects.all().delete()
    ## on compte le nombre de séances possibles pour les cops
    seances=list(CoursOrientation.objects.all().order_by("debut","cop"))
    ## on en déduit la répartition des élèves, sans mixer les
    ## choix d'orientation
    affectations=OrderedDict() # seance => liste des élèves affectés
    derniereSeance=0
    effectifSeance={} ## dictionnaire : n° choix => effectif optimal
    for choix in orientations:
        ## calcul du nombre de profs à mobiliser pour les COPS
        ## sachant que la capacité d'un cours de COP est 27
        totalOrientation=len(list(Orientation.objects.filter(choix=choix)))
        nbProfs=1+int(totalOrientation/27)          # nb de profs à mobiliser
        effectifSeance[choix]=1+int(totalOrientation/nbProfs)
        for indexSeance in range(derniereSeance, derniereSeance+nbProfs):
            seances[indexSeance].formation=choix
        derniereSeance+=nbProfs
    ## À ce stade, derniereSeance pointe sur la dernière séance des COPS
    ## Pour chaque séance, on remplit avec la liste des élèves qui sont
    ## avec le prof de séance, en priorité, puis on butine les profs des
    ## séances non utilisées pour finir de remplir. On n'affecte que les
    ## élèves qui suivent la formation prévue pour cette séance.
    ############################################################
    dejaEnroles={} ## dictionnaire : n° choix => liste de chaînes d'étudiants
    ## il faut comptabiliser str(Etudiant) plutôt que les instances de
    ## etudiant, si la comparaison des instances peut poser problème
    ############################################################
    ## premier round : on enrole les étudiants du prof sélectionné
    for c in choices:
        dejaEnroles[c[0]]=[]
    for s in seances[:derniereSeance]:
        enrolesDansSeance=[]
        ## commençons par le prof de la séance
        cours=Cours.objects.filter(enseignant=s.prof)
        for c in cours:
            if c.formation.duree==1 and \
               c.horaire.heure.strftime("%H:%M") != timezone.localtime(s.debut).strftime("%H:%M"):
                # cours d'une heure, mais pas à la bonne heure
                continue
            ## maintenant c est un cours de deux heures,
            ## ou c est à l'heure de la séance
            ## on parcourt les élèves inscrits au cours
            for i in Inscription.objects.filter(cours=c):
                voeux=Orientation.objects.filter(etudiant=i.etudiant, choix=s.formation)
                ## on regarde si l'élève  a un voeu pour s.formation
                ## et s'il n'est pas déjà inscrit à s.formation
                if voeux.count() and \
                   str(i.etudiant) not in dejaEnroles[s.formation]:
                    enrolesDansSeance.append(i.etudiant)
                    dejaEnroles[s.formation].append(str(i.etudiant))
        affectations[s]=enrolesDansSeance
    ## deuxième round : on enrole les élèves pas encore inscrits
    ## en tournant parmi tous les élèves
    etudiants=Etudiant.objects.all()
    for s in seances[:derniereSeance]:
        for e in etudiants:
            if str(e) not in dejaEnroles[s.formation] and Orientation.objects.filter(etudiant=e, choix=s.formation).count() > 0 and len(affectations[s]) < effectifSeance[s.formation]:
                ## à ce stade, l'étudiant est encore libre
                ## et il a un voeu compatible
                affectations[s].append(e)
                dejaEnroles[s.formation].append(str(e))
                
    ## inscription des affectations dans la base de données
    for s in affectations:
        for e in affectations[s]:
            io=InscriptionOrientation(etudiant=e, cours=s)
            io.save()
    context={
        "orientations": orientations,
        "seances":      seances,
        "affectations": affectations,
    }
    context.update(dicoBarrette(request))
    return render(request, "cop.html", context)

def changeSalle(request):
    """
    fonction de rappel pour changer un prof de salle
    """
    prof=request.POST.get("prof","")
    salle=request.POST.get("salle","")
    barrette=request.POST.get("barrette","")
    nouvelleSalle=request.POST.get("nouvelleSalle","")
    matiere=request.POST.get("matiere","")
    nouvelleMatiere=request.POST.get("nouvelleMatiere","")
    indir=request.POST.get("indir","")=="true"
    b=Barrette.objects.get(nom=barrette)
    trouve=[e for e in Enseignant.objects.filter(barrettes__in=[b.pk]) if "%s %s" %(e.nom, e.prenom)==prof]
    if trouve:
        try:
            ok="ok"
            trouve[0].salle=nouvelleSalle
            trouve[0].matiere=nouvelleMatiere
            if indir:
                trouve[0].indirects.add(b)
            else:
                trouve[0].indirects.remove(b)
            trouve[0].save()
            message="Mis %s en salle %s (%s)" %(prof,nouvelleSalle,nouvelleMatiere)
        except Exception as e:
            ok="ko"
            message="Erreur: %s" %e
    else:
        ok="ko"
        message="pas trouvé %s dans la barrette %s" %(prof, barrette)
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })
            
def delProfBarrette(request):
    """
    Détache un prof d'une barrette
    """
    prof=request.POST.get("prof","")
    barrette=request.POST.get("barrette","")
    b=Barrette.objects.get(nom=barrette)
    trouve=[e for e in Enseignant.objects.filter(barrettes__in=[b.pk]) if "%s %s" %(e.nom, e.prenom)==prof]
    if trouve:
        try:
            trouve[0].barrettes.remove(b)
            ok="ok"
            message="%s supprimé(e) de la barrette" %prof
        except Exception as e:
            ok="ko"
            message="Erreur : %s" %e
    else:
        ok="ko"
        message="pas trouvé %s dans la barrette" %prof
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })
    
def addProfs(request):
    """
    Une page pour ajouter des profs à une barrette d'AP
    """
    barretteCourante=request.session.get("barrette")
    b=Barrette.objects.filter(nom=barretteCourante)[0]
    profsInscrits=list(Enseignant.objects.filter(barrettes__in=[b.pk]).order_by('nom'))
    for p in profsInscrits:
        # b__in fait référence à la référence de prof par "barrettes"
        # par opposition à la référence par "indirects"
        p.bb=", ".join([b.nom for b in list(Barrette.objects.filter(b__in=[p.pk]).order_by('nom'))])
        p.indir= b in p.indirects.all() # vrai si le prof a une inscription indirecte 
    profs=getProfsLibres(barretteCourante)
    context={
        "barretteCourante": b.nom,
        "profs":  profs,
        "profsInscrits": profsInscrits,
    }
    context.update(dicoBarrette(request))
    return render(request, "addProfs.html", context)

def chargeProf(request):
    """
    récpère un prof d'après son nom et son prénom
    """
    trouves=[e for e in Enseignant.objects.all()
             if request.POST.get("nomPrenom")== e.nom+" "+e.prenom]
    if trouves:
        e=trouves[0]
        return JsonResponse({
            "ok"      : "ok",
            "salle"   : e.salle,
            "matiere" : e.matiere,
        })
    return JsonResponse({
        "ok"      : "ko",
    })
    
        

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
            jaugeOK=True
            message="Inscriptions : "
            complets=[]
            for c in classes:
                classe=Cours.objects.get(pk=c)
                ## on vérifie la jauge de cette classe
                if classe.complet :
                    jaugeOK=False
                    complets.append("<span style='color:red; font-weight: bold;'>La classe {} -- {} était déjà pleine</span> ... ".format(classe.formation.titre, classe.formation.contenu[:20]))
            if jaugeOK:
                for c in classes:
                    classe=Cours.objects.get(pk=c)
                    inscription=Inscription(etudiant=etudiant, cours=classe)
                    inscription.save()
                    message+="« {}, {}» ... ".format(classe.formation.titre, classe.formation.contenu[:20])
            else:
                message="Désolé, mais :"+", ".join(complets)
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })
   
def profil(request):
    barrette=request.session.get("barrette","")
    b=Barrette.objects.get(nom=barrette)
    e=Enseignant.objects.filter(username=request.user.username, barrettes=b)[0]
    salle=request.POST.get("salle","")
    matiere=request.POST.get("matiere","")
    modifEnregistree=False
    if salle and matiere:
        e.salle=salle
        e.matiere=matiere
        e.save()
        modifEnregistree=True
    context={
        "modifEnregistree": modifEnregistree,
        "estprof": estProfesseur(request.user),
        "barrette": barrette,
        "username": request.user.username,
        "prof": e
    }
    context.update(dicoBarrette(request))
    return render(request, "profil.html", context)
        
    
def lesCours(request):
    """
    affiche les cours des profs pour la barrettes courante
    et pour la dernière "Ouverture" en date.
    """
    prof=estProfesseur(request.user)
    pourqui=request.GET.get("uid","")
    csv=request.GET.get("csv","")
    ods=request.GET.get("ods","")
    odt=request.GET.get("odt","")
    # filtrage des cours : barrette courante et dernière session d'ouverture
    barrette=request.session.get("barrette","")
    b=Barrette.objects.get(nom=barrette)
    enseignant=None
    od=Ouverture.derniere()
    if not od:
        ## il faut définir au moins une première période d'ouverture d'aperho
        return HttpResponseRedirect('addOuverture')
    else:
        # on assure que chaque prof de la barrette ait au moins des cours
        # par défaut pour la dernière ouverture en date
        creeCoursParDefaut(barrette, od)
        cours=Cours.objects.filter(enseignant__barrettes__id=b.id, ouverture=od).order_by("horaire")
    noninscrits=set([])
    if pourqui:
        if request.user.is_superuser:
            ### pour l'admin, on extrait les données de pourqui
            enseignant=Enseignant.objects.get(username=pourqui, barrettes__id=b.id)
            cours=cours.filter(enseignant=enseignant)
        else:
            ### on ne garde que les cours du seul prof qui demande
            nom=request.user.last_name
            prenom=request.user.first_name
            enseignant=Enseignant.objects.get(nom=nom, prenom=prenom)
            cours=cours.filter(enseignant__nom=nom, enseignant__prenom=prenom)
    else:
        ## calcul des non-inscrits
        eleves=set([e for e in Etudiant.objects.all()
                    if e.classe in json.loads(b.classesJSON)])
        inscrits=set([i.etudiant for i in Inscription.objects.filter(cours__ouverture=od)])
        noninscrits=sorted(list(eleves-inscrits), key=lambda e: e.classe+e.nom)
    if pourqui:
        cours=list(cours.order_by("horaire"))
    else:
        cours=list(cours.order_by("formation__titre","enseignant__nom","horaire"))
    enseignants=[c.enseignant for c in cours]
    cops=list(Cop.objects.all().order_by("nom"))
    horaires=set([c.horaire for c in cours])
    horaires=sorted(list(horaires), key=lambda h: h.heure)
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
        if b in e.indirects.all():
            continue # rien pour les profs qui ont une participation indirecte
        ec=[c for c in cours if c.enseignant==e and c.barrette==b and not c.invalide]
        eci[e]=OrderedDict()
        i=0
        for c in ec:
            inscriptions=Inscription.objects.filter(cours=c)
            eci[e][c]=list(inscriptions.order_by('etudiant__nom','etudiant__prenom'))
            i+=len(eci[e][c])
        e.nbEtudiants=i
    if csv:
        inscriptions=Inscription.objects.filter(cours__barrette=b, cours_ouverture=od)
        response=csvResponse(inscriptions, noninscrits)
        return response
    elif ods:
        inscriptions=Inscription.objects.filter(cours__barrette=b, cours__ouverture=od)
        response=odsResponse(inscriptions, noninscrits)
        return response
    elif odt:
        response=odtResponse(eci, horaires, noninscrits, cci)
        return response
    else:
        # orientationOuverte est un booléen ; pour le forcer à vrai
        # il suffit qu'il y ait au moins un object Orientation avec
        # la bonne date d'ouverture, même si les autres champs sont par défaut.
        orientationOuverte=len([o for o in Orientation.objects.all() if o.ouverture.estActive()]) > 0
        ## on autorise à utiler cette page les profs d'AP et l'admin.
        autorise = prof=="profAP" or request.user.is_superuser
        context={
            "autorise":  autorise,
            "eci":   eci,
            "cops": cops,
            "orientationOuverte": orientationOuverte,
            "cci" : cci,
            "pourqui": pourqui,
            "horaires": horaires,
            "estprof": estProfesseur(request.user),
            "username": request.user.username,
            "noninscrits": noninscrits,
            "barrette": barrette,
            "ouverture" : od,
            "prof": enseignant,
        }
        context.update(dicoBarrette(request))
        return render(request, "lesCours.html", context)

def estEnPremier (c):
    """
    Vérifie si un cours est en premier
    @param c une instance de Cours
    @return True si le cours vient en premier dans l'horaire
    """
    h=Horaire.objects.get(pk=c.horaire_id)
    premier=Horaire.objects.filter(barrette_id=c.barrette_id).order_by('heure').first()
    return h.heure==premier.heure
    
def metEnPremier (c):
    """
    Modifie un cours pour le mettre premier dans l'horaire. On
    n'appelle cette procédure qu'après avoir vérifié qu'un cours est bien seul
    dans son horaire.
    @param c une instance de Cours
    """
    h=Horaire.objects.get(pk=c.horaire_id)
    premier=Horaire.objects.filter(barrette_id=c.barrette_id).order_by('heure').first()
    c.horaire=premier
    return

def metEnDernier (c):
    """
    Modifie un cours pour le mettre premier dans l'horaire. On
    n'appelle cette procédure qu'après avoir vérifié qu'un cours est bien seul
    dans son horaire.
    @param c une instance de Cours
    """
    h=Horaire.objects.get(pk=c.horaire_id)
    dernier=Horaire.objects.filter(barrette_id=c.barrette_id).order_by('heure').last()
    c.horaire=dernier
    return

def enroler(request):
    """
    Les profs du groupe d'AP peuvent enrôler des élèves non-inscrits
    grâce à cette page
    """
    etudiant=""
    coursConnus={}
    if request.GET.get("c0",""): # appel de la page avec des cours connus
        c0=int(request.GET.get("c0"))
        coursConnus[0]=Cours.objects.get(pk=c0)
        c1=int(request.GET.get("c1"))
        if c1>0:
            coursConnus[1]=Cours.objects.get(pk=c1)
    if request.POST.get("uid",""): # appel de la page avec un élève et des cours
        b=Barrette.objects.get(pk=request.POST.get("barrette"))
        barrette=b.nom
        derniereOuverture=Ouverture.objects.get(pk=request.POST.get("ouverture"))
        etudiant=Etudiant.objects.get(uid=request.POST.get("uid"))
        inscriptions=sorted([ i for i in Inscription.objects.filter(
            etudiant=etudiant,
            cours__barrette=b,
            cours__ouverture=derniereOuverture,
        ) ], key=lambda i: i.cours.horaire)
        for i in range(len(inscriptions)):
            coursConnus[i]=inscriptions[i].cours
            ## on efface l'inscription
            inscriptions[i].delete()
    else:
        barrette=request.session.get("barrette","")
        b=Barrette.objects.get(nom=barrette)
        ouvertures=Ouverture.objects.all().order_by("debut")
        derniereOuverture=ouvertures.last()
    cours=list(Cours.objects.filter(
        formation__barrette__id=b.id,
        ouverture=derniereOuverture.pk,
    ).exclude(
        enseignant__indirects__id=b.id,
    ).order_by("enseignant__nom", "horaire"))
    horaires=sorted(list(set([c.horaire for c in cours])))
    cours0=[c for c in cours if estEnPremier(c)]
    cours1=[c for c in cours if not estEnPremier(c)]
    ## calcul des non-inscrits
    eleves=set([e for e in Etudiant.objects.filter(barrette_id=b.id)])
    inscrits=set([i.etudiant for i in Inscription.objects.filter(cours__ouverture=derniereOuverture)])
    noninscrits=list(eleves-inscrits)
    noninscrits.sort(key=lambda e: e.nom)
    context={
        "autorise":    estProfesseur(request.user)=="profAP" or request.user.is_superuser,
        "estprof":    estProfesseur(request.user),
        "username":    request.user.username,
        "cours0":      cours0,
        "cours1":      cours1,
        "h0":          horaires[0],
        "h1":          horaires[1],
        "noninscrits": noninscrits,
        "etudiant":    etudiant,
        "coursConnus": coursConnus,
    }
    context.update(dicoBarrette(request))
    return render(request, "enroler.html", context)

def creeCoursParDefaut(barrette, ouverture, cours=None):
    """
    Enregistre un nouveau cours pour chaque enseignant de la barrette,
    en reprenant les formations connues lors de la formation précédente,
    quitte à en créer avec des formations par défaut. Attention, si la barrette
    est dans le champ "indirects" de l'enseignant, on ne crée pas de cours.
    @param barrette le nom d'une barette
    @param ouverture la dernière ouverture en date
    @param cours si non None, on crée un seul cours sur le modèle de celui-là
    mais pas au même horaire
    @return le nombre de cours éventuellement créés
    """
    b=Barrette.objects.get(nom=barrette)
    if cours and b not in cours.enseignant.indirects.all():
        #place le cours en premier dans l'horaire
        metEnPremier(cours)
        cours.save()
        # duplique le cours et la formation
        cours.id=None
        metEnDernier(cours)
        f=Formation.objects.get(pk=cours.formation_id, barrette__nom=barrette)
        f.id=None
        f.save()
        cours.formation_id=f.id
        cours.save()
        return 1
    nouveaux=0
    enseignants=Enseignant.objects.filter(barrettes__id=b.pk)
    for e in enseignants:
        if b in e.indirects.all():
            continue ## pas de création de cours sir le prof est indirect ici
        cours=Cours.objects.filter(enseignant=e, barrette=b, ouverture=ouverture).order_by("horaire")
        if not cours:
            coursAnciensTrouves=False
            ## on essaie d'abord de récupérer des cours donnés précédemment
            ## dans la même barrette, à l'ouvrture précédente
            try:
                precOuverture=Ouverture.objects.filter(~Q(id = ouverture.pk)).latest('debut')
                coursAnciens=Cours.objects.filter(enseignant=e, barrette=b, ouverture=precOuverture)
                if coursAnciens:
                    coursAnciensTrouves=True
                    for c in coursAnciens:
                        c.id=None # on prépare un duplicata
                        c.ouverture=ouverture
                        c.save()
                        nouveaux+=1
            except ObjectDoesNotExist:
                # il n'y a pas eu d'ouverture précédemment, on doit tout créer
                pass
            if not coursAnciensTrouves:
                h=list(Horaire.objects.filter(barrette__nom=barrette))
                c1=Cours(enseignant=e, horaire=h[0], formation=formationParDefaut(b,e), ouverture=ouverture,barrette=b)
                c2=Cours(enseignant=e, horaire=h[1], formation=formationParDefaut(b,e), ouverture=ouverture,barrette=b)
                c1.save()
                c2.save()
                nouveaux+=2
        cours=Cours.objects.filter(enseignant=e, barrette=b, ouverture=ouverture).order_by("horaire")
    return nouveaux

def formationParDefaut(b,e):
    """
    renvoie un objet formation par défaut, qu'il faut modifier
    @param b une instance de Barrette
    @param e une instance d'Enseignant
    """
    matiere="Matière"
    if e.matiere!="??":
        matiere=e.matiere
    defaultTitre="%s -- Description courte, À MODIFIER !!)" %matiere
    defaultContenu="Description longue, À MODIFIER : Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim ..."
    fs=Formation.objects.filter(titre=defaultTitre, contenu=defaultContenu, duree=1,public_designe=False,barrette=b)
    if fs:
        f= fs.last()
    else:
        f=Formation(titre=defaultTitre, contenu=defaultContenu, duree=1,public_designe=False,barrette=b)
        f.save()
    return f

def contenuMinimal(request):
    """
    Met un contenu minimal dans les formations qui n'ont été 
    renseignées par aucun professeur.
    """
    formations=Formation.objects.all()
    aModifier=[ f for f in formations if "À MODIFIER" in f.titre or "À MODIFIER" in f.contenu]
    for f in aModifier:
        try:
            matiere=f.auteur.matiere
        except:
            matiere="[Matière]"
        f.titre = "%s -- remédiation, soutien" %matiere
        f.contenu = "Ce cours convient aux élèves qui connaissent une difficulté ou ne sont pas tout à fait sûrs d'eux-mêmes."
        f.save()
    return JsonResponse({
        "message" : "%s intitulés ont été modifiés" %len(aModifier),
        "ok"      : "ok",
    })

def enroleEleveCours(request):
    """
    enrole un élève dans un cours request.POST doit contenir deux variables,
    uid et cours.
    """
    uid=request.POST.get("uid","")
    cours=request.POST.get("cours","")
    cours2=request.POST.get("cours2","")
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
                inscr=len(Inscription.objects.filter(etudiant=eleve, cours__ouverture=Ouverture.derniere()))
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

def listClasse(request):
    c=request.GET.get("classe")
    etudiants=Etudiant.objects.filter(classe=c)
    eleves=[e.nom+" "+e.prenom for e in etudiants]
    return JsonResponse({
        "eleves": "<br/>".join(eleves),
    })

def classeFromString(s):
    """
    transforme des chaînes comme "2d01 (36)" en "2d01"
    @param s chaîne d'entrée
    @return le nom d'un groupe classe
    """
    m=re.match(r"(\S+) .*",s)
    if m:
        return m.group(1)
    else:
        return s
    
def delClasse(request):
    c=classeFromString(request.GET.get("classe"))
    etudiants=Etudiant.objects.filter(classe=c)
    if etudiants:
        # on enleve la classe de la barrette
        b=etudiants[0].barrette
        b.removeClasse(c)
    etudiants.delete()
    return JsonResponse({
        "status": "ok",
    })

def delCours(request):
    c=request.GET.get("cours")
    cours=Cours.objects.filter(pk=c)
    cours.delete()
    return JsonResponse({
        "status": "ok",
    })

def classesPrises(barrettes):
    """
    Détermine les classes déjà prises quand on considère un ensemble
    de barrettes
    @param barrettes un itérable de barrettes
    @return un ensemble de classes déjà prises
    """
    return set(sum([json.loads(b.classesJSON) for b in barrettes],[]))

def addBarrette(request):
    """
    Cette page sert à la gestion des barrettes. Il faut commencer à
    vérifier le statut de l'utilisateur, et le renvoyer éventuellement vers
    une page d'erreur, ou alors lui permettre seulement de voir la liste des
    barrettes.
    """
    avertissement=""
    barrettes=list(Barrette.objects.all())
    nom=request.POST.get("nom","")
    classes=request.POST.get("selectedclasses","")
    h1=request.POST.get("h1","")
    h2=request.POST.get("h2","")
    j1=request.POST.get("j1","")
    j2=request.POST.get("j2","")
    if nom and classes:
        try:
            b=Barrette(nom=nom, classesJSON=classes)
            if set(json.loads(classes)) & classesPrises(barrettes):
                avertissement="On ne peut pas enregistrer plusieurs fois les mêmes classes"
                raise ValidationError(avertissement)
            b.save()
            Horaire(heure=h1.strip(), jour=int(j1),barrette=b).save()
            Horaire(heure=h2.strip(), jour=int(j2),barrette=b).save()
            ## changement de barrette par défaut
            request.session["barrette"]=nom
            avertissement="Nouvelle barrette : {nom}".format(nom=nom)
            barrettes.append(b)
            for c in json.loads(classes):
                inscritClasse(None, b, cn=c)
        except ValidationError as e:
            avertissement="Erreur : %s" %e.messages[0]
        except IntegrityError as e:
            avertissement="Le nom de barrette doit être unique (%s)" %e
        except Exception as e:
            avertissement="Erreur : %s" %e
    # ajoute une liste "ordinaire" des classes à chaque barrette
    for b in barrettes:
        b.l=sorted(json.loads(b.classesJSON))
    classes=sorted(list(set(lesClasses())-classesPrises(barrettes)))
    context={
        "lesBarrettes": barrettes,
        "classes" : classes,
        "avertissement" : avertissement,
    }
    context.update(dicoBarrette(request))
    return render(request, "addBarrette.html", context)

def delBarrette(request):
    """
    suppression d'une barrette
    """
    nom=request.GET.get("nom").strip()
    b=Barrette.objects.filter(nom=nom)
    b.delete()
    return JsonResponse({
        "status": "ok",
    })

def editBarrette(request):
    """
    traitement de la modification d'un barrette
    la requête contient dans le POST les variables :
    nom pour le nouveau nom de barrette
    nomOrig pour le nom d'origine
    selectedclasses pour une liste de classes à mettre dans la barrette
    """
    nom=request.POST.get("nom","")
    nomOrig=request.POST.get("nomOrig","")
    classes=request.POST.get("selectedclasses","")
    assert (nom and classes)
    b=Barrette.objects.filter(nom=nomOrig)[0]
    b.nom=nom
    b.classesJSON=classes
    b.save()
    return HttpResponseRedirect('addBarrette')

def addOuverture(request):
    """
    Cette page sert à la gestion des périodes d'AP. Il faut commencer à
    vérifier le statut de l'utilisateur, et le renvoyer éventuellement vers
    une page d'erreur, ou alors lui permettre seulement de voir la liste des
    périodes d'AP.
    """
    avertissement=""
    if not request.user.is_superuser:
        avertissement="Il faut avoir un rôle d'administrateur pour utiliser cette page."
    elif request.GET.get("editMsg",""):
        ## il y a un message d'erreur au sujet de l'édition de période d'AP
        avertissement=request.GET.get("editMsg","")
    elif "editMsg" in request.GET:
        ## édition d'une période réussie
        avertissement="La période d'AP a été modifiée."
    else:
        nom=request.POST.get("nom","")
        debut=request.POST.get("debut","")
        debut_h=request.POST.get("debut_h","")
        fin=request.POST.get("fin","")
        fin_h=request.POST.get("fin_h","")
        barrette=request.POST.get("barrette","")
        if nom and debut and debut_h and fin and fin_h and barrette:
            date_debut=datetime.strptime(debut+" "+debut_h,"%d/%m/%Y %H:%M")
            date_debut=timezone.make_aware(date_debut)
            date_fin=datetime.strptime(fin+" "+fin_h,"%d/%m/%Y %H:%M")
            date_fin=timezone.make_aware(date_fin)
            if date_fin < date_debut:
                avertissement="erreur dans le choix des dates : %s est avant %s" % (date_fin, date_debut)
            else:
                try:
                    new=Ouverture(debut=date_debut, fin=date_fin, nom_session=nom)
                    new.save()
                    avertissement="Période d'AP bien enregistrée."
                except Exception as e:
                    avertissement="Erreur: %s" %e
                    
    # cette partie vaut pour tout le monde
    barrette=request.session.get("barrette")
    ouvertures=list(Ouverture.objects.all().order_by("debut"))
    context={
        "ouvertures": ouvertures,
        "barrette" : barrette,
        "avertissement" : avertissement,
    }
    context.update(dicoBarrette(request))
    return render(request, "addOuverture.html", context)

def delOuverture(request):
    nom=request.POST.get("nom")
    barrette=request.POST.get("barrette")
    ok="ok"
    message=""
    try:
        ouverture=Ouverture.objects.filter(nom_session=nom)
        result=ouverture.delete()
    except Exception as e:
        ok="ko"
        message="Erreur : %s" %e
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })

def editOuverture(request):
    nom=request.POST.get("nom")
    cacheNom=request.POST.get("cacheNom")
    debut=request.POST.get("debut","")
    debut_h=request.POST.get("debut_h","")
    fin=request.POST.get("fin","")
    fin_h=request.POST.get("fin_h","")
    message=""
    ok="ok"
    if nom and debut and debut_h and fin and fin_h:
        date_debut=datetime.strptime(debut+" "+debut_h,"%d/%m/%Y %H:%M")
        date_debut=timezone.make_aware(date_debut)
        date_fin=datetime.strptime(fin+" "+fin_h,"%d/%m/%Y %H:%M")
        date_fin=timezone.make_aware(date_fin)
        if date_fin < date_debut:
            message="erreur dans le choix des dates : %s est avant %s" % (date_fin, date_debut)
            ok="ko"
        else:
            try:
                achanger=Ouverture.objects.get(nom_session=cacheNom)
                achanger.nom_session=nom
                achanger.debut=date_debut
                achanger.fin=date_fin
                achanger.save()
            except Exception as e:
                message="Erreur: %s" %e
                ok="ko"
    else:
        message="appel de la page editOuverture incorrect."
        ok="ko"
    return HttpResponseRedirect('addOuverture?%s' %urlencode({"editMsg":message}))
    
def editeCours(request):
    """
    édition d'un cours et de la formation associée
    """
    cours=Cours.objects.get(pk=int(request.POST.get("c_id")))
    formationCourante=Formation.objects.get(pk=cours.formation_id)
    prof=Enseignant.objects.get(pk=cours.enseignant_id)
    ## on récupère les anciennes formations, dans les cours actuels
    ## du prof, et dans les formations qu'il a détachées d'un cours
    ## suite à une édition
    anciennesFormations=set()
    for c in Cours.objects.filter(~Q(ouverture=cours.ouverture),enseignant=prof):
        anciennesFormations.add(c.formation)
    for f in Formation.objects.filter(auteur=prof):
        anciennesFormations.add(f)
    anciennesFormations-=set([formationCourante])
    ## on détermine si une formation ancienne est jetable ou non
    for af in anciennesFormations:
        coursLies=list(Cours.objects.filter(formation=af))
        ajeter=False
        if not coursLies:
            ajeter=True # formation orpheline
        else:
            coursRecents=[ c for c in coursLies if c.ouverture.estRecente()]
            ajeter= not coursRecents
        af.ajeter=ajeter # on ajoute un attribut à l'ancienne formation
    horaire=Horaire.objects.get(pk=cours.horaire_id)
    if "editeCours" in request.META["HTTP_REFERER"]:
        ## la page se rappelle elle-même, on a cliqué sur le bouton
        ## de validation donc on peut récupérer les valeurs de form
        form=editeCoursForm(request.POST, isSuperUser=request.user.is_superuser)
        if form.is_valid():
            ok=True
            ## on vérifie, pour un cours de deux heures, s'il est à la première
            ## des deux heures.
            if form.cleaned_data["duree"]==2:
                if not estEnPremier (cours):
                    ok=False
                    form.add_error("duree","Erreur : un cours de 2 heures doit commencer en début d'horaire")
            if ok: # à ce stade le cours lui-même est valide
                cours.capacite=form.cleaned_data["capacite"]
                
                if formationCourante.titre != form.cleaned_data["titre"] or \
                   formationCourante.contenu != form.cleaned_data["contenu"]:
                    # on crée une nouvelle formation dès qu'il y a une variante
                    # avant de détacher la formation du cours, on l'attache
                    # à l'enseignant, sans quoi elle devient orpheline
                    # dans la base de données
                    formationCourante.auteur_id=cours.enseignant_id
                    formationCourante.save()
                    # elle est sauvée, on la duplique
                    formationCourante.id=None
                    formationCourante.titre=form.cleaned_data["titre"]
                    formationCourante.contenu=form.cleaned_data["contenu"]
                formationCourante.duree=form.cleaned_data["duree"]
                try:
                    formationCourante.save()
                    cours.formation=formationCourante
                    cours.save()
                except Exception as e:
                    ok=False
                    message="Erreur : %s" %e
                    form.add_error(None, message)
            if ok:
                # à ce stade si duree==1, il faut vérifier le deuxième cours
                # et si duree==2, il faut supprimer le deuxième cours
                try:
                    if form.cleaned_data["duree"]==1:
                        # chercher le deuxième cours
                        deuxCours=list(Cours.objects.filter(enseignant=cours.enseignant, barrette=cours.barrette, ouverture=cours.ouverture))
                        total=0
                        for dc in deuxCours:
                            f=Formation.objects.get(pk=dc.formation_id)
                            total+=f.duree
                        assert total<=2, "Un enseignant doit faire un cours de 2 heures ou deux cours d'une heure"
                        if "v2" in request.POST:
                            # on a validé "Enregistrer pour tous les cours"
                            for dc in deuxCours:
                                if dc != cours:
                                    dc.formation=formationCourante
                                    dc.save()
                        if total<2: # un seul cours, il faut un deuxième
                            creeCoursParDefaut(cours.barrette.nom, cours.ouverture, cours=cours)
                    else:
                        # duree ==2 supprimer le deuxième cours éventuellement
                        deuxCours=list(Cours.objects.filter(enseignant=cours.enseignant, barrette=cours.barrette, ouverture=cours.ouverture))
                        if len(deuxCours) > 1:
                            # garder le cours modifié, supprimer l'autre
                            for dc in deuxCours:
                                if dc != cours:
                                    dc.delete()
                except Exception as e:
                    ok=False
                    message="Erreur : %s" %e
                    form.add_error(None, message)
            if ok:
                return HttpResponseRedirect(form.cleaned_data["back"])
            else:
                context={
                    'form': form,
                    'prof': prof,
                    'horaire': horaire,
                    "c_id": cours.id,
                    "anciennesFormations": sorted(list(anciennesFormations), key = lambda f: f.titre),
                    "estprof": estProfesseur(request.user),
                }
                context.update(dicoBarrette(request))
                return render(request, "editeCours.html", context)
                
        else: # le formulaire n'est pas validé
            context={
                'form': form,
                'prof': prof,
                'horaire': horaire,
                "c_id": cours.id,
                "anciennesFormations": sorted(list(anciennesFormations), key = lambda f: f.titre),
                "estprof": estProfesseur(request.user),
            }
            context.update(dicoBarrette(request))
            return render(request, "editeCours.html", context)
    else: ## la page est appelée directement, on n'en est pas à la validation/vérification
        cours=Cours.objects.get(pk=int(request.POST.get("c_id")))
        formationCourante=Formation.objects.get(pk=cours.formation_id)
        back=request.POST.get("back")
        prof=Enseignant.objects.get(pk=cours.enseignant_id)
        horaire=Horaire.objects.get(pk=cours.horaire_id)
        b=Barrette.objects.get(nom=request.session["barrette"])
        initial={
            "titre": formationCourante.titre,
            "contenu": formationCourante.contenuDecode,
            "duree": formationCourante.duree,
            "capacite": cours.capacite,
            "public_designe": formationCourante.public_designe,
            "public_designe_initial": formationCourante.public_designe,
            "reponse": "ok",
            "back": back,
            "is_superuser": request.user.is_superuser,
        }

        form = editeCoursForm(initial=initial)
        context={
            'form': form,
            'prof': prof,
            'horaire': horaire,
            "c_id": cours.id,
            "anciennesFormations": sorted(list(anciennesFormations), key = lambda f: f.titre),
            "estprof": estProfesseur(request.user),
        }
        context.update(dicoBarrette(request))
        return render(request, "editeCours.html", context)

def delFormation(request):
    formation_id=int(request.POST.get("formation_id"))
    ok="ok"
    message=""
    try:
        formation=Formation.objects.get(pk=formation_id)
        result=formation.delete()
    except Exception as e:
        ok="ko"
        message="Erreur : %s" %e
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })


def desinscrire(request):
    """
    permet à l'administrateur de désinscrire en masse des élèves, sauf
    pour quelques cours "sanctuarisés". Un cours est sanctuatrisé si on le
    dir, ou si c'est un cours à public désigné. Attention, les élèves
    sont maintenus dans l'autre cours (non sanctuarisé) si un de leurs
    cours est sanctuarisé
    """
    barrette=request.session.get("barrette")
    b=Barrette.objects.get(nom=barrette)
    eleves=Etudiant.objects.filter(barrette=b)
    for e in eleves:
        inscriptions=Inscription.objects.filter(etudiant=e)
        e.ins=[]
        e.desinscrire=True
        for i in inscriptions:
            e.ins.append(i)
            if i.cours.formation.public_designe:
                e.desinscrire=False
    # on ne garde que les élèves à désinscrire
    eleves=[e for e in eleves if e.desinscrire]
    desinscrire=""
    if request.GET.get("ok",""):
        for e in eleves:
            for i in e.ins:
                i.delete()
        desinscrire="Ces %d élèves ont été désinscrits" %len(eleves)
    context={
        "barrette": barrette,
        "eleves" : eleves,
        "desinscrire": desinscrire,
    }
    context.update(dicoBarrette(request))
    return render(request, "desinscrire.html", context)

def majElevesKwartz(request):
    """
    prend en compte le paramètre barrette, puis trouve toutes les classes
    associées à cette barrette ; retire les élèves de la barrette si ceux-ci
    ne sont plus associés à une classe de la barrette, puis reprend les élèves
    de la barrette, corrige leur classe, enfin inscrit ceux des élèves qui
    n'étaient pas encore dans la barrette.
    Si ce paramètre vaut "all", toutes les barrettes seront mises à jour
    @param request, qui fournit request.GET.get("barrette")
    """
    if request.GET.get("barrette","")=="all":
        barrettes=Barrette.objects.all()
        nomsBarrettes=[]
        for b in barrettes:
            nomsBarrettes.append(b.nom)
            majElevesKwartz1(b.nom)
        return JsonResponse({
            "message" : "mise à jour tentée pour les barrettes %s" %
              ",".join(nomsBarrettes),
            "ok"      : "ok",
        })
    else:
        b=request.GET.get("barrette","")
        return majElevesKwartz1(b)
        
def majElevesKwartz1(barrette):
    """
    sous-programme de la fonction majElevesKwartz
    @param barrette un nom de barrette
    @return une réponse JSON
    """
    if barrette:
        b=Barrette.objects.get(nom=barrette)
        eleves=Etudiant.objects.filter(barrette=b)
        classes={}
        for e in eleves:
            if e.classe in classes:
                classes[e.classe] += 1
            else:
                classes[e.classe]=1
        # on ne conserve que les classes de plus de 5 élèves, au cas où il
        # y aurait eu des changements de groupe de certains élèves qui les
        # sortent du champ de la barrette
        classes={ c : classes[c] for c in classes if classes[c]>5}
        # on reprend les listes de classes plus récentes selon Kwartz
        classesKwartz={}
        for c in classes:
            classesKwartz[c]=etudiantsDeClasse(c)
        # on supprime les élèves qui seraient sortis du Kwartz
        for e in eleves:
            found=False
            for c in classesKwartz:
                if e.uid in classesKwartz[c]:
                    found=True
            if not found:
                e.delete()
        # on inscrit les nouveaux élèves et on rectifie les anciens
        for c in classes:
            inscritClasse(None, b, c)
        return JsonResponse({
            "message" : "mise à jour OK",
            "ok"      : "ok",
        })
    else:
        return JsonResponse({
            "message" : "mise à jour impossible",
            "ok"      : "nok",
        })
    
def reinscription(request):
    """
    réinscrit un groupe d'élèves comme dans la période précédente
    ce qui est utile pour les formations à public désigné
    request.POST contient les arguments cours_id et ouverture_id
    """
    cours_id=int(request.POST.get("cours_id"))
    cours=Cours.objects.get(pk=cours_id)
    ouverture_id=int(request.POST.get("ouverture_id"))
    derniere=Ouverture.objects.get(pk=ouverture_id)
    avantDerniere=Ouverture.justeAvant(derniere)
    coursAvant=Cours.objects.filter(formation=cours.formation, ouverture=avantDerniere)
    if not coursAvant:
        return JsonResponse({
            "message" : "Pas de cours identique lors de la session précédente",
            "ok"      : "nok",
        })
    # récupération des élèves inscrits précédemment
    inscriptions=Inscription.objects.filter(cours=coursAvant[0])
    eleves=[]
    for i in inscriptions:
        eleves.append(i.etudiant)
        i.pk=None # pour dupliquer l'inscription
        i.cours=cours
        i.save()
    if cours.formation.duree < 2:
        for e in eleves:
            # on s'assure que l'élève e est bien inscrit pour deux heures.
            try:
                exInscription=Inscription.objects.get(
                    ~Q(cours=coursAvant),
                    etudiant=e,
                    cours__ouverture=avantDerniere
                )
            except ObjectDoesNotExist:
                return JsonResponse({
                    "message" : "une des inscriptions est ratée",
                    "ok"      : "nok",
                })
            autreCours=Cours.objects.filter(
                ~Q(horaire=cours.horaire), # pas à la même heure que le cours
                formation=exInscription.cours.formation, # même formation
                ouverture=derniere,                      # maintenant
            )
            if not autreCours:
                # ça ne marche pas avec exactement la même formation
                # on essaie avec le même prof
                autreCours=Cours.objects.filter(
                    ~Q(horaire=cours.horaire), # pas à la même heure
                    enseignant=exInscription.cours.enseignant, # même enseignant
                    ouverture=derniere,                      # maintenant
                )
                
            autreCours=autreCours[0]
            exInscription.pk=None # pour une duplication
            exInscription.cours=autreCours
            exInscription.save()
    return JsonResponse({
        "message" : "Réinscription terminée ({} élèves)".format(len(inscriptions)),
        "ok"      : "ok",
    })

def addUnProf(request):
    """
    fonction de rappel pour inscrire un prof
    @return une réponse JSON
    """

    message, ok = addUnProfLdap(request)
    return JsonResponse({
        "message" : message,
        "ok"      : ok,
    })

def addEleves(request):
    """
    Une page pour ajouter des élèves à une barrette d'AP
    """
    context=addElevesLdap(request)
    context.update(dicoBarrette(request))
    return render(request, "addEleves.html", context)
    
