"""
Implémentation de l'export CSV des résultats d'une "barrette" d'AP
"""

import csv
from django.utils import timezone
from django.http import HttpResponse
from .models import rdvOrientation

def csvResponse(inscriptions, noninscrits):
    """
    fabrique un objet de type HttpResponse avec les données qui vont bien
    @param inscriptions un objet issu de Inscription.objects.all()
    @param noninscrits une liste d'Etudiants
    @return un objet de type HttpResponse
    """
    response = HttpResponse(content_type='text/csv')
    now=timezone.now()
    filename="aperho-{}.csv".format(now.strftime("%Y%m%d-%H%M"))
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    writer = csv.writer(response)
    writer.writerow(['id', 'Eleve_nom', 'Eleve_prenom', 'Eleve_classe', 'Professeur', 'Salle', 'Heure', 'Duree', 'Public_designe', 'Resume','Detail','Autres'])
    for i in inscriptions:
        writer.writerow([i.pk, i.etudiant.nom, i.etudiant.prenom, i.etudiant.classe, i.cours.enseignant.nom, i.cours.enseignant.salle, i.cours.horaire, i.cours.formation.duree, i.cours.formation.public_designe, i.cours.formation.titre, i.cours.formation.contenu, rdvOrientation(i)])
    for e in noninscrits:
        writer.writerow([0, e.nom, e.prenom, e.classe, '', '', '', '', '', '', '',''])
    return response
