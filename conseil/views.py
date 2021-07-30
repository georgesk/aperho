from django.shortcuts import render

import collections

from conseil.utils.readBulletin import *

def csv2fields_and_data(csvfile):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @return une liste d'en-têtes, puis une liste de lignes de données
    """
    h1 = csvfile.readline().strip().split(";")
    h2 = csvfile.readline().strip().split(";")
    fieldnames = h2[:3] + h1[3:]
    data = sorted(
        [l.strip().split(";") for l in csvfile.readlines()[:-2]],
        key = lambda x: x[0])
    return fieldnames, data

def index(request):
    fieldnames, data = csv2fields_and_data(
        open("conseil/1G09_3tri.csv", encoding="latin-1")
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
                dataline.append({
                    "cl": "resume",
                    "field": fieldnames[i],
                    "val": "résumé",
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

