from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

from votes.models import Cours, Inscription, Etudiant, Enseignant
from votes.models import estProfesseur

def index_admin(request):
    return render(request, "home_admin.html")

            
    

def index(request):
    if request.user.is_authenticated():
        cours=list(Cours.objects.all().order_by("formation__titre"))
        cours=[c for c in cours if c.estOuvert()]
        ## On enrichit les cours avec le remplissage actuel de chacun
        ## Et on décide si on doit désactiver la modification de ce cours
        for c in cours:
            inscriptions=Inscription.objects.filter(cours=c)
            ## liste des étudiants inscrits dans le cours
            c.inscriptions=[i.etudiant for i in inscriptions]
            ## on désactive le cours s'il est à public désigné ou s'il est plein
            ## et que l'étudiant n'y est pas déjà inscrit
            c.disabled=c.formation.public_designe or (len(c.inscriptions) >= c.capacite and request.user.username not in [e.uid for e in c.inscriptions])
        cours_suivis=[]
        etudiants=list(Etudiant.objects.filter(uid=request.user.username))
        etudiant=None
        if etudiants:
            ## on a affaire à un étudiant, qui est etudiants[0]
            etudiant=etudiants[0]
            cours_suivis=[i.cours for i in Inscription.objects.filter(etudiant=etudiant)]
        ## on s'assure qu'il y a bien deux horaires, pas plus, pas moins
        horaires=sorted(list(set([str(c.horaire) for c in cours])))
        while len(horaires) < 2:
            horaires.append("remplissage_{}".format(len(horaires)))
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
                        "horaire": horaires[0][:5]
                    },
                    {
                        "cours": [c for c in cours
                                  if str(c.horaire)==horaires[1]],
                        "horaire": horaires[1][:5]
                    },
                ],
                "horaires" : horaires,
                "etudiant" : etudiant,
                "cours_suivis" : cours_suivis,
                "estprof": estProfesseur(request.user),
                "username": request.user.username,
            }
        )
    else:
        return HttpResponseRedirect("/login/")

