from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

import json

from votes.models import Cours, Inscription, Etudiant, Enseignant, \
    Orientation, Horaire, estProfesseur, barrettesPourUtilisateur, \
    Barrette, Ouverture

def choixBarrette(request):
    """
    Prend une barrette de façon pertinente : s'il n'y en a qu'une ce sera
    celle-là, sinon on propose de choisir avant toute autre chose.
    @param request une requête
    @return la liste de barrettes possibles, 
    une ligne de code HTML pour le menu, et un peu de code Javascript
    pour lancer un dialogue.
    """
    initScript="" # script à insérer dans home.html
    bpu=barrettesPourUtilisateur(request.user)
    if len(bpu)==1: # une seule barrette, on la choisit
        request.session["barrette"]=bpu[0].nom
        
        actionChangeBarrette="<!-- barrette unique -->"
    else: # plusieurs barrette, on voit si l'une d'entre elles a été demandée
        nomsBarrettes=[str(b.nom) for b in bpu]
        nouvelleBarrette=request.GET.get("nouvelleBarrette","")
        if nouvelleBarrette in nomsBarrettes:
            request.session["barrette"]=nouvelleBarrette
        barretteCourante=request.session.get("barrette","")
        actionChangeBarrette="""<li><a href='javascript:changebarrette(%s,%s)'>Changer de barrette</a></li>"""%(json.dumps(nomsBarrettes),nomsBarrettes.index(barretteCourante) if barretteCourante in nomsBarrettes else "undef")
        if not barretteCourante:
            # par défaut, la première barrette est activée
            request.session["barrette"]=bpu[0].nom
            # mais on propose de changer de barrette s'il y en plusieurs
            initScript=""" $(function(){changebarrette(%s,%d)});""" %(json.dumps(nomsBarrettes),0)
    return bpu, actionChangeBarrette, initScript

def coursAModifier(request, cours):
    """
    Liste des cours qui n'ont probablement pas été mis à jour
    et qui concernent un prof d'AP
    """
    if "profAP"==estProfesseur(request.user):
        return[c for c in cours
               if not c.invalide and
               c.enseignant.nom == request.user.last_name and
               ("MODIFIER" in c.formation.contenu or
                "MODIFIER" in c.formation.titre)]
    else:
        return []

def coursDeBarretteCourante(request):
    """
    @return une liste de cours de la barrette courante
    """
    barretteNom=request.session.get("barrette")
    if not barretteNom:
        return []
    b=Barrette.objects.get(nom=barretteNom)
    return list(Cours.objects.filter(
        barrette=b,                     # cours dans la barrette,
        enseignant__barrettes__id=b.pk, # et enseignant aussi.
        invalide=False,                 # cours non invalide
    ).order_by("formation__titre"))     # triés par orde de titres
    
    
def index(request):
    if request.user.is_authenticated():
        #########################################################
        #   GESTION DE LA BARRETTE COURANTE POUR LA SESSION     #
        #########################################################
        bpu, actionChangeBarrette,initScript = choixBarrette(request)
        if len(bpu)==1: # une seule barrette, on la choisit
            barretteCourante=bpu[0].nom
        else:
            barretteCourante=request.GET.get("nouvelleBarrette","")
        #########################################################
        # GESTION DES COURS À AFFICHER, DANS LA BARRETTE        #
        #########################################################
        cours=coursDeBarretteCourante(request)
        choix=Orientation._meta.get_field("choix")
        orientations=[{"val": c[0], "label": c[1],} for c in choix.choices]
        # orientationOuverte est un booléen ; pour le forcer à vrai
        # il suffit qu'il y ait au moins un object Orientation avec
        # la bonne date d'ouverture, même si les autres champs sont par défaut.
        orientationOuverte=len([o for o in Orientation.objects.all() if o.ouverture.estActive()]) > 0
        if request.user.is_superuser or "profAP"==estProfesseur(request.user):
            cours=[c for c in cours if c.estRecent]
        else:
            cours=[c for c in cours if c.estOuvert]
        coursAchanger=coursAModifier(request, cours)
        capacite={} # tableau heure -> nombre d'élèves accueillis
        heures=[h.hm for h in Horaire.objects.all()]
        for h in heures:
            capacite[h]=0
        ## On enrichit les cours avec le remplissage actuel de chacun
        ## Et on décide si on doit désactiver la modification de ce cours
        ## au passage, on met à jour les capacités d'accueil des élèves
        for c in cours:
            inscriptions=Inscription.objects.filter(cours=c)
            ## liste des étudiants inscrits dans le cours
            c.inscriptions=[i.etudiant for i in inscriptions]
            ## on désactive le cours s'il est à public désigné ou s'il est plein
            ## et que l'étudiant n'y est pas déjà inscrit
            c.disabled=c.formation.public_designe or (len(c.inscriptions) >= c.capacite and request.user.username not in [e.uid for e in c.inscriptions])
            ## mise à jour des capacités :
            if c.formation.duree == 2:
                for h in heures:
                    capacite[h]+=c.capacite
            else:
                capacite[c.horaire.hm]+=c.capacite
        cours_suivis=[]
        orientations_demandees=[]
        etudiants=list(Etudiant.objects.filter(uid=request.user.username))
        etudiant=None
        if etudiants:
            ## on a affaire à un étudiant, qui est etudiants[0]
            etudiant=etudiants[0]
            cours_suivis=[i.cours for i in Inscription.objects.filter(etudiant=etudiant)]
            orientations_demandees = [o.choix for o in Orientation.objects.filter(etudiant=etudiant) if o.estOuvert()]
            
        ## on s'assure qu'il y a bien deux horaires, pas plus, pas moins
        horaires=sorted(list(set([c.horaire for c in cours])))
        if len(horaires)==2:
            h0=horaires[0].hm
            h1=horaires[1].hm
        else:
            while len(horaires) < 2:
                hi="remplissage_{}".format(len(horaires))
                horaires.append(hi)
                capacite[hi]="??"
            h0=horaires[0]
            h1=horaires[1]
        c0=capacite[h0]
        c1=capacite[h1]
        assert len(horaires)==2
        
        ## on sépare les cours selon les deux horaires
        tousLesCours=[
            {
                "cours": [c for c in cours if c.horaire==horaires[0]],
                "horaire": h0,
                "capacite" : c0,
            },
            {
                "cours": [c for c in cours if c.horaire==horaires[1]],
                "horaire": h1,
                "capacite" : c1,
            },
        ]
        od=Ouverture.derniere()
        if od:
            ouverte=od.estActive()
        else:
            ouverte=False
        return render(
            request,
            "home.html",
            {
                "initScript": initScript,
                "barrette": barretteCourante,
                "actionChangeBarrette": actionChangeBarrette,
                "tousLesCours": tousLesCours,
                "horaires" : horaires,
                "etudiant" : etudiant,
                "cours_suivis" : cours_suivis,
                "orientations_demandees": orientations_demandees,
                "orientations" : orientations,
                "orientationOuverte" : orientationOuverte,
                "od": od,
                "ouverte": ouverte,
                "estprof": estProfesseur(request.user),
                "username": request.user.username,
                "coursAchanger": coursAchanger,
            }
        )
    else:
        return HttpResponseRedirect("/login/")

