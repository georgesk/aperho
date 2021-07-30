#! /usr/bin/python3

import csv, sys, io

def _visite_fichier(csvfile, head=None, body=None, foot=None):
    """
    @param csvfile: un fichier ouvert, sous-classe de io.IOBase
    @param head: une fonction qui forme la tête du résultat
    @param body: une fonction qui forme l'intérieur du résultat
    @param foot: une fonction qui forme la fin du résultat
    @return une chaîne composé de la concaténation des résultats de
            head, body, foot
    """
    r = csv.DictReader(csvfile, delimiter=";")
    result = ""
    if head:
        result += head(r)
    for row in r:
        if body:
            result += body(row)
        else:
            result += str(row) + "\n"
    if foot:
        result += foot(r)
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
    def head_table(r):
        result = "<table class=\"matable\">\n<tr>"
        for h in r.fieldnames:
            result += f"<th>{h}</th>"
        result += "</tr>\n"
        return result
    def foot_table(r):
        return "</table>\n"
    def body_table(row):
        result = "<tr>"
        for col, val in row.items():
            result += f"<td class='{col}'>{val}</td>"
        result += "</tr>\n"
        return result
    
    with open(sys.argv[1], encoding="latin-1") as csvfile:
        result = visite_fichier(csvfile, head_table, body_table, foot_table)
        print(result)
    
