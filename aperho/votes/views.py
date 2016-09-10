from django.shortcuts import render
from django.http import HttpResponse

from aperho.settings import connection
from .models import Etudiant

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
                etudiant=Etudiant(uid=e["uid"], nom=e["nom"], prenom=e["prenom"])
                etudiant.save()
    base_dn = 'ou=Groups,dc=lycee,dc=jb'
    filtre = '(&(|(cn=prof*)(&(cn=c*)(!(cn=*smbadm))))(objectclass=kwartzGroup))'
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
    return render(
        request, "addEleves.html",
        context={
            "classes": classes,
            "eleves":  eleves,
        }
    )
