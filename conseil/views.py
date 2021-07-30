from django.shortcuts import render

import collections, io, json

from conseil.utils.readBulletin import *

def protect(fieldname):
    return fieldname.replace(" ", "_").replace(".","_")

def csv2fields_and_data(csvfile):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @return une liste d'en-têtes, puis une liste de lignes de données
    """
    h1 = csvfile.readline().strip().split(";")
    h2 = csvfile.readline().strip().split(";")
    fieldnames = [ protect(f) for f in h2[:3] + h1[3:]]
    data = sorted(
        [l.strip().split(";") for l in csvfile.readlines()[:-2]],
        key = lambda x: x[0])
    return fieldnames, data

def index(request):
    if request.method == 'POST':
        csv_data = request.FILES['fichier'].read().decode("latin-1")
        request.session["csv_data"] = csv_data
    else:
        return render(request, 'index_getfilename.html', {})
    csv_data = request.session["csv_data"]
    fieldnames, data = csv2fields_and_data(
        io.StringIO(csv_data)
    )
    
    uniqueFields = collections.OrderedDict()
    for i,f in enumerate(fieldnames):
        if f in uniqueFields:
            uniqueFields[f].append(i)
        else:
            uniqueFields[f] = [i]
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
            
    return render(request, "index.html", context = {
        "uniqueFields": uniqueFields,
        "fieldnames": fieldnames,
        "data": data,
        "data_supplemented": data_supplemented,
        })

def printable(request):
    debug = "data = " + str(json.loads(request.GET["data"]))
    return render(request, 'index_getfilename.html', {"debug": debug,})
