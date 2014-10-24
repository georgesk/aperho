#!/usr/bin/python3

def webpage():
    """
    @return une page web où il est possible de formater des parties
    nommées "title", "header_elements" et "body_elements"
    """
    return """<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{title}</title>
{header_elements}
</head>
<body>
{body_elements}
</body>
</html>
"""

def cssLink(url, indent=2):
    """
    crée un texte "<link ... rel='stylesheet'>"
    @param url le nom d'un fichier de style, qui sera automatiquement
    préfixé par "/static/css"
    @param indent espaces ajoutés à gauche
    @return le texte d'un élément link
    """
    return " "*indent+"<link href='/static/css/{url}' rel='stylesheet'/>\n".format(url=url)

def jsScript(url, indent=2):
    """
    crée un texte "<script ...></script>"
    @param url le nom d'un fichier de script, qui sera automatiquement
    préfixé par "/static/js"
    @param indent espaces ajoutés à gauche
    @return le texte d'un élément script
    """
    return " "*indent+'<script type="application/javascript" src="/static/js/{url}"></script>\n'.format(url=url)

# compteur de forms statique
formCounter=0

def form(method="get", action="#", form_elements="", indent=2, **kw):
    """
    crée un formulaire
    @param method a la valeur GET (par défaut) ou POST
    @param action une url ("#" par défaut")
    @param form_elements des éléments à inclure dans le formulaire
    @param indent indentation (2 espaces par défaut)
    @param kw dictionnaire de paramètres => valeurs
    @return le texte d'un élément form
    """
    global formCounter
    formCounter+=1
    return """{indent}<form method="{method}" action="{action}" id="{idt}">
{form_elements}
{indent}</form>
""".format(indent=" "*indent, 
           method=method, 
           action=action, 
           form_elements=form_elements,
           idt="form{0:03d}".format(formCounter),
           )
