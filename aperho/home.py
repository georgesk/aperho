from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

import json

from votes.models import Cours, Inscription, Etudiant, Enseignant, \
    Orientation, Horaire, estProfesseur, barrettesPourUtilisateur, \
    Barrette

def index(request):
    if request.user.is_authenticated():
        #########################################################
        #   GESTION DE LA BARRETTE COURANTE POUR LA SESSION     #
        #########################################################
        initScript="" # script à insérer dans home.html
        bpu=barrettesPourUtilisateur(request.user)
        if len(bpu)==1:
            request.session["barrette"]=bpu[0].nom
        nomsBarrettes=[str(b.nom) for b in bpu]
        nouvelleBarrette=request.GET.get("nouvelleBarrette","")
        if nouvelleBarrette in nomsBarrettes:
            request.session["barrette"]=nouvelleBarrette
        barretteCourante=request.session.get("barrette","")
        actionChangeBarrette="" # code HTML pour une ligne de menu
        if len(bpu)>1:
            # on donne un menu pour changer de barrette
            actionChangeBarrette=""" <li><a href='javascript:changebarrette(%s,%s)'>Changer de barrette</a></li>"""%(json.dumps(nomsBarrettes),nomsBarrettes.index(barretteCourante) if barretteCourante in nomsBarrettes else "undef")
        if not barretteCourante:
            if not bpu:
                print("L'impossible est arrivé ? un utilisateur sans barrette connue")
            else:
                # par défaut, la première barrette est activée
                request.session["barrette"]=bpu[0].nom
                # mais on propose de changer de barrette s'il y en plusieurs
                if len(bpu) > 1:
                    initScript=""" $(function(){changebarrette(%s,%d)});""" %(json.dumps(nomsBarrettes),0)
        #########################################################
        # GESTION DES COURS À AFFICHER, DANS LA BARRETTE        #
        #########################################################
        try:
            b=Barrette.objects.get(nom=barretteCourante)
            cours=list(Cours.objects.filter(
                barrette=b,                     # cours dans la barrette
                enseignant__barrettes__id=b.pk  # et enseignant aussi
            ).order_by("formation__titre"))     # par orde de titres
        except:
            cours=[]
        choix=Orientation._meta.get_field("choix")
        orientations=[{"val": c[0], "label": c[1],} for c in choix.choices]
        # orientationOuverte est un booléen ; pour le forcer à vrai
        # il suffit qu'il y ait au moins un object Orientation avec
        # la bonne date d'ouverture, même si les autres champs sont par défaut.
        orientationOuverte=len([o for o in Orientation.objects.all() if o.ouverture.estActive()]) > 0
        if request.user.is_superuser or "profAP"==estProfesseur(request.user):
            cours=[c for c in cours if c.estRecent()]
        else:
            cours=[c for c in cours if c.estOuvert()]
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
                "estprof": estProfesseur(request.user),
                "username": request.user.username,
            }
        )
    else:
        return HttpResponseRedirect("/login/")

