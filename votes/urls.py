from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^addEleves$', views.addEleves, name='addEleves'),
    url(r'^addProfs$', views.addProfs, name='addProfs'),
    url(r'^addFormation$', views.addFormation, name='addFormation'),
    url(r'^addInscription$', views.addInscription, name='addInscription'),
    url(r'^lesCours$', views.lesCours, name='lesCours'),
    url(r'^enroler$', views.enroler, name='enroler'),
    url(r'^enroleEleveCours$', views.enroleEleveCours, name='enroleEleveCours'),
]
