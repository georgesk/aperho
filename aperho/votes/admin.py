from django.contrib import admin

from .models import Enseignant, Formation, Horaire, Etudiant, Cours, Inscription

admin.site.register(Enseignant)
admin.site.register(Formation)
admin.site.register(Horaire)
admin.site.register(Cours)
admin.site.register(Inscription)

class EtudiantAdmin (admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'uid')

admin.site.register(Etudiant, EtudiantAdmin)
