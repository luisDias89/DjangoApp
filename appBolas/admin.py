from django.contrib import admin

# Register your models here.

from .models import SettingsGRBL

# Class que define as colunas que são apresentadas na Vista Admin
class configuracaoColunas(admin.ModelAdmin):
    list_display=('comandoGRBL','titulo','valorMin','valorMax','valorDefault')

admin.site.register(SettingsGRBL,configuracaoColunas)
