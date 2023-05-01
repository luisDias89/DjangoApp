from ast import arg
import threading
from turtle import goto
import serial
import time
import numpy
from time import time as Time
import threading
from .machine_lb import *



class ClasseThreadLance(threading.Thread):
    memoryLOCK=threading.Lock()
    runing=True
    quantidadeLances = 4
    iteradorLances = 0
    #setPointX = 23
    #setPointY = 50
    #setPointZ = -60

    # Estes valores deveram estar num ficheiro .py com configurações gerais da máquina
    print(angulo)
    print(maximo)

    def __init__(self,ser):
        super(ClasseThreadLance, self).__init__()            # Extende os metodos deste objeto ao da class thread
        self._stop = threading.Event()                       # adiciona à variavel _stop o evento thread
        # Recebe as variaveis para dentro do objeto.
        self.ser=ser 
        # Referenciação dos eixos
        
        
    def stop(self):                                         # set da flag para terminar a Thread
        self._stop.set()
    
    def startLance(self, nomeLance, velRoloEsq, velRoloDir, angulo_X, angulo_Y, angulo_Z, cadencia, qtBolasLancadas):
        
        self.nomeLance=nomeLance 
        self.velRoloEsq=velRoloEsq 
        self.velRoloDir=velRoloDir
        self.angulo_X=angulo_X    
        self.angulo_Y=angulo_Y   
        self.angulo_Z=angulo_Z 
        self.cadencia=cadencia
        self.qtBolasLancadas=qtBolasLancadas

        if(self.runing and (not self.stopped())):           # se o Thread não estiver parada então coloca em funcionamento
            self.lb_home()
            print("ACABEI O HOMING!!!!!!")
            self.start()
            print("START LANCE!!!!!!")
        else:
            self.runing=True
    
    def restartThread(self, nomeLance, velRoloEsq, velRoloDir, angulo_X, angulo_Y, angulo_Z, cadencia, qtBolasLancadas):
        self.runing=True                            # Aceita novos valores e coloca o ciclo da Thread novamente em funcionamento
        pass

    def pausar(self):
        #ser.write(b"!\n")
        self.pause=True
    
    def resume(self):
        #ser.write(b"~\n")
        self.pause=False

    def stopped(self):                              # Retorna a informação se a thread já foi fechada
        return self._stop.is_set()

    startTime = 0
    def tic(self):
        global startTime
        self.start = Time()
        return Time()

    def toc(self):
        delta_t = Time() - self.start
        return delta_t
    
    def get_nomeLance(self):
        return self.nomeLance

    def get_bolasLeft(self):
        bolasLeft= self.qtBolasLancadas-self.iteradorLances
        if (bolasLeft>=0):
            return bolasLeft
        else:
            return 0
    
    def get_percentLeft_porbolas(self):
        bolasLeft = (self.iteradorLances/self.qtBolasLancadas)*100
        if (bolasLeft>=0 and bolasLeft<=100):
            return bolasLeft
        elif(bolasLeft>100):
            return 100
        else:
            return 0

    def send_to_GRBL(self,msg):
        if self.ser.isOpen():
            # Remove o buffer de entrada, caso existam mensagens
            self.ser.flushInput()
            mensagem = msg + "\n"
            # Bloco de envio de G-CODE
            self.ser.write(mensagem.encode())
            # Tenta comunicar a True para iniciar a comunicação, repetidamente até receber "OK"
            TentaComunicar = True
            while (TentaComunicar):
                time.sleep(0.05)
                if self.ser.inWaiting() > 0:                                   # Se se algum caracter já estiver no buffer executa
                    # Lee todas as linhas que gera como resposta do GRBL
                    grbl_out = self.ser.readlines()
                    TentaComunicar = False
                    return grbl_out


    def getCoordenadas(self):
        if self.ser.isOpen():                                        # Se a porta serial está aberta
            # remove toda a data na fila de entrada, só para se focar no pedido seguinte
            self.ser.flushInput()
            # Pergunta quais as coordenadas atuais (Comando GRBL "?\n")
            mensagem = "?\n"
            # Escreve na SerialPort "?\n" para receber as coordenadas
            self.ser.write(mensagem.encode())
            # Espera a resposta do arduino
            time.sleep(0.05)

            if self.ser.inWaiting() > 0:                             # Se tiver algum caracter então executa
                # recebe a mensagem e insere na variavel
                mensagemlida = self.ser.readline()
                
                SerialPort = mensagemlida.decode()                   # Passa de Byte para string
                SerialPort = SerialPort.replace('<Run|MPos:', "")
                SerialPort = SerialPort.replace('<Idle|MPos:', "")
                SerialPort = SerialPort.replace('<Home|MPos:', "")
                # Replaces seguintes é para limpar a mensagem
                SerialPort = SerialPort.replace("|FS:", ",")
                SerialPort = SerialPort.replace(">\r\n", "")
                SerialPort = SerialPort.replace("|WCO:", ",")
                SerialPort = SerialPort.replace("|Ov:", ",")
                # Divide o que é separado por , em lista array
                self.memoryLOCK.acquire()                                 # Bloqueia as variavel para só poder ser acedida por uma Thread
                arrayEstadoMaquina = SerialPort.split(",")
                time.sleep(0.05)
                if (numpy.size(arrayEstadoMaquina) > 2):
                    dic = {
                        'X': float(arrayEstadoMaquina[0]),
                        'Y': float(arrayEstadoMaquina[1]),
                        'Z': float(arrayEstadoMaquina[2]),
                        "A": float(arrayEstadoMaquina[3]),
                        # "rolDir":float(arrayEstadoMaquina[4])
                    }
                    # remove data after reading     # Limpa o buffer do SerialPort
                    self.ser.flushInput()
                    self.memoryLOCK.release()
                    return dic
                # remove data after reading     # Limpa o buffer do SerialPort
                self.ser.flushInput()
                self.memoryLOCK.release()                              # Desbloqueia as variaveis e já podem ser lidas e acedidas por outra Threads
                return False


    def retorna_zero_Lancabolas_mm(self,eixo):
    # Encontra o zero em mm da maquina
        somaAngulos = abs(angulo["min_" + str(eixo)]) + angulo["max_" + str(eixo)]
        retorno = (abs(angulo["min_" + str(eixo)])*maximo[str(eixo)])/somaAngulos
        #print(str(eixo) + " " + str(round(retorno, 2)))
        return round(retorno, 2)


    def ConversorGrausToMM(self, Valorangulo, eixo):

        # Garante que o valor do angulo não ultrapassa o valor minimo ou maximo definido nos settingsLB.py
        if (Valorangulo > angulo["max_" + str(eixo)]):
            Valorangulo = angulo["max_" + str(eixo)]
        elif (Valorangulo < angulo["min_" + str(eixo)]):
            Valorangulo = angulo["min_" + str(eixo)]

        # Encontra o zero em mm da maquina
        somaAngulos = abs(angulo["min_" + str(eixo)]) + angulo["max_" + str(eixo)]
        anguloNormalizado = abs(angulo["min_" + str(eixo)]) + Valorangulo
        # (Valor do angulo *maximo do eixo) / maximo de angulos
        retorno = (anguloNormalizado*maximo[str(eixo)])/somaAngulos
        return round(retorno, 2)

    
    def gotTo_mm(self, X="n", Y="n", Z="n", A="n", F=1000):
    #print("Indica comando G90" + str(send_to_GRBL("G90")))
        mensagem = "G01"
        if (X != "n"):
            mensagem += " X" + str(X)
        if (Y != "n"):
            mensagem += " Y" + str(Y)
        if (Z != "n"):
            mensagem += " Z" + str(Z)
        if (A != "n"):
            mensagem += " A" + str(A)

        mensagem += " F" + str(F)
        #print("A mensagem GRBL é " + str(mensagem))
        self.send_to_GRBL(mensagem)


    def gotTo_graus(self, X="n", Y="n", Z="n", A="n", F=1000):                  # Se não chegar nenhum valor, a posição do eixo que é atribuido é n -> nenhum valor
        # send_to_GRBL("G90")
        mensagem = "G01"
        if (X != "n"):
            mensagem += " X" + str(self.ConversorGrausToMM(X, "X"))
        if (Y != "n"):
            mensagem += " Y" + str(self.ConversorGrausToMM(Y, "Y"))
        if (Z != "n"):
            mensagem += " Z" + str(self.ConversorGrausToMM(Z, "Z"))
        if (A != "n"):
            mensagem += " A" + str(self.ConversorGrausToMM(A, "A"))
        mensagem += " F" + str(F)
        self.send_to_GRBL(mensagem)


    def confirmaPosicaoFinal(self, X="n", Y="n", Z="n", A="n"):
        # Garante que vem o dicionario e não ocorre um erro de RUNTIME
        posAtual = self.getCoordenadas()
        while (posAtual == False):
            posAtual = self.getCoordenadas()     
        time.sleep(0.1)
        # Caso não seja passado o valor por parametro, então fica "n" e não entra nos calculos.
        if ((posAtual["X"] == X or X == "n") and (posAtual["Y"] == Y or Y == "n") and (posAtual["Z"] == Z or Z == "n") and (posAtual["A"] == A or A == "n")):
            return True
            
        else:
            return False

    def lb_home(self, a=1):
        print("A referenciar lançado de bolas")
        print("G90" + str(self.send_to_GRBL("G90")))
        print("Homing X Y Z , is ok" + str(self.send_to_GRBL("$H")))
        print("Homing A , is ok" + str(self.send_to_GRBL("$HA")))

        X0=self.retorna_zero_Lancabolas_mm("X")
        Y0=self.retorna_zero_Lancabolas_mm("Y")
        Z0=self.retorna_zero_Lancabolas_mm("Z")
        A0=self.retorna_zero_Lancabolas_mm("A")
        # vai para o centro de cada eixo, velocidadezeromaquina vem dos settingsLB
        self.gotTo_mm(X=X0, Y=Y0, Z=Z0, A=A0, F=velocidadeZeroMaquina)
        
        # enquanto não atinge não procegue
        while (not self.confirmaPosicaoFinal(X=X0, Y=Y0, Z=Z0, A=A0)):
            time.sleep(0.3)

    # ======================== Ciclo de Treinos =============================

    
    def run(self):
        #print(" Entrei no Run. -> Nome do lance: " + self.nomeLance  )
        self.pause = False                                                                     # se o lance não estiver em pausa, (tecla pause do lance)
                                                                                               # O tempo é inializado a 0 e à medida que 
        timeStartLance = 0                                                                     # vai sendo executado o lance é incrementado
        flagEnviaCoordenadas = True                                                            # levanto a flag para enviar coordenadas
        prontoSequencialancamento = False                                                      # e inicializo uma variavel que controlo a Seq de lançamento
        
        while (not self.stopped()):                                                            # enquanto não está parado o lance
            if ((not self.pause and self.runing)):                                             # e se não houver uma pausa e existe um sinal apra correr então
                # Condição usada no primeiro ciclo para enviar a mensagem de coordenadas do lance
                if (flagEnviaCoordenadas):                                                     # Esta função chamada a cada ciclo e é responsavel por enviar
                                                                                               # de enviar as posições para o lança bolas através pela porta COM                        
                    self.gotTo_graus(X=self.angulo_X, Y=self.angulo_Y, Z=self.angulo_Z, F=2000)
                    # Iterador de lançamento zerado
                    self.iteradorLances = 0                                                    
                    flagEnviaCoordenadas = False                                               # Baixa a flag porque ja foi enviado o comando

                if (not prontoSequencialancamento):    # Quando chegar à posição final continua
                    if (self.confirmaPosicaoFinal(X=self.ConversorGrausToMM(self.angulo_X, "X"), Y=self.ConversorGrausToMM(self.angulo_Y, "Y"), Z=self.ConversorGrausToMM(self.angulo_Z, "Z"))):
                        for iter in range(1, 20):
                            mensagem = "M67 E1 Q" + \
                                str(self.velRoloEsq*(iter/20)) + "\n"
                            # Bloco de envio de G-CODE
                            self.ser.write(mensagem.encode())
                            mensagem = "M67 E0 Q" + \
                                str(self.velRoloDir*(iter/20)) + " \n"
                            # Bloco de envio de G-CODE
                            self.ser.write(mensagem.encode())
                            time.sleep(0.05)
                        prontoSequencialancamento = True

                if (prontoSequencialancamento):
                    #print("passei no if dos setpoints")
                    # Simulação do Loop de controlo da Thread
                    if (self.iteradorLances <= self.qtBolasLancadas):
                       
                        # nota o dicionario vem do settingsLB.py 
                        mensagem = "G01 A" + \
                            str(self.ConversorGrausToMM(graus_desl_a["lancaBola"], "A")) + " F" + velocidadeAvancoGate  + "\n"
                        
                        #self.send_to_GRBL(mensagem)
                        self.ser.flushInput()
                        self.ser.write(mensagem.encode())                      # Bloco de envio de G-CODE
                        self.tic()
                        mensagem = "G01 A" + \
                            str(self.ConversorGrausToMM(graus_desl_a["retemBola"], "A")) + " F" + velocidadeAvancoGate  + "\n"
                        # Bloco de envio de G-CODE
                        self.ser.write(mensagem.encode())
                        #print("enviei o comando dos 10 graus")
                        
                        while (not self.confirmaPosicaoFinal(A=self.ConversorGrausToMM(graus_desl_a["retemBola"], "A")) or self.toc()<=self.cadencia):
                            time.sleep(0.2)
                            if(self.stopped()):
                                break
                        self.iteradorLances += 1                         # Itera a quantidade de bolas que já foram lançadas
                    else:                                                # Aqui inicia o processo de paragem do lançamento, porque acabou o sequenciamento
                        for iter in range(1, 20):
                            mensagem = "M67 E1 Q" + \
                                str(self.velRoloEsq -
                                    self.velRoloEsq*(iter/20)) + "\n"
                            # Bloco de envio de G-CODE
                            self.ser.write(mensagem.encode())
                            mensagem = "M67 E0 Q" + \
                                str(self.velRoloDir -
                                    self.velRoloDir*(iter/20)) + " \n"
                            # Bloco de envio de G-CODE
                            self.ser.write(mensagem.encode())

                            time.sleep(0.1)
                        mensagem = "M67 E1 Q0\n"
                        # Bloco de envio de G-CODE
                        self.ser.write(mensagem.encode())
                        mensagem = "M67 E0 Q0\n"
                        # Bloco de envio de G-CODE
                        self.ser.write(mensagem.encode())

                        prontoSequencialancamento=False
                        flagEnviaCoordenadas=True
                        self.runing=False
        mensagem = "M67 E1 Q0\n"
        # Bloco de envio de G-CODE
        self.ser.write(mensagem.encode())
        mensagem = "M67 E0 Q0\n"
        # Bloco de envio de G-CODE
        self.ser.write(mensagem.encode())

 # ==================================
    #  Calcula o centro,


