from django.urls import path
from .views import index, contato, settingsReturn

from django.conf.urls import handler404,handler500
#importa do arquivo de views

from appBolas import views

urlpatterns = [
    path('', index),
    path("modoauto", views.modoauto, name="modoauto"),
    path('vel_mot_esq_aum', views.vel_mot_esq_aum,name='vel_mot_esq_aum'),
    path('contato', contato, name='contato'),
    path('settings', settingsReturn, name='settings')
]