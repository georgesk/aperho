from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import *

from votes.models import Cours, Inscription

def index_admin(request):
    return render(request, "home_admin.html")

def index(request):
    if request.user.is_authenticated():
        cours=list(Cours.objects.all())
        ## On enrichit les cours avec le remplissage actuel de chacun
        for c in cours:
            inscriptions=Inscription.objects.filter(cours=c)
            c.inscriptions=[i.etudiant for i in inscriptions]
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
            }
        )
    else:
        return HttpResponseRedirect("/login/")

