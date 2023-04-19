from django.urls import path
from .views import index, contato, homepage, settingsReturn

from django.conf.urls import handler404,handler500
#importa do arquivo de views

from appBolas import views

urlpatterns = [
    path('', index),                                                            # Quando vem um pedido do '' browser retorna a funcao index
    path("modoauto", views.modoauto, name="modoauto"),                          # Quando vem um pedido de 'modoauto' browser retorna a funcao modoauto     NÃO UTILIZADO!!!!
    path('vel_mot_esq_aum', views.vel_mot_esq_aum,name='vel_mot_esq_aum'),      # vel_mot_esq_aum -> retorna a funcao vel_mot_esq_aum
    path('contato', contato, name='contato'),                                   # contato -> retorna a funcao homepage       NÃO IMPLEMENTADO!!!!
    path('homepage', homepage, name='homepage'),                                # homepage -> retorna a funcao homepage
    path('settings', settingsReturn, name='settings')                           # settings -> retorna a funcao settings 
]