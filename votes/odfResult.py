"""
Implémentation de l'export ODF des résultats d'une "barrette" d'AP
"""

from django.utils import timezone
from django.http import HttpResponse

from odf.opendocument import OpenDocumentSpreadsheet, OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableColumnProperties, ListLevelProperties
from odf.text import P, H, List, ListItem, ListStyle, ListLevelStyleBullet, SoftPageBreak
from odf.table import Table, TableColumn, TableRow, TableCell
from io import BytesIO

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
    #table.addElement(TableColumn(numbercolumnsrepeated=4,stylename=widthshort))
    table.addElement(TableColumn(numbercolumnsrepeated=3,stylename=widthwide))
    tr = TableRow()
    table.addElement(tr)
    for title in ['id', 'Eleve_nom', 'Eleve_prenom', 'Eleve_classe', 'Professeur', 'Salle', 'Heure', 'Duree', 'Public_designe', 'Resume','Detail']:
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
    for e in noninscrits:
        tr = TableRow()
        table.addElement(tr)
        for val in [0, e.nom, e.prenom, e.classe, '', '', '', '', '', '', '']:
            tc = TableCell()
            tr.addElement(tc)
            p = P(stylename=tablecontents,text=str(val))
            tc.addElement(p)
    doc.spreadsheet.addElement(table)
    output=BytesIO()
    doc.save(output)
    response.write(output.getvalue())
    return response

def odtResponse(eci, horaires, noninscrits):
    """
    fabrique un objet de type HttpResponse qui comporte un tableur au format
    ODT, avec les exportations d'une "barrette" d'AP.
    @param eci un dictionnaire de dictionnaires enseignant => cours => inscriptions
    @param horaires les horaires existant dans la "barrette"
    @param noninscrits une liste d'Etudiants
    @return un objet de type HttpResponse
    """
    response = HttpResponse(content_type='application/vnd.oasis.opendocument.text')
    now=timezone.now()
    filename="aperho-{}.odt".format(now.strftime("%Y%m%d-%H%M"))
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    textdoc = OpenDocumentText()
    textdoc.text.setAttribute('usesoftpagebreaks', 1)
    tablecontents = Style(name="Table Contents", family="paragraph")
    tablecontents.addElement(ParagraphProperties(numberlines="false", linenumber="0"))
    tablecontents.addElement(TextProperties(fontweight="bold"))
    textdoc.styles.addElement(tablecontents)

    widthwide = Style(name="Wwide", family="table-column")
    widthwide.addElement(TableColumnProperties(columnwidth="1.5in"))
    textdoc.automaticstyles.addElement(widthwide)

    """
    l = List(stylename=listhier)
    textdoc.text.addElement(l)
    for x in [1,2,3,4]:
        elem = ListItem()
        elem.addElement(P(text="Listitem %d" % x))
        l.addElement(elem)
    """
    for e,ci in eci.items():
        # e est un enseignant, ci est un dictionnaire
        for c,inscriptions in ci.items():
            titre="{} {} ({})".format(c.horaire, c.enseignant.nom, c.enseignant.salle)
            textdoc.text.addElement((H(text=titre, outlinelevel=1)))
            ### on début un tableau n°, Nom, prénom, classe pour les élèves
            table = Table()
            table.addElement(TableColumn(numbercolumnsrepeated=4,stylename=widthwide))
            textdoc.text.addElement(table)
            n=1
            tr = TableRow()
            table.addElement(tr)
            for val in ("n°","Nom","Prénom","Classe"):
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
                n+=1
        #après chaque enseignant, on passe une page.
        sautDePage=SoftPageBreak()
        textdoc.text.addElement(sautDePage)
    output=BytesIO()
    textdoc.save(output)
    response.write(output.getvalue())
    return response
