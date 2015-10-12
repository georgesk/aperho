#!/usr/bin/python3

import sys, csv, re, os
from collections import OrderedDict
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span, SoftPageBreak

def checkCsvEleves(data):
    """
    Vérification qu'un fichier contient bien une liste d'élèves
    @param data un nom de fichier censément de type CSV
    @return vrai si la vérification est faite
    """
    champsAttendus = set(('firstname', 'login', 'lastname'))
    WimsEncoding   = 'latin-1'
    WimsDelimiter  = ','
    result=False
    try:
        reader = csv.DictReader(open(data, encoding=WimsEncoding), 
                                delimiter=WimsDelimiter)
        for d in reader:
            if set (d.keys()) >= champsAttendus and d['login']:
                    result=True
    except:
        pass
    return result

def checkCsvGroupes(data):
    """
    Vérification qu'un fichier contient bien une liste d'élèves
    @param data un nom de fichier censément de type CSV
    @return vrai si la vérification est faite
    """
    WimsEncoding   = 'latin-1'
    WimsDelimiter  = ','
    result=False
    try:
        reader = csv.DictReader(open(data,  encoding=WimsEncoding), 
                                delimiter=WimsDelimiter)
        for d in reader:
            items=list(d.items())[0]
            if 'Questionnaire' in items[0] and '_' in items[1]: 
                    result=True
    except:
        pass
    return result

class groupesAp(OrderedDict):
    """
    @class implementation d'un ensemble de groupes d'AP comme dictionnaire
    ordonné
    """

    def __init__(self, dataE, dataC):
        """
        Le constructeur travaille à partir du dépouillement
        d'un questionnaire de Wims.
        @param dataE données concernant les comptes d'élèves ; typiquement le
        nom d'un fichier CSV tel que "data-127342_3.csv"
        @param dataC données concernant leurs choix ; typiquement le nom
        d'un fichier CSV tel que "data-127342_3-vote-2.csv"
        @return un OrderedDict des votes, les clés sont les choix, et les valeurs
        sont des listes d'identifications d'élèves.
        """
        OrderedDict.__init__(self)
        self.details={}
        self.textdoc=None
        readerE = csv.DictReader(open(dataE, encoding='latin-1'), delimiter=',')
        readerC = csv.DictReader(open(dataC, encoding='latin-1'), delimiter=',')
        eleves={}
        for dE in readerE:
            dE["choix"]=False
            eleves[dE["login"]]=dE
        for dC in readerC:
            m=re.match(r"\d+/\d+/(.*);(\d+)_", dC[list(dC.keys())[0]])
            if m:
                eleves[m.group(1)]["choix"]=True
                i=int(m.group(2))
                if i not in self:
                    self[i]=[]
                    self.details[i]={"titre": "groupe {i}".format(i=i), "salle":"?"}
                # création de l'identifiant d'élève et inscription
                self[int(m.group(2))].append(idEleve.fromWims(eleves[m.group(1)]))
        # et pour les élèves qui n'ont rien choisi
        for e in eleves:
            # attention, il y a des enregistrements vides dont il ne faut
            # pas tenir compte, on teste le login.
            if eleves[e]["login"] != "" and eleves[e]["choix"] == False:
                if 0 not in self:
                    self[0]=[]
                    self.details[0]={"titre": "non inscrits".format(i=i), "salle": ""}
                # création de l'identifiant d'élève et non-inscription
                self[0].append(idEleve.fromWims(eleves[e]))
        # et au cas où un groupe (autre que le dernier) n'aurait
        # pas été choisi par les élèves, on le crée quand même
        maxi=max(list(self.keys()))
        for i in range(1,maxi): # pas la peine de tester le dernier groupe
            if i not in self:
                self[i]=[]
                self.details[i]={"titre": "groupe {i}".format(i=i), "salle":"?"}
        return

    def changeDeGroupe(self, e, g1, g2):
        """
        change un élève de groupe
        @param e une instance de idEleve
        @param g1 numéro de groupe initial
        @param g2 numéro de groupe destination
        """
        e=self.trouveEleve(e,g1)
        if e:
            self[g1].remove(e)
            self[g2].append(e)
        return

    def supprimeEleve(self, e, g):
        """
        supprime un élève, repéré dans un groupe
        @param e une instance de idEleve
        @param g numéro de groupe
        """
        e=self.trouveEleve(e,g)
        if e:
            self[g].remove(e)
        return

    def trouveEleve(self, e, g):
        """
        S'assure de bien trouver un élève dans le groupe g, et si e
        est juste un identifiant-chaîne, trouve l'instance de eleveId
        @param e une chaîne ou une instance d'eleveId
        @param g un numéro de groupe
        @return une instance de eleveId ou None
        """
        if type(e)==type(""): # on passe une chaîne
            found=filter(lambda x: str(x.id)==str(e), self[g])
            if found:
                e=list(found)[0]
            else:
                e=None
        else:
           if e not in self[g]:
               e=None
        return e

    def ajouteEleve(self, e):
        """
        ajoute un élève dans les non-inscrits
        @param e une instance de idEleve
        @param g numéro de groupe
        """
        self[0].append(e)
        return
        
    def nouveauGroupe(self, nomBref, salle):
        """
        ajoute un groupe nouveau
        @param nomBref nom du groupe (pas trop long)
        @param salle salle où le groupe aura cours
        """
        i=max(list(self.keys()))+1
        self[i]=[]
        self.details[i]={"titre": nomBref, "salle": salle}
        return

    def supprimeGroupe(self, i):
        """
        supprime un groupe
        @param i un numéro de groupe
        """
        del self[i]
        if i in self.details:
            del self.details[i]
        return

    def __str__(self):
        """
        @return une forme imprimable du dictionnaire
        """
        result=""
        for i in self:
            if i > 0:
                result+="==== {desc} (salle {salle}) ====\n".format(desc=self.details[i]["titre"], salle=self.details[i]["salle"])
            else:
                result+="============ non-inscrits =================\n"
            for elv in self[i]:
                result+="  {eleve}\n".format(eleve=elv)
        return result

    def newODF(self):
        """
        Crée un nouveau document texte vide, mais pourvu de styles
        ce document est dans self.textdoc
        """
        self.textdoc = OpenDocumentText()
        # Styles
        h1style = Style(name="Heading 1", family="paragraph")
        h1prop = ParagraphProperties(breakbefore="page")
        h1style.addElement(h1prop)
        h1style.addElement(TextProperties(attributes={'fontsize':"48pt",'fontweight':"bold" }))
        self.textdoc.styles.addElement(h1style)
        h2style = Style(name="Heading 2", family="paragraph")
        h2style.addElement(TextProperties(attributes={'fontsize':"36pt",'fontweight':"bold" }))
        self.textdoc.styles.addElement(h2style)
        # Même technique, mais avec les styles "automatiques"
        boldstyle = Style(name="Bold", family="text")
        boldprop = TextProperties(fontweight="bold")
        boldstyle.addElement(boldprop)
        self.textdoc.automaticstyles.addElement(boldstyle)
        grandstyle = Style(name="Grand", family="text")
        grandprop = TextProperties(fontsize="20pt")
        grandstyle.addElement(grandprop)
        self.textdoc.automaticstyles.addElement(grandstyle)
        #self.textdoc.text.setAttribute('usesoftpagebreaks', 1)
        return

    def toODF(self, filename="Nouveau_Fichier.odt"):
        """
        Fabrique un fichier au format OpenDocument à partir des données de
        groupes d'AP.
        @param filename un chemin vers un fichier à créer.
        """
        self.newODF()
        # Fabrication du texte
        for i in self:
            # Titres pour chaque groupe d'AP
            self.heading(self.textdoc,1,self.details[i]["titre"])
            self.heading(self.textdoc,2,self.details[i]["salle"])
            # noms des participants, par ordre de classe et de nom
            for e in sorted(self[i], key=lambda e: e.classe+e.nom+e.prenom):
                e.paragraph(self.textdoc)
            # on tente un saut de page
            saut=SoftPageBreak()
            self.textdoc.text.addElement(saut)
        # Enregistement du document
        self.textdoc.save(filename)
        return

    def heading(self, textdoc, level, text=""):
        """
        Ajoute un titre
        @param textdoc document en cours de modification
        @param level niveau de sous-titre
        @param text texte du titre
        """
        hstyle=self.textdoc.getStyleByName("Heading {level:d}".format(level=level))
        h=H(outlinelevel=level, 
            stylename=hstyle, 
            text=text)
        textdoc.text.addElement(h)
        return

