"""
Champ pour définir une « saveur » relative à une barrette
"""

from django.db import models

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

    def deconstruct(self):
        """
        Le déconstructeur, tel que conseillé à
        https://docs.djangoproject.com/en/1.10/topics/migrations/#migration-serializing
        @return un tuple (path, args, kwargs)
        """
        return (
            "votes.saveurField.Ventilation",
            [self.actif, self.nombre],
            dict()
        )

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
        @param categories un dictionnaire nom -> Ventilation
        """
        self.effectif=effectif
        self.saveurs=saveurs
        self.ajusteEffectifs()
        return

    def deconstruct(self):
        """
        Le déconstructeur, tel que conseillé à
        https://docs.djangoproject.com/en/1.10/topics/migrations/#migration-serializing
        @return un tuple (path, args, kwargs)
        """
        return (
            "votes.saveurField.SaveurDict",
            [self.effectif, self.saveurs],
            dict()
        )

    def __str__(self):
        l=["  %s: %s\n" %(s, self.saveurs[s]) for s in sorted(self.saveurs)]
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

def parse_saveurDict(saveurDictString):
    """
    Désérialise un objet SaveursDict de 5 saveurs au maximum.

    Deux caractères donnent l'effectif total, puis 5 fois de suite
    on cherche 5 caractère de nom de saveur, puis un caractère 0/1
    actif, et deux caractères pour le nombre.
    """
    effectif=int(saveurDictString[0:2])
    saveurDict=dict()
    for i in range(5):
        nom=saveurDictString[2+8*i:7+8*i].strip()
        if nom:
            saveurDict[nom]=Ventilation(
                "0" != saveurDictString[7+8*i:8+8*i],
                int(saveurDictString[8+8*i:10+8*i])
            )
    return SaveurDict(effectif,saveurDict)
    
    

class SaveurDictField(models.Field):
    description = "Un dictionnaire de saveurs (pas plus de cinq) pour l'AP"

    def __init__(self, *args, **kwargs):
        """
        Le constructeur
        """
        # max 5 saveurs, sur 8 caractères chacune,
        # plus 2 caractères d'effectif tital
        kwargs['max_length'] = 42
        if 'saveurDict' in kwargs:
            saveurDict=kwargs.pop('saveurDict')
        else:
            saveurDict=SaveurDict(0,dict())
        super(SaveurDictField, self).__init__(*args, **kwargs)
        self.saveurDict=saveurDict
        return

    def deconstruct(self):
        name, path, args, kwargs = super(SaveurDictField, self).deconstruct()
        del kwargs["max_length"]
        kwargs['saveurDict'] = self.saveurDict
        return name, path, args, kwargs
    
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        return parse_saveurDict(value)

    def to_python(self, value):
        if isinstance(value, SaveurDict):
            return value
        if value is None:
            return value
        return parse_saveurDict(value)

    def get_prep_value(self, saveurDict):
        if not saveurDict:
            saveurDict=SaveurDict(0,dict())
        if not 0 <= saveurDict.effectif <= 99:
            raise ValidationError("Effectif total incorrect : %s" % saveurDict.effectif)
        result="%02d" % saveurDict.effectif
        saveurs=sorted(saveurDict.saveurs.keys())
        savList=[]
        for i in range(5):
            sav=""
            if i < len(saveurs):
                nom=saveurs[i]
                if len(nom) > 5:
                    raise ValidationError("nom de saveur trop long : %s" % nom)
                sav="%5s" % nom
                if saveurDict[nom].actif:
                    sav+="1"
                else:
                    sav+="0"
                nombre=saveurDict[nom].nombre
                if not 0 <= nombre <= 99:
                    raise ValidationError("Effectif ventilé incorrect : %s" % nombre)
                sav+="%02d" % nombre
            else: # plus de saveurs, mais on doit aller jusqu'à 5
                sav=" "*8
            savList.append(sav)
        # fin de la boucle de cinq
        result+="".join(savList)
                    
        return result
    
    def get_internal_type(self):
        return 'CharField'
    
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
  
    
if __name__=="__main__":
    sd=SaveurDict(18,{
        "tes":   Ventilation(True,0),
        "tl":    Ventilation(True, 0),
        "ts":    Ventilation(False,0),
        "tstmg": Ventilation(False,0),
    })
    print(sd)
    
