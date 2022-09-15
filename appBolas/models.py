from django.db import models                # importa a biblioteca models

# Cria o teu modelo de Base de Dados Aqui

class SettingsGRBL(models.Model):
    titulo=models.CharField('titulo', max_length=100)
    textoInformação = models.CharField('textoInformação', max_length=2000)          # Cria a coluna para inserir a informação referente à configuração
    valorDefault= models.IntegerField('Default')                                    # Default de cada Configuração
    valorMin= models.IntegerField('Min')                                            # Valor minimo de cada Configuração
    valorMax= models.IntegerField('Max')                                            # Valor minimo de cada Configuração
    comandoGRBL= models.CharField('comandoGRBL', max_length=100)                    # Qual o comando para receber esta configuração

    # Nesta função definimos o que retorna quando chamado só pelo objeto que compõe todo o grupo de informação da linha da tabela
    def __str__(self):
        #return f'{self.comandoGRBL}{self.titulo}'
        return self.comandoGRBL