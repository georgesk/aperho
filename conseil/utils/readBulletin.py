#! /usr/bin/python3

import sys, io

def _visite_fichier(csvfile, head=None, body=None, foot=None):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @param head: une fonction qui forme la tête du résultat
    @param body: une fonction qui forme l'intérieur du résultat
    @param foot: une fonction qui forme la fin du résultat
    @return une chaîne composé de la concaténation des résultats de
            head, body, foot
    """
    h1 = csvfile.readline().split(";")
    h2 = csvfile.readline().split(";")
    fieldnames = h2[:3] + h1[3:]
    result = ""
    if head:
        result += head(fieldnames)
    for row in sorted(
            [l.strip().split(";") for l in csvfile.readlines()[:-2]],
            key = lambda x: x[0]):
        if body:
            result += body(row)
        else:
            result += str(row) + "\n"
    if foot:
        result += foot()
    return result

def visite_fichier(f, head=None, body=None, foot=None):
    """
    @param f : un fichier CSV, éventuellement déjà ouvert (prêt à lire)
    @param head: une fonction qui forme la tête du résultat
    @param body: une fonction qui forme l'intérieur du résultat
    @param foot: une fonction qui forme la fin du résultat
    @return une chaîne composé de la concaténation des résultats de
            head, body, foot
    """
    if isinstance(f, io.IOBase):
        return _visite_fichier(f, head, body, foot)
    else:
        with open(f, encoding="latin-1") as csvfile:
            return _visite_fichier(csvfile, head, body, foot)

if __name__ == "__main__":
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
    
    with open(sys.argv[1], encoding="latin-1") as csvfile:
        result = visite_fichier(csvfile, head_table, body_table, foot_table)
        print(result)
    
