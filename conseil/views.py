from django.shortcuts import render
from conseil.utils.readBulletin import *

def csv2fields_and_data(csvfile):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @return une liste d'en-têtes, puis une liste de lignes de données
    """
    h1 = csvfile.readline().split(";")
    h2 = csvfile.readline().split(";")
    fieldnames = h2[:3] + h1[3:]
    data = sorted(
        [l.strip().split(";") for l in csvfile.readlines()[:-2]],
        key = lambda x: x[0])
    return fieldnames, data

def head_table(fieldnames):
    result = """\
<html>
<head>
<title>Test</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<style>
table {border-collapse: collapsed}
th, td {border: 1px solid black; background: rgba(255,255,200,0.5);}
tr { height: 52px;}
tr:nth-child(odd) {background: lightcyan}
</style>
<script src="test.js"></script>
</head>
<body>
<table class="matable">\n<tr>
"""
    for h in fieldnames:
        result += f"<th>{h}</th>"
    result += "</tr>\n"
    return result
def foot_table():
    return "</table>\n</body>\n</html>\n"
def body_table(row):
    result = "<tr>"
    for val in row:
        result += f"<td>{val}</td>"
    result += "</tr>\n"
    return result

def index(request):
    return render(request, "index1.html", context = {
        "page": visite_fichier("conseil/1G09_3tri.csv", head_table, body_table, foot_table)
        })

