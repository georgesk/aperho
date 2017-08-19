from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

from votes.models import Cours, Inscription, Etudiant, Enseignant, \
    Orientation, Horaire, estProfesseur, barrettesPourUtilisateur

def index(request):
    if request.user.is_authenticated():
        bpu=barrettesPourUtilisateur(request.user)
        print("GRRRR1", request.session.get("barrette","barrette inconnue"))
        if not request.session.get("barrette",""):
            if len(bpu)==1:
                request.session["barrette"]=bpu[0].nom
            elif len(bpu) > 1:
                print("GRRRRR on choisira une des barrettes pour la session parmi", bpu)
                """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
     À faire : appeler une page autre que home.html, avec
     un formulaire pour sélectionner une des barrettes possibles
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                """
            else:
                print("L'impossible est arrivé ? un utilisateur sans barrette connue")
        print("GRRRR2", request.session.get("barrette","barrette inconnue"))
        cours=list(Cours.objects.all().order_by("formation__titre"))
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
        heures=[str(h.heure)[:5] for h in Horaire.objects.all()]
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
                capacite[str(c.horaire.heure)[:5]]+=c.capacite
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
        horaires=sorted(list(set([str(c.horaire) for c in cours])))
        while len(horaires) < 2:
            horaires.append("remplissage_{}".format(len(horaires)))
            capacite["rempl"]="??" # au cas où on aurait rempli quelque chose
        assert len(horaires)==2
        ## on sépare les cours selon les deux horaires
        return render(
            request,
            "home.html",
            {
                "tousLesCours": [
                    {
                        "cours": [c for c in cours
                                  if str(c.horaire)==horaires[0]],
                        "horaire": horaires[0][:5],
                        "capacite" : capacite[horaires[0][:5]]
                    },
                    {
                        "cours": [c for c in cours
                                  if str(c.horaire)==horaires[1]],
                        "horaire": horaires[1][:5],
                        "capacite" : capacite[horaires[1][:5]]
                    },
                ],
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