class idEleve:
    """
    @class identification d'un élève
    """
    def __init__(self, idt, nom, prenom, classe):
        """
        Le constructeur
        @param idt un identifiant unique
        @param nom le nom
        @param prenom le prénom
        @param classe la classe
        """
        self.id=idt
        self.nom=nom
        self.prenom=prenom
        self.classe=classe
        return

    def __str__(self):
        """
        Conversion en chaîne de caractères
        """
        return "{classe} {nom} {prenom}".format(nom=self.nom, prenom=self.prenom, classe=self.classe)

    def __repr__(self):
        """
        Conversion en chaîne de caractères pour des motifs techniques
        (doit donner tous les détails internes, dont le login
        """
        return "{idt} : {classe} {nom} {prenom}".format(idt=self.id, nom=self.nom, prenom=self.prenom, classe=self.classe)

    def paragraph(self, textdoc):
        """
        Écrit les données de l'élève dans un paragraphe du document courant
        @param textdoc document en cours d'élaboration
        """
        if not textdoc:
            return
        grandstyle=textdoc.getStyleByName("Grand")
        boldstyle=textdoc.getStyleByName("Bold")

        p = P()
        s = Span(stylename=grandstyle, text=self.classe+" ")
        p.addElement(s)
        s1=Span(stylename=boldstyle, text=self.nom)
        s.addElement(s1)
        s.addText(" "+self.prenom)
        textdoc.text.addElement(p)
        return

    @staticmethod
    def fromWims(dico):
        """
        crée une nouvelle instance d'idEleve
        à partir d'un enregistrement issu de Wims
        @param dico un dictionnaire
        @return une instance de idEleve
        """
        try:
            classe, nom = dico["lastname"].split('-',1)
        except:
            classe="????"
            nom=dico["lastname"]
        prenom = dico["firstname"]
        idt = dico["login"]
        return idEleve(idt, nom, prenom, classe)

if __name__ =="__main__":
    dataEleves=sys.argv[1]
    dataChoix=sys.argv[2]
    groupes = groupesAp(dataEleves,dataChoix)
    groupes.toODF("essai.odt")
    os.stdout.write("=============== on a créé essai.odt =================\n")
