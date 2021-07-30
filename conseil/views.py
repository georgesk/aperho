from django.shortcuts import render, HttpResponse

import collections, io, json, tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from conseil.utils.readBulletin import *
from aperho.settings import TMP_CONSEIL_DIR

def protect(fieldname):
    return fieldname.replace(" ", "_").replace(".","_")

def csv2fields_and_data(csvfile):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @return une liste d'en-têtes, une liste d'en-têtes uniques avec les
            colonnes qui les concernent, puis une liste de lignes de données,
            et une liste de lignes de données augmentée de données résumées
            pour les en-têtes couvrant plus d'une colonne.
    """
    h1 = csvfile.readline().strip().split(";")
    h2 = csvfile.readline().strip().split(";")
    fieldnames = [ protect(f) for f in h2[:3] + h1[3:]]
    uniqueFields = collections.OrderedDict()
    for i,f in enumerate(fieldnames):
        if f in uniqueFields:
            uniqueFields[f].append(i)
        else:
            uniqueFields[f] = [i]
    data = sorted(
        [l.strip().split(";") for l in csvfile.readlines()[:-2]],
        key = lambda x: x[0])
    data_supplemented=[]
    for d in data:
        dataline=[]
        for i, col in enumerate(d):
            colonnes = uniqueFields[fieldnames[i]]
            if len(colonnes) > 1 and colonnes[0] == i:
                ### on est juste avant une zone résumables
                val = "".join([d[c] for c in colonnes])
                dataline.append({
                    "cl": "resume",
                    "field": fieldnames[i],
                    "val": val,
                    "disp": "none",
                    "cols": len(colonnes),
                })
            dataline.append ({
                "cl": "val",
                "field": fieldnames[i],
                "val": col,
                "disp": "visible",
                "cols": 1,
            })
        data_supplemented.append(dataline)  
    return fieldnames, uniqueFields, data, data_supplemented

def index(request):
    if request.method == 'POST':
        csv_data = request.FILES['fichier'].read().decode("latin-1")
        request.session["csv_data"] = csv_data
    else:
        return render(request, 'index_getfilename.html', {})
    csv_data = request.session["csv_data"]
    fieldnames, uniqueFields, data, data_supplemented = csv2fields_and_data(
        io.StringIO(csv_data)
    )
    
            
    return render(request, "index.html", context = {
        "uniqueFields": uniqueFields,
        "fieldnames": fieldnames,
        "data": data,
        "data_supplemented": data_supplemented,
        })

def printable(request):
    ## debug = "data = " + str(json.loads(request.GET["data"]))
    ## debug += request.session["csv_data"]
    csv_data = request.session["csv_data"]
    fieldnames, uniqueFields, data, data_supplemented = csv2fields_and_data(
        io.StringIO(csv_data)
    )
    with tempfile.NamedTemporaryFile(
        dir=TMP_CONSEIL_DIR, suffix=".pdf", delete=False) as tmpfile:
        fname = tmpfile.name
        doc = SimpleDocTemplate(fname, pagesize=landscape(A4), )
        # container for the 'Flowable' objects
        elements = []
        t=Table([fieldnames] + data)
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.yellow),
            ('TEXTCOLOR',(0,0),(1,-1),colors.red),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),    ]))
        elements.append(t)
        # write the document to disk
        doc.build(elements)
    pdf_contents = open(fname, "rb").read()
    response = HttpResponse(pdf_contents, content_type='application/pdf')
    return response
