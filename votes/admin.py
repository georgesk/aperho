from django.contrib import admin

from .models import Enseignant, Formation, Horaire, Etudiant, Cours, \
    Inscription, Ouverture, Orientation, CoursOrientation, Cop, \
    InscriptionOrientation

admin.site.register(Horaire)
admin.site.register(Ouverture)
admin.site.register(Cop)

class InscriptionOrientationAdmin(admin.ModelAdmin):
 search_fields = [
     "etudiant__nom", "cours__cop__nom", "cours__prof__nom", "cours__debut"
 ]
   
admin.site.register(InscriptionOrientation, InscriptionOrientationAdmin)

class CoursOrientationAdmin(admin.ModelAdmin):
    list_filter = ("cop", "debut", "formation", "prof")
    search_fields = ['cop__nom','debut','prof__nom']
admin.site.register(CoursOrientation, CoursOrientationAdmin)

    
class OrientationAdmin (admin.ModelAdmin):
    search_fields = ['etudiant__nom']
    list_filter = ("choix", "ouverture")
    
admin.site.register(Orientation, OrientationAdmin)

class FormationAdmin (admin.ModelAdmin):
    list_filter = ("duree","public_designe")
    
admin.site.register(Formation, FormationAdmin)

class InscriptionAdmin (admin.ModelAdmin):
    search_fields = ['etudiant__nom','cours__enseignant__nom']
    
admin.site.register(Inscription, InscriptionAdmin)

class EtudiantAdmin (admin.ModelAdmin):
    search_fields = ['nom']
    list_display = ('nom', 'prenom', 'classe', 'uidNumber', 'uid')
    list_filter = ("classe",)

admin.site.register(Etudiant, EtudiantAdmin)

class EnseignantAdmin(admin.ModelAdmin):
    search_fields = ['nom']
    
admin.site.register(Enseignant, EnseignantAdmin)

class CoursAdmin (admin.ModelAdmin):
    list_filter = ("horaire","enseignant", "ouverture")
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Don't allow adding new Cours Enseignant or Horaire
        """
        form = super(CoursAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['enseignant'].widget.can_add_related = False
        form.base_fields['horaire'].widget.can_add_related = False
        return form
    
admin.site.register(Cours, CoursAdmin)
