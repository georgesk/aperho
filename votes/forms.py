from django import forms

class dureeField(forms.IntegerField):
    def validate(self, value):
       super(dureeField, self).validate(value)
       if value not in (1,2):
           raise forms.ValidationError("un cours dure 1 ou 2 heures.")

class capaciteField(forms.IntegerField):
    def validate(self, value):
       super(capaciteField, self).validate(value)
       minCap=16
       maxCap=25
       if value < minCap:
           raise forms.ValidationError("Trop peu d'élèves.")
       elif value > maxCap:
           raise forms.ValidationError("Trop d'élèves.")

class editeCoursForm(forms.Form):
    titre = forms.CharField(
        max_length=80,
        widget=forms.TextInput(attrs={
            "size": 61,
        })
    )
    contenu = forms.CharField(
        max_length=400,
        widget=forms.Textarea(attrs={
            "cols": 80,
            "rows": 5,
        })
    )
    duree = dureeField()
    capacite=capaciteField()
    public_designe=forms.BooleanField(required=False)
    back=forms.CharField(max_length=80, widget=forms.HiddenInput())
    public_designe_initial=forms.BooleanField(required=False, widget=forms.HiddenInput())
    is_superuser=forms.BooleanField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(editeCoursForm, self).clean()
        if cleaned_data["public_designe"] !=  cleaned_data["public_designe_initial"] and not cleaned_data["is_superuser"]:
            msg="Seul le gestionnaire du site peut modifier la critère de public désigné. Préparez une liste d'élèves et contactez-le."
            self.add_error("public_designe", msg)
        return cleaned_data
