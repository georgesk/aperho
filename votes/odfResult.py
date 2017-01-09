"""
Implémentation de l'export ODF des résultats d'une "barrette" d'AP
"""

from django.utils import timezone
from django.utils.timezone import localtime
from django.http import HttpResponse

from odf.opendocument import OpenDocumentSpreadsheet, OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties, ListLevelProperties
from odf.text import P, H, List, ListItem, ListStyle, ListLevelStyleBullet, Page
from odf.table import Table, TableColumn, TableRow, TableCell
from io import BytesIO
from .models import rdvOrientation, Orientation, Ouverture

def odsResponse(inscriptions, noninscrits):
    """
    fabrique un objet de type HttpResponse qui comporte un tableur au format
    ODS, avec les exportations d'une "barrette" d'AP.    
    @param inscriptions un objet issu de Inscription.objects.all()
    @param noninscrits une liste d'Etudiants
    @return un objet de type HttpResponse
    """
    response = HttpResponse(content_type='application/vnd.oasis.opendocument.spreadsheet')
    now=timezone.now()
    filename="aperho-{}.ods".format(now.strftime("%Y%m%d-%H%M"))
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    doc = OpenDocumentSpreadsheet()
    # Create a style for the table content. One we can modify
    # later in the word processor.
    tablecontents = Style(name="Table Contents", family="paragraph")
    tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
    tablecontents.addElement(TextProperties(fontweight="bold"))
    doc.styles.addElement(tablecontents)

    # Create automatic styles for the column widths.
    # We want two different widths, one in inches, the other one in metric.
    # ODF Standard section 15.9.1
    widthshort = Style(name="Wshort", family="table-column")
    widthshort.addElement(TableColumnProperties(columnwidth="1.7cm"))
    doc.automaticstyles.addElement(widthshort)

    widthwide = Style(name="Wwide", family="table-column")
    widthwide.addElement(TableColumnProperties(columnwidth="1.5in"))
    doc.automaticstyles.addElement(widthwide)

    # Start the table, and describe the columns
    table = Table(name="Inscriptions")
    table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=widthwide))
    tr = TableRow()
    table.addElement(tr)
    for title in ['id', 'Eleve_nom', 'Eleve_prenom', 'Eleve_classe', 'Professeur', 'Salle', 'Heure', 'Duree', 'Public_designe', 'Resume','Detail','Autres']:
        tc = TableCell()
        tr.addElement(tc)
        p = P(stylename=tablecontents,text=title)
        tc.addElement(p)
    for i in inscriptions:
        tr = TableRow()
        table.addElement(tr)
        for val in [i.pk, i.etudiant.nom, i.etudiant.prenom, i.etudiant.classe, i.cours.enseignant.nom, i.cours.enseignant.salle, i.cours.horaire, i.cours.formation.duree, i.cours.formation.public_designe, i.cours.formation.titre, i.cours.formation.contenu]:
            tc = TableCell()
            tr.addElement(tc)
            p = P(stylename=tablecontents,text=str(val))
            tc.addElement(p)
        ## write something in the last column (Autres)
        tc = TableCell()
        tr.addElement(tc)
        p = P(stylename=tablecontents,text=rdvOrientation(i))
        tc.addElement(p)
    for e in noninscrits:
        tr = TableRow()
        table.addElement(tr)
        for val in [0, e.nom, e.prenom, e.classe, '', '', '', '', '', '', '','']:
            tc = TableCell()
            tr.addElement(tc)
            p = P(stylename=tablecontents,text=str(val))
            tc.addElement(p)
    doc.spreadsheet.addElement(table)
    output=BytesIO()
    doc.save(output)
    response.write(output.getvalue())
    return response

