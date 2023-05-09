#   Luís Dias 2022   #
import threading
import time
from time import time as Time
memoryLOCK = threading.Lock()
import random
import numpy


from .objLance import ClasseThreadLance
class threadTreino(threading.Thread):
    """Thread class com metodo de stop(). A thread precisa checar 
    regularmente pela condição de stopped() ."""
    
    runThread=True                                  # Variavel que suporta a função pause e resume da Thread, !não apagar
    tempInicial=0                                   # Quando a Thread inicia regista nesta variavel qual o tempo de inicio
    tempoTreino=0                                   # Quando entra no __init__ regista o tempo do treino para o id selecionado
    tempoNormalizadoSegundos=0                      # Da base de dados vem o tempo no formato H:S, aqui já recebemos o tempo em segundos para descontar no toc() diretamente
    MaxBolasTreino=0
    timeLeft=0
    percentLeft=0
    tempoDePausa=0
    str_getAexecutar= ""

    #Variaveis auxiliares para contabilizar o tempo de pausa
    totalPausa=0
    init_time_pausa=0

    def tic(self,ponteiro="runTime"):
        if(ponteiro=="pause"):
            self.init_time_pausa = Time()
        elif(ponteiro=="runTime"):
            self.tempInicial = Time()
        return Time()

    def toc(self,ponteiro="runTime"):
        if(ponteiro=="pause"):
            delta_t = Time() - self.init_time_pausa
        elif(ponteiro=="runTime"):
            delta_t = Time() - self.tempInicial
        #print("Elapser ime is " + str(delta_t) + " second.")
        return delta_t

    
    def __init__(self,ser, tempoTreino, qtLancamentos, objLances, cadencia, tipoSequencia,MaxBolasTreino):
        super(threadTreino, self).__init__()        # Extende os metodos deste objeto ao da class thread
        self._stop = threading.Event()              # adiciona à variavel _stop o evento thread
        # -----------   Inicialização de variaveis --------------------------
        self.ser=ser                                # recebe o serialPort para dentro do objeto;
        self.qtLancamentos=qtLancamentos            # recebe a quantidade de lancamentos;
        self.MaxBolasTreino=MaxBolasTreino
        self.objLances=objLances                    # recebe o objeto lances
        self.lancesJson={}
        i=0
        quantidadeLancamentos=0
        for lance in self.objLances:
            self.lancesJson.update({'lance'+ str(i): lance.nomeLance})
            quantidadeLancamentos+=qtLancamentos
            i=i+1
        
        self.cadencia=cadencia                      # Recebe a cadencia de lançamento
        self.tipoSequencia=tipoSequencia            # Recebe o tipo de Sequancia de lançamento, , (ALEATORIA = 1 SEQUENCIAL = 2)
        self.tempoTreino=tempoTreino                # Recebe o tempo de treino e itribui à variavel da classe
    
        
        # normalização do tempo de treino
        inteiro = int(tempoTreino)                              # 
        virgula= tempoTreino-inteiro                            # separa o que esta para alem da virgula
        tempoNormalizado= (float(virgula)*1.666666)+inteiro     # Normaliza o tempo de treino
        self.tempoNormalizadoSegundos=tempoNormalizado*60       # passa de minutos para segundos
        
        
    def stop(self):                                 # set da flag para terminar a Thread
        self._stop.set()

    def stopped(self):                              # Retorna a informação se a thread já foi fechada
        return self._stop.is_set()
    
    def set_pause(self):                           
        '''
        Pausa o processamento dentro da Thread, registo do tempo
        '''
        if( self.runThread==True):                  # se a thead estiver a correr então 
            self.tic("pause")                               # regista o tempo em que foi feita a pausa
            memoryLOCK.acquire()                        # tranca a variavel para não haver conflitos de thread
            self.runThread=False                            # e pára o loop da THREAD
            memoryLOCK.release()                        # volta a libertar a variavel para processamento da thread
    
    def set_resume(self):                           # Continua a execução da Thread
        '''
        Faz resume se a thead estiver parada, regista o tempo
        '''
        if(self.runThread==False):
            self.totalPausa+=self.toc("pause")              # recebe a quantidade de tempo que esteve pausado, incrementa ao que já tem.
            memoryLOCK.acquire()                        # tranca a variavel para não haver conflitos de thread
            self.runThread=True                             # continua loop da THREAD
            memoryLOCK.release()                        # volta a libertar a variavel para processamento da thread


    def get_timeleft(self):      
        # O tempo decrescent é dado por timeLeft-(toc("runTime"))+tempoTotaldePause
        # caso esteja na pause então é contabilizado tambem o toc da pause porque ainda não foi aficionado ao tempo total de pausa               
        if(self.runThread==True):
            self.timeLeft= int((self.tempoNormalizadoSegundos - self.toc())+self.totalPausa)
        if( self.runThread==False):
            self.timeLeft= int((self.tempoNormalizadoSegundos - self.toc())+self.totalPausa+self.toc("pause"))
        return self.timeLeft                                       # Retorna o tempo restante do treino
    

    def get_percentleft(self):
        tempoDecorrido=self.tempoNormalizadoSegundos-self.timeLeft
        self.percentLeft=round((tempoDecorrido / self.tempoNormalizadoSegundos)*100, 2)      # Round a 2 casas decimais
        return self.percentLeft                                                              # Retorna a percentagem faltante do treino
        
        # O erro da percentagem errada é devido ao tempo de ciclo não contabilizar quantas bola são lançadas e a cadencia delas.
        # Deve portanto verificar qual demora menos tempo, e atribuir a self.tempoNormalizadoSegundos, que é a variavel que recebe o tempo do lançamento 

    def get_Aexecutar(self):
        """
        Durante a execução do treino retorna qual o lance que está a 
        ser executado em tempo real.
        """
        # Tranca a variavel que pode estar a ser escrita na THREAD para guardar numa memoria buffer e fazer return
        memoryLOCK.acquire()                        # tranca a variavel para não haver conflitos de thread
        buffer= self.str_getAexecutar
        memoryLOCK.release()                        # volta a libertar a variavel para processamento da thread
        return buffer
    
    # Por implementar @LuisDias
    def get_bolasPorLance(self):
        pass

    # Por implementar @LuisDias
    def get_bolasLancadasLeft(self):
        pass

    # Por implementar @LuisDias
    def __baralha():
        pass

    # Por implementar @LuisDias
    def __go2(self,x,y,z):
        pass


    #================================================#
    # Aqui fica a Thread de controlo dentro da class #
    def run(self):
        
        self.tic()                                  # Momento do inicialização, regista o momento em que é iniciado o treino, antes de entrar no loop
        i=0
        iteradorGrafset = 0
        quantidadeLances=len(self.objLances)-1                                   # os lances são iterados de [0 até (len(lances)-1)]
        iteradorLances=0                                                         # Inicializa o iterador
        
        self.threadLance=ClasseThreadLance(self.ser)                             # Cria um objeto da classe thead lance para executar lance a lance, enquato os itera.
                                                                                 # importante, passa o objeto serialPort para ter controlo do GRBL
        
        # ============ LOOP DE CONTROLO DOS LANCES ==============
        while(True):
            
            if(self.runThread):                                                                              # Se nao estiver em pausa  
                self.threadLance.resume()                                                                       # Força resume na Thread lance                                  
                if(self.tipoSequencia==2):                        # {SEQUENCIAL} (2-> treino com lances Sequencial)         
                                       
                    # Implementação de Grafset em Python de lances sequenciais
                    
                    # 0 -> Iterador lance a 0 ,  "Temporário" atualiza estado do lançador para o front end
                    # 1 -> Inicialização do grafset, com verificação da lance a executar 
                    # 2 -> Comando para inicial lance
                    # 3 -> Atualiza para o Front End qual o nome do lance
                    # 4 -> Decisão de lançar novo lance ou saltar para o reset do grafset
                    # 5 -> Reset das variáveis e saida do Grafset
                    if iteradorGrafset == 0: 
                        """
                        STEP 0
                        """        
                        # Inicialização das variaveis  
                        self.str_getAexecutar="Referenciação do lançador"                           # Envia ao front end o que está a executar                                           # Inicializa o iterador de lances
                        iteradorBolas = 0
                        lançaQT=0 
                        iteradorLances=0 
                        #salta para o proximo passo
                        iteradorGrafset += 1
                    elif iteradorGrafset == 1:
                        """
                        STEP 1
                        """  
                        if( iteradorLances >= quantidadeLances):                                   # Quando o iterador de lances for igual ou superior ao máximo, então
                            iteradorLances=0                                                            # Reinicia a sequencia
                        
                        if(iteradorBolas+self.qtLancamentos<self.MaxBolasTreino):                  # se o proximo incremento for inferior ao maximo possivel
                            lançaQT = self.qtLancamentos                                                # e cria a variavel com a qt laçamentos
                            iteradorBolas += lançaQT                                                    # Incrementa o numero de bolas normal registado na DB
                            iteradorGrafset += 1                                                        # Continua para o passo seguinte do grafset
                        elif(self.MaxBolasTreino-iteradorBolas ==0):                               # Caso não possa incrementar mais
                            iteradorGrafset=4                                                           # não lança, Salta para o grafset de tomada de decisão       
                        else:                                                                      # senão
                            lançaQT = self.MaxBolasTreino-iteradorBolas                                 # e cria a variavel com a qt laçamentos
                            iteradorBolas += lançaQT                                                    # incrementa a quantidade de bolas que falta até ao maximo
                            iteradorGrafset += 1                                                        # Continua para o passo seguinte do grafset
                    elif iteradorGrafset == 2:
                        """
                        STEP 2
                        """ 
                        self.threadLance.startLance(                                                                   
                                        nomeLance=str(self.objLances[iteradorLances].nomeLance),                                    
                                        velRoloEsq=int(self.objLances[iteradorLances].velocidadeRoloEsq), 
                                        velRoloDir=int(self.objLances[iteradorLances].velocidadeRoloDir), 
                                        angulo_X=int(self.objLances[iteradorLances].anguloX), 
                                        angulo_Y=int(self.objLances[iteradorLances].anguloY), 
                                        angulo_Z=int(self.objLances[iteradorLances].anguloInclinacao), 
                                        cadencia=int(self.cadencia), 
                                        qtBolasLancadas=int(lançaQT)
                                        )      
                        iteradorGrafset += 1
                    elif iteradorGrafset == 3: 
                        """
                        STEP 3
                        """ 
                        self.str_getAexecutar=str(self.objLances[iteradorLances].nomeLance)
                        iteradorGrafset += 1
                    elif iteradorGrafset == 4:
                        """
                        STEP 4
                        """
                        if(self.threadLance.runing == False):
                            if (self.MaxBolasTreino-iteradorBolas <= 0 or (self.get_timeleft() < 0)):   # Se já lançou todas as bolas ou já passou o tempo de treino
                                iteradorGrafset += 1                                                        # Para o treino continuando no grafset
                            else:                                                                       # caso contrario
                                iteradorLances += 1                                                         # Incrementa o lance
                                iteradorGrafset = 1                                                         #  volta a lançar, passo 1


                    elif iteradorGrafset == 5:
                        """
                        STEP 5
                        """
                        # Reset às variaveis do grafset
                        iteradorGrafset = 0
                        # Para o lance
                        self.stop() 
                    else:
                        print("Iterador Grafset" + str(iteradorGrafset))
                
                elif(self.tipoSequencia==1):                      # {ALEATORIO}  (1-> treino com lances Aleatorio)                     
                    # Implementação de Grafset em Python de lances aleatórios
                    
                    # 0 -> Iterador lance a 0 ,  "Temporário" atualiza estado do lançador para o front end
                    # 1 -> Inicialização do grafset, com randomInt do lance 
                    # 2 -> Comando para inicial lance
                    # 3 -> Atualiza para o Front End qual o nome do lance
                    # 4 -> Decisão de lançar novo lance ou saltar para o reset do grafset
                    # 5 -> Reset das variáveis e saida do Grafset

                    if iteradorGrafset == 0: 
                        """
                        STEP 0
                        """        
                        # Inicialização das variaveis  
                        self.str_getAexecutar="Referenciação do lançador"                           # Envia ao front end o que está a executar                                           # Inicializa o iterador de lances
                        iteradorBolas = 0
                        iteradorGrafset += 1
                        lançaQT=0               
                    elif iteradorGrafset == 1:
                        """
                        STEP 1
                        """  
                        randomint=random.randint(0,quantidadeLances)                               # Recebe um numero random dentro da quantidade de lances
                        iteradorGrafset += 1                                                       # Incrementa a quantidade de bolas lançadas
                        if(iteradorBolas+self.qtLancamentos<self.MaxBolasTreino):                  # se o proximo incremento for inferior ao maximo possivel
                            lançaQT = self.qtLancamentos                                                # e cria a variavel com a qt laçamentos
                            iteradorBolas += lançaQT                                                    # Incrementa o numero de bolas normal registado na DB
                            
                        elif(self.MaxBolasTreino-iteradorBolas ==0):                               # Caso não possa incrementar mais
                            iteradorGrafset=4                                                           # não lança, Salta para o grafset de tomada de decisão       
                        else:                                                                      # senão
                            lançaQT = self.MaxBolasTreino-iteradorBolas                                 # e cria a variavel com a qt laçamentos
                            iteradorBolas += lançaQT                                                    # incrementa a quantidade de bolas que falta até ao maximo
                            
                    elif iteradorGrafset == 2:
                        """
                        STEP 2
                        """ 
                        self.threadLance.startLance(                                                                   
                                        nomeLance=str(self.objLances[randomint].nomeLance),                                    
                                        velRoloEsq=int(self.objLances[randomint].velocidadeRoloEsq), 
                                        velRoloDir=int(self.objLances[randomint].velocidadeRoloDir), 
                                        angulo_X=int(self.objLances[randomint].anguloX), 
                                        angulo_Y=int(self.objLances[randomint].anguloY), 
                                        angulo_Z=int(self.objLances[randomint].anguloInclinacao), 
                                        cadencia=int(self.cadencia), 
                                        qtBolasLancadas=int(lançaQT)
                                        )      
                        iteradorGrafset += 1
                    elif iteradorGrafset == 3: 
                        """
                        STEP 3
                        """  
                        self.str_getAexecutar=str(self.objLances[randomint].nomeLance)
                        iteradorGrafset += 1
                    elif iteradorGrafset == 4:
                        """
                        STEP 4
                        """  
                        if(self.threadLance.runing == False):
                            # Se já lançou todas as bolas ou já passou o tempo de treino
                            if (self.MaxBolasTreino-iteradorBolas <= 0 or (self.get_timeleft() < 0)): 
                                iteradorGrafset += 1                            # Para o treino continuando no grafset
                            else:
                                iteradorGrafset = 1                             # caso contrario volta a lançar


                    elif iteradorGrafset == 5:
                        """
                        STEP 5
                        """ 
                        # Reset às variaveis do grafset
                        iteradorGrafset = 0
                        randomint = 0
                        # Para o lance
                        self.stop() 
                    else:
                        print("Grafset Overflow engineThread.py")                                                

                time.sleep(0.1)                                                                                         # Verifica este estados 10 vezes por segundo
            else:
                self.threadLance.pausar()
            # Acaba com a Thread se o tempo de treino acabar ou houver ordem de paragem
            if(self.stopped() or (self.get_timeleft() < 0)):                                                            # Se alguem parar o lance ou acabar o tempo .. 
                self.threadLance.stop() 
                self.stop()                                                                                # .. ou o iterador for superior a quantidade de lances
                self.str_getAexecutar=""
                print("SAIU DA TREATH TREINO!!!!")
                break                                                                                                   # entao faz stop ao lance e sai da thread