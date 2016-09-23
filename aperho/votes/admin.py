from django.contrib import admin

from .models import Enseignant, Formation, Horaire, Etudiant, Cours, Inscription

admin.site.register(Enseignant)
admin.site.register(Formation)
admin.site.register(Horaire)
admin.site.register(Inscription)

class EtudiantAdmin (admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'classe', 'uid')

admin.site.register(Etudiant, EtudiantAdmin)

class CoursAdmin (admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        """
        Don't allow adding new Cours Enseignant or Horaire
        """
        form = super(CoursAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['enseignant'].widget.can_add_related = False
        form.base_fields['horaire'].widget.can_add_related = False
        return form
    
admin.site.register(Cours, CoursAdmin)
