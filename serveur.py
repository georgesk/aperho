#!/usr/bin/python3

import wimsdata, templates, os, os.path, json, copy, time
import cherrypy

from cherrypy.process import servers

class APserveur(object):
    """
    @class un serveur qui permet de gérer une interface web pour
    gérer des groupes d'accompagnement personnalisé.
    """
    
    def __init__(self):
        """
        Le constructeur initialise quelques variables internes, dont
        les groupes d'AP, indéfinis au départ.
        """
        return

    
    @cherrypy.expose
    def index(self, **kw):
        """
        Page d'accueil du serveur. 
        Si cherrypy.session["groupes"] est défini, ou si les
        paramètres "csvEleves" et "csvGroupes" sont définis, on
        affichera une interface pour retravailler les groupes. Dans le
        cas contraire, on demandera d'entrer les valeurs de ces deux
        derniers paramètres, qui sont des chemins vers des fichiers
        CSV.
        @param kw un dictionnaire paramètres => valeurs
        @return le code html d'une page web
        """
        result="Quelque chose s'est mal passé, ce texte ne doit pas apparaître"
        self.unlinkObsoleted()
        if self.ODFdemande(kw):
            return self.makeODF()
        if self.resetDemande(kw):
            return self.reset()
        if not self.assezDeDonnees():
            result = self.demandePlusDeDonnees(kw)
        else:
            self.instancieGroupeSiNecessaire()
            if "call" in kw:
                self.bidouilleGroupes(
                    cherrypy.session["groupes"], 
                    kw["call"], 
                    kw)
            result = self.pageDesOnglets(header_elements=self.headersCommuns())
        return result

    def ODFdemande(self, kw):
        """
        Vérifie s'il y a une demande de fichier ODF en cours
        @param kw un dictionnaire de paramètres issus d'une requête
        @return vrai si c'est bien le cas
        """
        return "call" in kw and kw["call"]=="makeODF"

    def instancieGroupeSiNecessaire(self):
        """
        Permet d'instancier la variable de session "groupes"
        quand on dispose des données suffisantes, quand celle-ci
        n'existe pas encore.
        """
        if "groupes" not in cherrypy.session:
            cherrypy.session["groupes"]=wimsdata.groupesAp(
                cherrypy.session["fichEleves"],
                cherrypy.session["fichGroupes"])
        return

    def headersCommuns(self):
        """
        Renvoie des en-têtes communs à toutes les pages
        @return une suite déléments valides dans l'en-tête d'une page HTML
        """
        return templates.cssLink("style.css") + \
            templates.cssLink("smoothness/jquery-ui.css") + \
            templates.jsScript("jquery/jquery.js") + \
            templates.jsScript("jquery-ui/jquery-ui.js") + \
            templates.jsScript("programme.js")

    def demandePlusDeDonnees(self, kw=dict()):
        """
        Renvoie la page qui demande plus de données pour pouvoir
        gérer les groupes d'AP, et éventuellement si le dictionnaire kw
        apporte les données manquantes, renvoie directement la
        page de gestion
        @param kw dictionnaires de données issues de requêtes précédentes.
        Par défaut, c'est un dictionnaire vide (nécessaire pour l'opération
        reset)
        @return du code HTML valide
        """
        result="Problème avec demandePlusDeDonnees : ce texte ne doit pas apparaître."
        if "leFichier" in kw:
            leFichier=kw["leFichier"]
            if leFichier is not str and leFichier.filename:
                tempName="tmp/WIMS{0:f}.csv".format(time.time())
                with open(tempName,"wb") as tempOutfile:
                    while True:
                        data=leFichier.file.read(8192)
                        if not data: break
                        tempOutfile.write(data)

                fichEleves=""
                fichGroupes=""
                if wimsdata.checkCsvEleves(tempName):
                    cherrypy.session["fichEleves"]=tempName
                if wimsdata.checkCsvGroupes(tempName):
                    cherrypy.session["fichGroupes"]=tempName

                if "fichEleves" in cherrypy.session:
                    fichEleves=cherrypy.session["fichEleves"]
                if "fichGroupes" in cherrypy.session:
                    fichGroupes=cherrypy.session["fichGroupes"]

                if not self.assezDeDonnees():
                    # ce script est inutile si les deux données sont là
                    result = self.pageTelechargement(
                        header_elements=self.headersCommuns()+\
                            self.feedbackDonnees(
                                fichEleves, fichGroupes, leFichier.filename),
                        body_elements=self.csvForm(),
                        )
                else:
                    # il y a assez de données !
                    cherrypy.session["groupes"]=wimsdata.groupesAp(
                        cherrypy.session["fichEleves"],
                        cherrypy.session["fichGroupes"])
                    result = self.pageDesOnglets(
                        header_elements=self.headersCommuns())
        else: # il n'y a pas de paramètre "leFichier"
            result = self.pageTelechargement(
                header_elements=self.headersCommuns(),
                body_elements=self.csvForm(),
                )
        return result

    def feedbackDonnees(self, fichEleves, fichGroupes, filename):
        """
        Produit un script de type Javascript qui s'occupe d'afficher
        un feedback au sujet du fichier de données téléchargé
        @param fichEleves nom du fichier contenant les données des élèves,
        ou une chaîne vide
        @param fichGroupes nom du fichier contenant les données des groupes,
        ou une chaîne vide
        @param filename nom du fichier qu'on a essayé de télécharger
        """
        return """
<script type="text/javascript">
  function alertAboutFile(){
    var fichEleves="%s";
    var fichGroupes="%s";
    if (fichEleves.length==0 && fichGroupes.length==0){
      alert("Fichier « %s » non reconnu.");
    }
    if (fichEleves.length>0){
      $("#fichEleves").text("Le fichier des élèves a été chargé. Il reste à envoyer le fichier des choix de groupes.");
    }
    if (fichGroupes.length>0){
      $("#fichGroupes").text("Le fichier des choix de groupes a été chargé. Il reste à envoyer le fichier des noms d'élèves.");
    }
  }
  window.addEventListener("load", alertAboutFile, false);
</script>
""" % (fichEleves,
       fichGroupes,
       filename)

    def resetDemande(self, kw):
        return "call" in kw and kw["call"]=="reset"

    def reset(self):
        """
        redémarre le service au niveau de la demande de fichiers
        efface les données de session
        @return le code HTML de la page initiale
        """
        del cherrypy.session["groupes"]
        del cherrypy.session["fichEleves"]
        del cherrypy.session["fichGroupes"]
        return self.demandePlusDeDonnees()

    def bidouilleGroupes(self,groupes, routine, kw):
        """
        modifie en place l'objet qui représente les groupes
        @param groupes une instance de groupesAp
        @param routine une chaîne qui identifie le traitement à faire
        @param kw dictionnaire contenant d'autres paramètres issus de
        requêtes.
        """
        if routine=="delete":
            eleveId=kw["eleveId"]
            i=int(kw["groupe"])
            if i==0:
                # cas des élèves non-inscrits, on supprime vraiment
                # ce serait bien d'afficher un dialogue garde-fou
                groupes.supprimeEleve(eleveId,0)
            else:
                # cas des élèves inscrits, on ne suprime pas vraiment
                # on déplace l'élève vers le groupe des non-inscrits
                groupes.changeDeGroupe(eleveId,i,0)
        elif routine=="change":
            eleveId=kw["eleveId"]
            i=int(kw["groupe"])
            try:
                j=int(kw["dest"])
            except:
                j=i # si on a mal sélectionné la classe de destination
                # la clé "dest" est indéfinie : on ne fait rien.
            groupes.changeDeGroupe(eleveId,i,j)
        elif routine=="newEleve":
            nom=kw["nom"].upper()
            prenom=kw["prenom"]
            classe=kw["classe"]
            ident=nom+prenom+classe
            groupes.ajouteEleve(wimsdata.idEleve(ident, nom, prenom, classe))
        elif routine=="changeTitre":
            i=int(kw["i"])
            titre=kw["titre"]
            groupes.details[i]["titre"]=titre
        elif routine=="changeSalle":
            i=int(kw["i"])
            salle=kw["salle"]
            groupes.details[i]["salle"]=salle
        elif routine=="creeGroupe":
            titre=kw["titre"]
            salle=kw["salle"]
            i=self.groupeMax()+1
            groupes[i]=[]
            groupes.details[i]={"titre": titre, "salle": salle}
        elif routine=="supprimeGroupe":
            titre=kw["dest"]
            found=[i for i in groupes if groupes.details[i]["titre"]==titre]
            if found:
                i=found[0]
                for e in copy.copy(groupes[i]):
                    #désinscrire tous les élèves du groupe
                    groupes.changeDeGroupe(e,i,0)
                del(groupes[i])
                del(groupes.details[i])
        return

    def pageDesOnglets(self, header_elements="", body_elements="",
                       title="..:: Aperho -- gestion de groupes d'AP ::.."):
        """
        Fabrique une page web interactive avec des onglets
        contenant les groupes d'AP pré-remplis.
        @param header_elements éléments d'entête hérités
        @param body_elements éléments de la page hérités
        @param title titre de la page web
        """
        body_elements+=self.groupe2tabs()
        return templates.webpage().format(
            title=title,
            header_elements=header_elements,
            body_elements=body_elements,
            )

    def pageTelechargement(
        self, header_elements="", body_elements="",
        title="..:: APERHO : mise en place des fichiers de WIMS ::.."):
        """
        Fabrique une page web interactive pour mettre en place deux
        fichiers de données de WIMS au formats CSV.
        @param header_elements éléments d'entête hérités
        @param body_elements éléments de la page hérités
        @param title titre de la page web
        """
        return templates.webpage().format(
            title="title",
            header_elements=header_elements,
            body_elements=body_elements,
            )

    def assezDeDonnees(self):
        """
        vérifie si on dispose de données suffisantes pour créer
        les groupes d'AP.
        @return vrai si les deux fichiers temporaires nécessaires sont déjà là
        """
        return "fichEleves" in cherrypy.session and \
            "fichGroupes" in cherrypy.session

    @cherrypy.expose
    def test_fileUpload(self, leFichier=None):
        """
        un essai pour récupérer des fichiers, les analyser et passer à
        la constitution de groupes automatiquement.
        @param leFichier enregistreent renvoyé par le champ de saisie
        """
        additionalScript="" # script à ajouter dans l'en-tête si nécessaire
        if leFichier:
            if leFichier is not str and leFichier.filename:
                tempName="tmp/WIMS{0:f}.csv".format(time.time())
                with open(tempName,"wb") as tempOutfile:
                    while True:
                        data=leFichier.file.read(8192)
                        if not data: break
                        tempOutfile.write(data)
                recog=""
                
                if wimsdata.checkCsvEleves(tempName)=='OK':
                    recog="OK_E"
                    cherrypy.session["fichEleves"]=tempName
                if wimsdata.checkCsvGroupes(tempName)=='OK':
                    recog="OK_G"
                    cherrypy.session["fichGroupes"]=tempName
                additionalScript="""
<script type="text/javascript">
  function alertAboutFile(){
    var recog="%s";
    if (recog==""){
      alert("Fichier « %s » non reconnu.");
    }
    if (recog=="OK_E"){
      $("#fichEleves").text("Le fichier des élèves a été chargé. Il reste à envoyer le fichier des choix de groupes.");
    }
    if (recog=="OK_G"){
      $("#fichEleves").text("Le fichier des choix de groupes a été chargé. Il reste à envoyer le fichier des noms d'élèves.");
    }
  }
  window.addEventListener("load", alertAboutFile, false);
</script>
""" % (recog, leFichier.filename)
        header_elements=templates.cssLink("style.css")
        header_elements+=templates.cssLink("smoothness/jquery-ui.css")
        header_elements+=templates.jsScript("jquery/jquery.js")
        header_elements+=templates.jsScript("jquery-ui/jquery-ui.js")
        header_elements+=templates.jsScript("programme.js")
        header_elements+=additionalScript
        
        body_elements="""
<form action="#" id="fichForm" method="post"  enctype="multipart/form-data">
  Fichier : <input type="file" name="leFichier" onchange="$('#fichForm').submit()"/>
</form>
<div id="fichEleves"></div>
<div id="fichGroupes"></div>

"""
        return templates.webpage().format(
            title="Mise en place des fichiers de WIMS",
            header_elements=header_elements,
            body_elements=body_elements,
            )

    @cherrypy.expose
    def a_propos(self):
        """
        Donne les informations légales à propos du logiciel
        """
        return templates.webpage().format(
            title="À propos d'AP-Rho",
            header_elements="",
            body_elements="""
<h1>À propos d'AP-Rho</h1>
<p>
Le but de l'application web AP-Rho consiste à faciliter la gestion des groupes
d'accompagnement personnalisé, telle qu'on la pratique au lycée Jean Bart de
Dunkerque. Cette gestion repose sur l'usage d'un serveur WIMS, selon un
protocole mis au point par Benoît Markey, et mis en œuvre par lui-même et
Gérard Dessingué durant les années 2013-2015.
</p>
<p>
La récolte des choix de groupes d'Accompagnement Personnalisé (AP) que font les
élèves s'effectue quelques semaines avant le démarrage des nouveaux groupes.
Cette « récolte » consistait initialement en une copie des résultats d'un
sondage supporté par la plateforme WIMS du lycée, puis du traitement des listes,
le plus souvent en les imprimant et en annotant à la main. Ensuite, quand les
listes étaient décidées par l'équipe pédagogique, il faut les communiquer aux
conseillers principaux d'éducation et les afficher aux élèves. Cette dernière
étape nécessite une remise en forme et de multiples vérifications, et pour tout
dire, elle constitue une « double saisie ».
</p>
<p>
Le but de l'application AP-Rho est d'éviter cette double saisie, et idéalement,
de permettre un fonctionnement sans papier superflu. Les changements de groupes
des élèves, le traitement des non-inscrits se fait sur un écran. On peut 
imaginer de projeter cet écran pour un travail collaboratif.
</p>
<p>
Quand le travail de constitution des groupes d'AP est fini, l'application
 permet d'exporter les groupes dans un fichier de traitement de texte au
format ODF (Open Document Format), qui est une norme ISO que l'on doit
utiliser de préférence pour tous nos documents pérennes.
</p>
<h2>Auteurs du logiciel AP-Rho</h2>
<p>
© 2014 Georges Khaznadar &lt;georgesk@debian.org&gt;
</p>
<h2>Licence du logiciel</h2>
<p>
AP-Rho est un logiciel libre : ainsi donc,
</p>
<ul>
<li>tout le monde a le droit de l'utiliser&nbsp;;</li>
<li>on peut légalement le copier et le diffuser&nbsp;;</li>
<li>on peut légalement comprendre son fonctionnement et le modifier, et diffuser les versions modifiées&nbsp;;</li>
</ul>
<p>Ce logiciel est protégé par la <a href="http://www.gnu.org/licenses/agpl-3.0.fr.html">licence AGPL version 3.0</a>, ceci entraîne quelques contraintes&nbsp;:</p>
<ul>
<li>Il est interdit de diffuser des copies ou des versions modifiées de ce logiciel en prétendant qu'il n'est pas libre&nbsp;;</li>
<li>Les mentions légales concernant ce logiciel doivent être apparentes&nbsp;;</li>
<li>Les version modifiées de ce logiciel doivent être sous licence AGPL version 3.0&nbsp;;</li>
<li>Les auteurs du logiciel original et des versions modifiées doivent être cités&nbsp;;</li>
</ul>
<p>
Vous pouvez trouver le texte complet de la licence AGPL version 3.0 sur le site
 <a href="http://www.gnu.org/licenses/agpl-3.0.fr.html">www.gnu.org</a>.
</p>
""",
            )

    @cherrypy.expose
    @cherrypy.tools.json_out(debug=True)
    def check_eleves(self,q):
        """
        traite une requête AJAX pour déterminer si un nom de fichier
        renvoie bel et bien une liste d'élèves
        * @param q la requête est un nom de fichier
        * @ return une chaîne de caractères "OK" en cas de succès
        """
        reponse=wimsdata.checkCsvEleves(q)
        return reponse

    @cherrypy.expose
    @cherrypy.tools.json_out(debug=True)
    def check_groupes(self,q):
        """
        traite une requête AJAX pour déterminer si un nom de fichier
        renvoie bel et bien une liste dde groupes
        * @param q la requête est un nom de fichier
        * @ return une chaîne de caractères "OK" en cas de succès
        """
        reponse=wimsdata.checkCsvGroupes(q)
        return reponse

    @staticmethod
    def unlinkObsoleted(timeout=600, tmpdir="tmp"):
        """
        efface les fichiers trop anciens dans le répertoire des 
        fichiers temporaires
        @param timeout durée en secondes avant qu'un fichier ne soit
        considéré comme obsolète (10 minutes par défaut)
        @param tmpdir répertoire des fichiers temporaires ("tmp" par défaut)
        """
        # on fait une liste de doublets (date, fichier)
        l=[ (os.stat(os.path.join(tmpdir,f)).st_ctime, f) \
                for f in os.listdir(tmpdir)]
        # on filtre ceux qui sont plus vieux que dix minutes
        obsoleted=filter(lambda x: time.time()-x[0] >= timeout, l)
        for o in obsoleted:
            # on efface ces fichiers-là
            os.unlink(os.path.join("tmp",o[1]))
        return

    def makeODF(self):
        """
        fabrique un fichier ODT pour l'affichage des groupes
        @return le contenu binaire du fichier odt
        """
        cherrypy.response.headers['Content-type'] = "application/vnd.oasis.opendocument.text"
        cherrypy.response.headers['Content-Disposition'] = "attachment; filename=ap.odt"
        nomfichier = "AP_{0:f}.odt".format(time.time())
        chemin = os.path.join("tmp",nomfichier)
        cherrypy.session["groupes"].toODF(chemin)
        return open(chemin,"rb").read()

    def csvForm(self):
        """
        Fabrique la page pour demander les fichiers CSV concernant
        les élèves et les groupes
        @return du code HTML valide
        """
        return """
<h1 id="accueilTitre">APERHO : mise en place des fichiers exportés par WIMS</h1>
<div id="explication">À l'aide du bouton de recherche de fichiers ci-dessous, 
il vous faut remonter au serveur AP-rho une série de deux fichiers :
<ol>
  <li>Un fichier qui contient la liste des élèves de la barrette d'AP&nbsp;;</li>
  <li>Un fichier qui contient la liste des choix faits par les élèves&nbsp;;<br/><i>N.B.&nbsp;: cette sorte de fichier contient le mot « vote ».</i></li>
</ol>
Vous pouvez aussi <a href="/static/manuel.html" target="_manuel_">lire l'aide en ligne</a>, ou <a href="/static/manuel.odt">télécharger un fichier d'aide</a>.
</div>
<form action="index" id="fichForm" method="post"  enctype="multipart/form-data">
<fieldset id="fichWims">
  <legend>Recherche des fichiers exportés par WIMS</legend>
  <input type="file" id="leFichier" name="leFichier" onchange="$('#fichForm').submit()"/>
</form>
<div id="fichEleves"></div>
<div id="fichGroupes"></div>
"""

    def groupe2tabs(self):
        """
        Produit des onglets web permettant de gérer les groupes d'AP.
        On utilise la structure cherrypy.session["groupes"]
        @return du code HTML valide
        """
        groupes=cherrypy.session["groupes"]
        result="""
  <div id="tabs">
    <ul>"""
        for i in groupes:
            result+= """
      <li><a href="#tabs-{i}">{detail}</a></li>""".format(
                i=i, detail=groupes.details[i]["titre"]+" ({n})".format(
                  n=len(groupes[i])
              ))
        result+="""
      <li><a href="#tabs-special">autres opérations</a></li>"""
        result+="""
    </ul>"""
        for i in groupes:
            result+="""
    <div id="tabs-{i}">
      {tab_elements}
    </div>""".format(i=i, tab_elements=self.eleveElements(i))
        result+="""
    <div id="tabs-special">
      {special}
    </div>""".format(special=self.operationsSpeciales())
        result+="""
  </div>
"""
        return result

    def operationsSpeciales(self):
        """
        Crée le contenu de l'onglet des opérations spéciales : ajouter
        un élève, ajouter un groupe, supprimer un groupe
        @return du code HTML valide
        """
        groupes=cherrypy.session["groupes"]
        result=""
        result+="""
      <button type="button" class="rounded" onclick="document.location='/a_propos'">À propos ... </button> <br/>"""
        result+="""
      <button type="button" class="rounded" onclick="document.location='/static/manuel.html'">Aide </button> <br/>"""
        result+="""
      <button type="button" class="rounded" onclick="creeEleve()">Créer un élève </button> <br/>"""
        result+="""
      <button type="button" class="rounded" onclick="creeGroupe()">Créer un groupe</button> <br/>"""
        liste_titres=[groupes.details[i]["titre"] for i in groupes.keys() if i > 0]
        liste_titres=json.dumps(liste_titres)
        result+="""
      <button type="button" class="rounded" onclick='supprimeGroupe({g})'>Supprimer un groupe</button> <br/>""".format(g=liste_titres)
        result+="""
      <button type="button" class="rounded download" onclick='makeODF()'>Imprimer</button> Fabrique un document (format ODT)<br/>"""
        result+="""
      <button type="button" class="rounded download" onclick='reset()'>Tout remettre à zéro</button>Permet de reprendre d'autres fichiers de Wims<br/>"""
        return result

    def eleveElements(self, i):
        """
        Crée une suite d'éléments représentant un groupe d'élèves.
        Chaque enregistrement d'élèves est rendu avec un groupe d'outils qui
        permet de gérer les groupes d'AP
        @param i une clé d'accès à cherrypy.session["groupes"] 
        (numéro du groupe)
        @return du code HTML valide
        """
        groupes=cherrypy.session["groupes"]
        result=""
        result+="""
      <p class="h1">{title}<button type="button" class="rounded" onclick="changeTitre({i},'{title}')"><img src='/static/img/change.png' alt='changer de titre' title='Changer de titre'/></button></p>
      <p class="h2">{salle}<button type="button" class="rounded" onclick="changeSalle({i},'{salle}')"><img src='/static/img/change.png' alt='changer de salle' title='Changer de salle'/></button></p>
      <ol>""".format(i=i,title=groupes.details[i]["titre"],salle=groupes.details[i]["salle"])
        for e in sorted(groupes[i],key=lambda x: x.classe+x.nom+x.prenom):
            result+="""
        <li class="eleve">{ctrl} {e}</li>
""".format(ctrl=self.controlEleve(e,i), e=str(e))
        result+="""
      </ol>"""
        return result

    def controlEleve(self, e, i):
        """
        fabrique la série de contrôles attachés à chaque élève dans 
        un groupe : supprimer, changer de groupe, etc.
        @param e une instance de eleveId
        @param i le numéro de groupe où se trouve l'élève couramment
        @return du code HTML valide
        """
        groupes=cherrypy.session["groupes"]
        result=""
        result+=" <img src='/static/img/del.png' alt='supprimer' title='Supprimer' onclick='supprimeEleve(\"{e}\", {i})'/>".format(e=e.id, i=i)
        maxi=self.groupeMax()
        liste_titres=[]
        # on fait une liste de groupes ordonnée par numéro
        for j in range(maxi+1):
            if j in groupes:
                liste_titres.append(groupes.details[j]["titre"])
        liste_titres=json.dumps(liste_titres)
        result+=" <img src='/static/img/change.png' alt='changer de groupe' title='Changer de groupe' onclick='deplaceEleve(\"{e}\", {i}, {maxi}, \"{nom}\",{g})'/>".format(e=e.id, i=i, maxi=maxi, nom=e.nom+" "+e.prenom, g=liste_titres)
        return result

    def groupeMax(self):
        """
        Détermine le plus grand nuéro de groupe
        @return un entier
        """
        return max(list(cherrypy.session["groupes"].keys()))

if __name__ == '__main__':
    conf = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8123,
            #'environment': 'production',
            #'log.error_file': os.path.join(os.path.abspath(os.getcwd()), 'aperho.log'),
            },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
            },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
            }
        }
    cherrypy.quickstart(APserveur(), '/', conf)