def odtResponse(eci, horaires, noninscrits, cci=None):
    """
    fabrique un objet de type HttpResponse qui comporte un tableur au format
    ODT, avec les exportations d'une "barrette" d'AP.
    @param eci un dictionnaire de dictionnaires enseignant => cours => inscriptions
    @param horaires les horaires existant dans la "barrette"
    @param noninscrits une liste d'Etudiants
    @param cci dictionnaire cop -> coursOrientation -> inscriptionOrientations
    @return un objet de type HttpResponse
    """
    ## détermine d'abord s'il y a des séances d'orientation, pour la dernière
    ## ouverture en date. yaCop est un booléen vrai si les COP interviennent.
    yaCop=len(Orientation.objects.filter(
        ouverture=Ouverture.objects.last()
    )) > 0
    response = HttpResponse(content_type='application/vnd.oasis.opendocument.text')
    now=timezone.now()
    filename="aperho-{}.odt".format(now.strftime("%Y%m%d-%H%M"))
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    textdoc = OpenDocumentText()

    tablecontents = Style(name="Table Contents", family="paragraph")
    tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
    tablecontents.addElement(TextProperties(fontweight="bold"))
    textdoc.styles.addElement(tablecontents)

    w=[] # styles de largeurs de colonnes
    w1 = Style(name="Wwide1", family="table-column")
    w1.addElement(TableColumnProperties(columnwidth="0.5in"))
    textdoc.automaticstyles.addElement(w1)
    w.append(w1)
    w2 = Style(name="Wwide2", family="table-column")
    w2.addElement(TableColumnProperties(columnwidth="2in"))
    textdoc.automaticstyles.addElement(w2)
    w.append(w2)
    w3 = Style(name="Wwide3", family="table-column")
    w3.addElement(TableColumnProperties(columnwidth="1.5in"))
    textdoc.automaticstyles.addElement(w3)
    w.append(w3)
    w4 = Style(name="Wwide4", family="table-column")
    w4.addElement(TableColumnProperties(columnwidth="1in"))
    textdoc.automaticstyles.addElement(w4)
    w.append(w4)
    w5 = Style(name="Wwide5", family="table-column")
    w5.addElement(TableColumnProperties(columnwidth="4in"))
    textdoc.automaticstyles.addElement(w5)
    w.append(w5)

    withbreak = Style(name="WithBreak", parentstylename="Standard", family="paragraph")
    withbreak.addElement(ParagraphProperties(breakbefore="page"))
    textdoc.automaticstyles.addElement(withbreak)

    for e,ci in eci.items():
        # e est un enseignant, ci est un dictionnaire
        p = P(stylename=withbreak,text="") # saut de page manuel
        textdoc.text.addElement(p)
        for c,inscriptions in ci.items():
            titre="{} {} ({}, {}h, {})".format(c.horaire, c.enseignant.nom, c.enseignant.salle, c.formation.duree, c.formation.titre)
            textdoc.text.addElement(H(text=titre, outlinelevel=1))
            ### on début un tableau n°, Nom, prénom, classe pour les élèves
            table = Table()
            nbCol=4
            if yaCop:
                nbCol=5
            for i in range(nbCol):
                table.addElement(TableColumn(stylename=w[i]))
            textdoc.text.addElement(table)
            n=1
            tr = TableRow()
            table.addElement(tr)
            colTitres=("n°","Nom","Prénom","Classe")
            if yaCop:
                colTitres=("n°","Nom","Prénom","Classe", "Séance COP")
            for val in colTitres:
                tc = TableCell()
                tr.addElement(tc)
                p = P(stylename=tablecontents,text=str(val))
                tc.addElement(p)
            for i in inscriptions:
                tr = TableRow()
                table.addElement(tr)
                for val in [n, i.etudiant.nom, i.etudiant.prenom, i.etudiant.classe]:
                    tc = TableCell()
                    tr.addElement(tc)
                    p = P(text=val)
                    tc.addElement(p)
                if yaCop:
                    tc = TableCell()
                    tr.addElement(tc)
                    p = P(text=rdvOrientation(i))
                    tc.addElement(p)                    
                n+=1
        #après chaque enseignant, on passe une page.

    p = P(stylename=withbreak,text="") # saut de page manuel
    textdoc.text.addElement(p)
    titre="Élèves non encore inscrits"
    textdoc.text.addElement(H(text=titre, outlinelevel=1))
    ni=list(noninscrits)
    ni.sort(key=lambda e: (e.classe, e.nom, e.prenom))
    for e in ni:
        ligne="{} {} {}".format(e.classe, e.nom, e.prenom)
        textdoc.text.addElement(P(text=ligne))

    if cci:
        for cop, ci in cci.items():
            titre="Conseillère d'orientation : {}".format(cop.nom)
            for cours, inscr in ci.items():
                p = P(stylename=withbreak,text="") # saut de page manuel
                textdoc.text.addElement(p)
                textdoc.text.addElement(H(text=titre, outlinelevel=1))
                titre2="{} {} avec {}".format(localtime(cours.debut).strftime("%d/%m/%Y %H%M"), cours.choice, cours.prof)
                textdoc.text.addElement(H(text=titre2, outlinelevel=2))
                ### on débute un tableau n°, Nom, prénom, classe pour les élèves
                table = Table()
                nbCol=4
                for i in range(nbCol):
                    table.addElement(TableColumn(stylename=w[i]))
                textdoc.text.addElement(table)
                tr = TableRow()
                table.addElement(tr)
                colTitres=("n°","Nom","Prénom","Classe")
                for val in colTitres:
                    tc = TableCell()
                    tr.addElement(tc)
                    p = P(stylename=tablecontents,text=str(val))
                    tc.addElement(p)
                ### compteur d'élèves au minimum ...
                n=1
                ### puis on ajoute une ligne par inscription
                for i in inscr:
                    tr = TableRow()
                    table.addElement(tr)
                    for val in [n, i.etudiant.nom, i.etudiant.prenom, i.etudiant.classe]:
                        tc = TableCell()
                        tr.addElement(tc)
                        p = P(text=val)
                        tc.addElement(p)
                    n+=1
        
    output=BytesIO()
    textdoc.save(output)
    response.write(output.getvalue())
    return response
