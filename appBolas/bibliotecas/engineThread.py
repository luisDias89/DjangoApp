#   Luís Dias 2022   #
import threading
import time
from time import time as Time
trancaVariavel = threading.Lock()
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
    timeLeft=0
    percentLeft=0
    tempoDePausa=0

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

    
    def __init__(self,ser, tempoTreino, qtLancamentos, objLances, cadencia, tipoSequencia):
        super(threadTreino, self).__init__()        # Extende os metodos deste objeto ao da class thread
        self._stop = threading.Event()              # adiciona à variavel _stop o evento thread
        # -----------   Inicialização de variaveis --------------------------
        self.ser=ser                                # recebe o serialPort para dentro do objeto;
        self.qtLancamentos=qtLancamentos            # recebe a quantidade de lancamentos;
        self.objLances=objLances                    # recebe o objeto lances
        self.lancesJson={}
        i=0
        for lance in self.objLances:
            self.lancesJson.update({'lance'+ str(i): lance.nomeLance})
            i=i+1
        
        self.cadencia=cadencia                      # Recebe a cadencia de lançamento
        self.tipoSequencia=tipoSequencia            # Recebe o tipo de Sequancia de lançamento, , (ALEATORIA = 1 SEQUENCIAL = 2)
        self.tempoTreino=tempoTreino                # Recebe o tempo de treino e itribui à variavel da classe
        # normalização do tempo de treino
        inteiro = int(tempoTreino)
        virgula= tempoTreino-inteiro
        tempoNormalizado= (float(virgula)*1.666666)+inteiro
        self.tempoNormalizadoSegundos=tempoNormalizado*3600
        
        



        
    def stop(self):                                 # set da flag para terminar a Thread
        self._stop.set()

    def stopped(self):                              # Retorna a informação se a thread já foi fechada
        return self._stop.is_set()
    
    def set_pause(self):                            # Pausa o processamento dentro da Thread
        if( self.runThread==True):
            self.tic("pause")
        trancaVariavel.acquire()
        self.runThread=False
        trancaVariavel.release()
    
    def set_resume(self):                           # Continua a execução da Thread
        if(self.runThread==False):
            self.totalPausa+=self.toc("pause")           # recebe a quantidade de tempo que esteve pausado, incrementa ao que já tem.
        trancaVariavel.acquire()
        self.runThread=True
        trancaVariavel.release()

    #================================================#
    #       Metodo para comunicar com o GRBL         #
    #       A mensagem que recebe é a mensagem que   #
    #       envia, retorna a primeira mensagem de    #
    #       resposta do GRBL                         #
    def send_to_GRBL(self, msg):
        if self.ser.isOpen():
            self.ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens                                  
            mensagem= msg + '\n'                                # Contrução da mensagem, não apagar o '\n', senão não funciona
            #print('Sending: ' + mensagem)                      # Bloco de depuração
            self.ser.write(mensagem.encode())                        # Bloco de envio de G-CODE
            time.sleep(0.1)                                     
            grbl_out = self.ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
            resposta=grbl_out[0].decode()
            return resposta                                     # Quando pretendemos só o ok, ficamos apenas pela primeira linha [0]
    #=================================================#
    
    # Metodo para aceder às variaveis do GRBL
    def getCoordenadas(self):
        if self.ser.isOpen():                                        # Se a porta serial está aberta
            self.ser.flushInput()                                    # remove toda a data na fila de entrada, só para se focar no pedido seguinte    
            mensagem="?\n"                                           # Pergunta quais as coordenadas atuais (Comando GRBL "?\n")
            self.ser.write(mensagem.encode())                        # Escreve na SerialPort "?\n" para receber as coordenadas
            time.sleep(0.05)                                         # Espera a resposta do arduino
            if  self.ser.inWaiting()>0 :                             # Se tiver algum caracter então executa
                mensagemlida=self.ser.readline()                     # recebe a mensagem e insere na variavel
                SerialPort = mensagemlida.decode()                   # Passa de Byte para string
                #SerialPort=SerialPort[11:]                          # Correção de bug !!!
                SerialPort = SerialPort.replace('<Run|MPos:', "")    # Elimina os primeiros 11 caracteres
                SerialPort = SerialPort.replace('<Idle|MPos:', "")
                SerialPort = SerialPort.replace("|FS:", ",")         # Replaces seguintes é para limpar a mensagem 
                SerialPort = SerialPort.replace(">\r\n", "")
                SerialPort = SerialPort.replace("|WCO:", ",")
                SerialPort = SerialPort.replace("|Ov:", ",")
                arrayEstadoMaquina = SerialPort.split(",")           # Divide o que é separado por , em lista array
                
                if(numpy.size(arrayEstadoMaquina)>2):
                    trancaVariavel.acquire()
                    self.dic = {
                    'X': float(arrayEstadoMaquina[0]), 
                    'Y': float(arrayEstadoMaquina[1]), 
                    'Z': float(arrayEstadoMaquina[2]), 
                    "gateBola": float(arrayEstadoMaquina[3]), 
                    #"rolDir":float(arrayEstadoMaquina[4])
                    }
                    trancaVariavel.release()
                    self.ser.flushInput()                                 # remove data after reading     # Limpa o buffer do SerialPort
                    return self.dic
                
                self.ser.flushInput()                                 # remove data after reading     # Limpa o buffer do SerialPort
                return False




    # Função concluida
    def get_timeleft(self):      
        # O tempo decrescent é dado por timeLeft-(toc("runTime"))+tempoTotaldePause
        # caso esteja na pause então é contabilizado tambem o toc da pause porque ainda não foi aficionado ao tempo total de pausa               
        if(self.runThread==True):
            self.timeLeft= int((self.tempoNormalizadoSegundos - self.toc())+self.totalPausa)
        if( self.runThread==False):
            self.timeLeft= int((self.tempoNormalizadoSegundos - self.toc())+self.totalPausa+self.toc("pause"))
        return self.timeLeft                                       # Retorna o tempo restante do treino
    # Função concluida
    def get_percentleft(self):
        tempoDecorrido=self.tempoNormalizadoSegundos-self.timeLeft
        self.percentLeft=round((tempoDecorrido / self.tempoNormalizadoSegundos)*100, 2)      # Round a 2 casas decimais
        return self.percentLeft                                          # Retorna a percentagem faltante do treino

    def get_LanceAexecutar(self):
        pass
    def get_bolasPorLance(self):
        pass
    def get_bolasLancadasLeft(self):
        pass
    def __baralha():
        pass

    def __go2(self,x,y,z):
        pass


    #================================================#
    # Aqui fica a Thread de controlo dentro da class #
    def run(self):
        
        self.tic()                                  # Momento do inicialização, regista o momento em que é iniciado o treino, antes de entrar no loop
        i=0
        #os lances são iterados de [0 até (len(lances)-1)]
        quantidadeLances=len(self.objLances)-1      
        iteradorLances=0
        
        self.threadLance=ClasseThreadLance(self.ser)
        
        while(True):
            
            if(self.runThread):                                                  #self.runThread -> Variavel de pause da Thread
                #dicCoordenadasAtuais=self.getCoordenadas()                      # Obtem coordendas atuais
                if(self.tipoSequencia==2):                                       # Lances sequenciais
                    # Se for o primeiro lance então
                    if(iteradorLances==0):
                        print("Inicializei")
                        self.threadLance.startLance(
                                        nomeLance=str(self.objLances[0].nomeLance), 
                                        velRoloEsq=int(self.objLances[0].velocidadeRoloEsq), 
                                        velRoloDir=int(self.objLances[0].velocidadeRoloDir), 
                                        angulo_X=int(self.objLances[0].anguloX), 
                                        angulo_Y=int(self.objLances[0].anguloY), 
                                        angulo_Z=int(self.objLances[0].anguloInclinacao), 
                                        cadencia=int(self.cadencia), 
                                        qtBolasLancadas=int(self.qtLancamentos)
                                        )
                        iteradorLances+=1           # Garante que só executa este if uma vez, no posição 0
                    # Se não estiver a correr um lance e o iterador for inferior à quantidade de lances
                    elif((iteradorLances <= quantidadeLances) and self.threadLance.runing == False):
                        self.threadLance.startLance(
                                        nomeLance=str(self.objLances[iteradorLances].nomeLance), 
                                        velRoloEsq=int(self.objLances[iteradorLances].velocidadeRoloEsq), 
                                        velRoloDir=int(self.objLances[iteradorLances].velocidadeRoloDir), 
                                        angulo_X=int(self.objLances[iteradorLances].anguloX), 
                                        angulo_Y=int(self.objLances[iteradorLances].anguloY), 
                                        angulo_Z=int(self.objLances[iteradorLances].anguloInclinacao), 
                                        cadencia=int(self.cadencia), 
                                        qtBolasLancadas=int(self.qtLancamentos)
                                        )
                        iteradorLances+=1
                elif(self.tipoSequencia==1):                           # Lances Aleatórios
                    print("Aleatória")
                    #Retorna um inteiro aleatório N de forma que a <= N <= b        ->    random.randint(a, b))
                    
                    randomint=random.randint(0,len(self.objLances)-1)
                    print(randomint)
                    print(self.objLances[randomint].nomeLance)
                    print(self.lancesJson)


                time.sleep(0.1)
            # Acaba com a Thread se o tempo de treino acabar ou ouver ondem de paragem
            if(self.stopped() or (self.get_timeleft() < 0) or ((iteradorLances-1) > quantidadeLances)):
                #print("O Treino Terminou"  + str(self.stopped()) + str((self.get_timeleft() < 0)) + str((iteradorLances-1) > quantidadeLances))
                self.threadLance.stop()
                break