from django.urls import path
from .views import index, contato, homepage, settingsReturn, ajaxRequest

from django.conf.urls import handler404,handler500
#importa do arquivo de views

from appBolas import views

urlpatterns = [
    path('', index),                                                            # Quando vem um pedido do '' browser retorna a funcao index
    path("modoauto", views.modoauto, name="modoauto"),                          # Quando vem um pedido de 'modoauto' browser retorna a funcao modoauto     NÃO UTILIZADO!!!!
    path('contato', contato, name='contato'),                                   # contato -> retorna a funcao homepage       NÃO IMPLEMENTADO!!!!
    path('homepage', homepage, name='home'),                                    # homepage -> retorna a funcao homepage
    path('settings', settingsReturn, name='settings'),                           # settings -> retorna a funcao settings 
    path('ajax_request/', ajaxRequest, name='ajaxRequest'),                       # settings -> retorna a funcao settings 
]