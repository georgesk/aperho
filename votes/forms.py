from django import forms

class dureeField(forms.IntegerField):
    def validate(self, value):
       super(dureeField, self).validate(value)
       if value not in (1,2):
           raise forms.ValidationError("un cours dure 1 ou 2 heures.")

class capaciteField(forms.IntegerField):
    def __init__(self, *args, **kwargs):
        forms.IntegerField.__init__(self, *args, **kwargs)
        self.isSuperUser=False
        return
    def validate(self, value):
       super(capaciteField, self).validate(value)
       minCap=16
       maxCap=25
       if self.isSuperUser:
           minCap=0
           maxCap=500
       if value < minCap:
           raise forms.ValidationError("Trop peu d'élèves.")
       elif value > maxCap:
           raise forms.ValidationError("Trop d'élèves.")

class editeCoursForm(forms.Form):
    def __init__(self, *args, **kwargs ):
        self.isSuperUser=kwargs.pop("isSuperUser",False)
        forms.Form.__init__(self, *args, **kwargs)
        for i in range(1,1+5):
            n="nom_"+str(i)
            setattr(self,n,kwargs["initial"][n])
        if self.isSuperUser:
            self.fields["capacite"].isSuperUser=True
        return
    titre = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={
            "size": 61,
        })
    )
    contenu = forms.CharField(
        max_length=1400,
        widget=forms.Textarea(attrs={
            "cols": 80,
            "rows": 5,
        })
    )
    duree = dureeField()
    public_designe=forms.BooleanField(required=False)
    back=forms.CharField(max_length=80, widget=forms.HiddenInput())
    public_designe_initial=forms.BooleanField(required=False, widget=forms.HiddenInput())
    is_superuser=forms.BooleanField(required=False, widget=forms.HiddenInput())

    effectif_total = capaciteField()

    nom_1 = "nom 1"
    actif_1 = forms.BooleanField(help_text="actif/inactif")
    ventilation_1 = forms.IntegerField(min_value=0,max_value=99, help_text='0 à 99')

    nom_2 = "nom 2"
    actif_2 = forms.BooleanField(help_text="actif/inactif")
    ventilation_2 = forms.IntegerField(min_value=0,max_value=99, help_text='0 à 99')

    nom_3 = "nom 3"
    actif_3 = forms.BooleanField(help_text="actif/inactif")
    ventilation_3 = forms.IntegerField(min_value=0,max_value=99, help_text='0 à 99')

    nom_4 = "nom 4"
    actif_4 = forms.BooleanField(help_text="actif/inactif")
    ventilation_4 = forms.IntegerField(min_value=0,max_value=99, help_text='0 à 99')

    nom_5 = "nom 5"
    actif_5 = forms.BooleanField(help_text="actif/inactif")
    ventilation_5 = forms.IntegerField(min_value=0,max_value=99, help_text='0 à 99')


    def clean(self):
        cleaned_data = super(editeCoursForm, self).clean()
        if cleaned_data["public_designe"] !=  cleaned_data["public_designe_initial"] and not cleaned_data["is_superuser"]:
            msg="Seul le gestionnaire du site peut modifier la critère de public désigné. Préparez une liste d'élèves et contactez-le."
            self.add_error("public_designe", msg)
        return cleaned_data
