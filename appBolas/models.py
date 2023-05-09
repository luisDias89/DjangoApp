from django.db import models                # importa a biblioteca models
from datetime import date, datetime
from email.policy import default

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




class lance(models.Model):
    #nome no lance
    nomeLance=models.CharField('Nome do lance', max_length=30)
    # angulo de X
    anguloX=models.DecimalField('Angulo em X',max_digits=5, decimal_places=2)
    # angulo de Y
    anguloY=models.DecimalField('Angulo em Y',max_digits=5, decimal_places=2)
    #angulo de inclinação 
    anguloInclinacao=models.DecimalField('Angulo de inclinação',max_digits=5, decimal_places=2)
    # Velocidade do rolo esquerdo
    velocidadeRoloEsq=models.SmallIntegerField('Velocidade do rolo esquerdo',default=0)
    # Velocidade do rolo direito
    velocidadeRoloDir=models.SmallIntegerField('Velocidade do rolo direito',default=0)

    # Nesta função definimos o que retorna quando chamado só pelo objeto que compõe todo o grupo de informação da linha da tabela
    def __str__(self):
        #return f'{self.comandoGRBL}{self.titulo}'
        return self.nomeLance


class treino(models.Model):
    #Nome do treino
    nomeTreino=models.CharField('Nome do Treino',max_length=20)
    # Cria um dependencia muitos para muitos, em que um treino pode ter varios lances escolhiveis, e os lances podem estar em varios treinos
    lances = models.ManyToManyField(lance)

    Qt_bolas_lance=models.IntegerField("Bolas lançadas por lance", default=5)            # Bolas lançadas por cada lance
    maxBolasTreino=models.IntegerField("Maximo de bolas por treino", default=200)        # Maximo de bolas por cada treino
    
    class cadencia(models.IntegerChoices):
            Baixa = 4
            Media = 3
            Alta = 2
            Elevada = 1
    cadenciaTreino = models.IntegerField("Cadencia do treino",choices=cadencia.choices, default=1)
    
    dataCriacao = models.DateTimeField("Data",default=datetime.now, editable=False)

    tempoTreino=models.DecimalField("Tempo de treino em minutos", default=5, max_digits=5, decimal_places=2)

    #Formulario para editar hora e data
    #date = models.DateTimeField("Data",default=datetime.now, blank=True)


    class Seqlances(models.IntegerChoices):
            ALEATORIA = 1
            SEQUENCIAL = 2

    SequenciaLances = models.IntegerField("Sequencia de lances",choices=Seqlances.choices, default=1)
    

    # Definição do tipo de execução dos lances
    '''
        ALEATORIA = 'AL'
    SEQUENCIAL = 'SQ'
    ALEATORIA_SEQUENCIAL = [
        (ALEATORIA, 'Aleatória'),
        (SEQUENCIAL, 'Sequencial'),
    ]
    SequenciaLances = models.CharField('Sequencia de lances',
        max_length=2,
        choices=ALEATORIA_SEQUENCIAL,
        default=ALEATORIA,
    )
    '''
    

    # Nesta função definimos o que retorna quando chamado só pelo objeto que compõe todo o grupo de informação da linha da tabela
    def __str__(self):
        #return f'{self.comandoGRBL}{self.titulo}'
        return self.nomeTreino + " -- Adicionado: " + str(self.dataCriacao.day) +"-"+ str(self.dataCriacao.month) +"-"+ str(self.dataCriacao.year)
