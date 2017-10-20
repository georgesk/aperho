"""
Champ pour définir une « saveur » relative à une barrette
"""

from collections import OrderedDict

class Ventilation:
    """
    Un doublet booléen/nombre ; si le booléen est vrai, le nombre
    est pris en compte
    """
    def __init__(self, actif, nombre):
        """
        Le constructeur
        @param actif booléen ; s'il est vrai le nombre est pris en compte
        @param nombre le nombre de la ventilation
        """
        self.actif=actif
        self.nombre=nombre
        return

    def __str__(self):
        if not self.actif: return "indéf."
        else: return str(self.nombre)

    def incr(self):
        """
        incrémente self.nombre
        @return l'incrément (toujours +1)
        """
        self.nombre+=1
        return 1

    def decr(self):
        """
        décrémente self.nombre sans jamais le rendre négatif
        @return l'incrément (-1, ou 0 si self.nombre était déjà nul)
        """
        if self.nombre > 0:
            self.nombre-=1
            return -1
        return 0

class SaveurDict:
    """
    Un « dictionnaire de saveurs » avec un effectif total.
    Si aucune des saveurs n'est active, seul l'effectif total est
    considéré. Par contre dès qu'une saveur au moins est active,
    on s'assure que la somme des nombres dans chaque saveur
    correspond à l'effectif total.
    """
    def __init__(self, effectif, saveurs):
        """
        Le constructeur
        @param effectif l'effectif maximal
        @param categories un SortedDict nom -> Ventilation
        """
        self.effectif=effectif
        self.saveurs=saveurs
        self.ajusteEffectifs()
        return

    def __str__(self):
        l=["  %s: %s\n" %(s, self.saveurs[s]) for s in self.saveurs]
        return "Saveurdict:\n"+"".join(l)
    
    def isMixte(self):
        """
        @return vrai si seul l'effectif total compte (aucune saveur
        n'est active.
        """
        result=True
        for s in self.saveurs:
            if self.saveurs[s].actif:
                result=False
                break
        return result

    def ajusteEffectifs(self):
        """
        S'assure bien qu'on retrouve l'effectif total comme somme des
        effectifs de chaque saveur active
        """
        if self.isMixte():
            return
        t=sum([self.saveurs[s].nombre for s in self.saveurs if self.saveurs[s].actif])
        while t < self.effectif:
            for s in self.saveurs:
                if self.saveurs[s].actif and t < self.effectif:
                    t += self.saveurs[s].incr()
        while t > self.effectif:
            for s in self.saveurs:
                if self.saveurs[s][0] and t > self.effectif:
                    t += self.saveurs[s].decr()
        assert(t==self.effectif)
        return
                    

if __name__=="__main__":
    sd=SaveurDict(18,OrderedDict([
        ("tes",Ventilation(True,0)),
        ("tl",Ventilation(True, 0)),
        ("ts",Ventilation(False,0)),
        ("tstmg",Ventilation(False,0)),
    ]))
    print(sd)
    
