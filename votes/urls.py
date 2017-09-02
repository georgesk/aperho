from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^addEleves$', views.addEleves, name='addEleves'),
    url(r'^addProfs$', views.addProfs, name='addProfs'),
    url(r'^delProfBarrette$', views.delProfBarrette, name='delProfBarrette'),
    url(r'^addUnProf$', views.addUnProf, name='addUnProf'),
    url(r'^changeSalle$', views.changeSalle, name='changeSalle'),
    url(r'^addInscription$', views.addInscription, name='addInscription'),
    url(r'^lesCours$', views.lesCours, name='lesCours'),
    url(r'^enroler$', views.enroler, name='enroler'),
    url(r'^enroleEleveCours$', views.enroleEleveCours, name='enroleEleveCours'),
    url(r'^cop$', views.cop, name='cop'),
    url(r'^listClasse$', views.listClasse, name='listClasse'),
    url(r'^delClasse$', views.delClasse, name='delClasse'),
    url(r'^delCours$', views.delCours, name='delCours'),
    url(r'^addBarrette$', views.addBarrette, name='addBarrette'),
    url(r'^delBarrette$', views.delBarrette, name='delBarrette'),
    url(r'^editBarrette$', views.editBarrette, name='editBarrette'),
    url(r'^addOuverture$', views.addOuverture, name='addOuverture'),
    url(r'^delOuverture$', views.delOuverture, name='delOuverture'),
    url(r'^editOuverture$', views.editOuverture, name='editOuverture'),
    url(r'^editeCours$', views.editeCours, name='editeCours'),
]
