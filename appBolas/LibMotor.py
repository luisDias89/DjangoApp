#######################################
# Copyright (c) 2022
# Author: Luís Dias
#######################################
#             Librari
# Raspberry Pi Steeper Motor Control
# --- DIR STEEP ENABLE CONTROL
# --- Test With DRV8825 and NEMA17
# --- MAX Frequenci 300 khz PI4
#
#          Luís Dias 2022
#######################################


from pickle import TRUE
import RPi.GPIO as GPIO #Importe la bibliothèque pour contrôler les GPIOs
import time
import threading


start = 0
def tic():
    global start
    start = time.time()
    return time.time()

def toc():
    delta_t = time.time() - start
    #print("Elapser time is " + str(delta_t) + " second.")
    return delta_t


class NewSteepMotor:

    # Variavel que guarda a posição em passos em relação ao ZERO
    MOTOR_POSITION=0

    #Variavel que guarda a posição para a qual o motor deve se mover,é iterada até ser igual a MOTOR_POSITION
    newPosition=MOTOR_POSITION

    # Variavel que define se o motor está bloqueado após se mover
    MotorEnableAfterMov=False

    #Direção do motor
    directionClockWise=True

    #Variaveis auxiliares do ciclo e controlo
    freq=0
    periodo=0
    STARTmodoFREQ=False
    STARTmodoSTEEP=False
    direction = 1
    
    def __init__(self, eixoMot, DIR_PIN, STEEP_PIN, ENABLE_PIN, miCrosteep=16, MotorEnableAfterMov = False):

        #Faz atribuições às variaveis internas
        self.eixoMot = eixoMot
        self.miCrosteep = miCrosteep
        self.DIR_PIN=DIR_PIN
        self.STEEP_PIN=STEEP_PIN
        self.ENABLE_PIN=ENABLE_PIN

        GPIO.setmode(GPIO.BCM)                              # Define o tipo de pinagem a utilizar
        GPIO.setwarnings(False)                             # Desativa as mensagens de alerta
        GPIO.setup(self.STEEP_PIN, GPIO.OUT)                # Ativa a controlo output do GPIO
        GPIO.setup(self.DIR_PIN, GPIO.OUT)                  # Ativa a controlo output do GPIO
        GPIO.setup(self.ENABLE_PIN, GPIO.OUT)               # Ativa a controlo output do GPIO
        GPIO.output(self.STEEP_PIN, GPIO.LOW)               # Ativa a controlo output do GPIO
        self.setMotorEnableAfterMov(MotorEnableAfterMov)    # Atribui e aplica a decisão do construtor sobre MotorEnableAfterMov

        #inicio da LOOP de controlo
        threading.Thread(target=self.funcThread, args=()).start()               
    
    def printInfo(self):
        print("Name of axys: ",self.eixoMot)
        print("miCrosteep: ",self.miCrosteep)
        print("DIR_PIN: ",self.DIR_PIN)
        print("STEEP_PIN: ",self.STEEP_PIN)
        print("ENABLE_PIN: ",self.ENABLE_PIN)


    #-----------------------------------------
    #      Bloquei motor após movimento      -
    #   Função para alterar parametros do    -
    #   motor, quando enable "True" o motor  -
    #   fica bloqueado após o movimento      -
    def setMotorEnableAfterMov(self,enable):
        self.MotorEnableAfterMov=enable
        if(self.MotorEnableAfterMov==False):
            GPIO.output(self.ENABLE_PIN,GPIO.HIGH)
        else:
            GPIO.output(self.ENABLE_PIN,GPIO.LOW)
    #-----------------------------------------


    #-----------------------------------------
    #   Função para receber a posição atual  -
    #   do motor em passos                   -
    def getAxysPosition(self):               
        return self.MOTOR_POSITION          
    #-----------------------------------------

    #-----------------------------------------
    #   Função para fazer reset da           -
    #   posição atual do motor em passos     -
    def resetAxysPosition(self):
        self.MOTOR_POSITION=0
    #-----------------------------------------
    
    def setAxysPosition(self,NEW_POSITION):
        self.MOTOR_POSITION=NEW_POSITION
    
    def setDirection(self,directionClockWise):
        self.__setDirection(int(directionClockWise))

    def __setDirection(self,direction):       # Usar somente para controlo interno, private
            if(direction==1):
                self.direction=1
                GPIO.output(self.DIR_PIN,1)
            elif(direction==0):
                self.direction=0
                GPIO.output(self.DIR_PIN,0)
    
    def modoComando(self, comando="stop"):
        if(comando=="stop"):
            self.STARTmodoSTEEP=False
            self.STARTmodoFREQ=False
            time.sleep(0.00001)                                         # Necessario para que pare o ciclo
            if(self.MotorEnableAfterMov==False):                    # Só desliga os motores de passo se for ativado o comando.
                GPIO.output(self.ENABLE_PIN,1)                      # O motor fica inabilitado
            else:
                GPIO.output(self.ENABLE_PIN,0)                      # O motor fica abilitado
        elif(comando=="frequencia"):
            self.STARTmodoSTEEP=False                               #Garante que desliga a Thread de STEEP
            GPIO.output(self.ENABLE_PIN,GPIO.LOW)                   #Garante que os motores de passo estão sempre ativados antes do arranque da Thread de comando
            self.STARTmodoFREQ=True                                 #Liga a thread de comando por Freq
            time.sleep(0.00001)                                         # Necessario para que pare o ciclo
        elif(comando=="steep"):
            self.STARTmodoFREQ=False                                #Garante que desliga a Thread de Freq
            GPIO.output(self.ENABLE_PIN,GPIO.LOW)                   #Garante que os motores de passo estão sempre ativados antes do arranque da Thread de comando
            self.STARTmodoSTEEP=True                                #Liga a thread de comando por STEEP
            time.sleep(0.00001)                                         # Necessario para que pare o ciclo

    
    def setFrequencia(self, freq, direction=0):
        direction = int(direction)
        self.modoComando(comando="stop")                            # Para todos os comandos
        if(freq>0):                                                 # So arranca se a frequencia for superior a 0
            self.__setDirection(direction)
            self.freq=freq                                          # recebe a frequencia da função
            self.periodo=1/freq                                     # Atualiza o periodo
            self.meioPeriodo=self.periodo/2                         # Atualiza o meioPeriodo
            self.modoComando(comando="frequencia")                  # Inicia a While da thread
    
    def setRPS(self, RPS, direction=0):
        self.modoComando(comando="stop")                            # Coloca o While do modo freq a Falso (Necesita de reservar a memoria para escrever, imp futura)
        direction = int(direction)
        self.freq=200*self.miCrosteep*RPS
        if(self.freq>0):         
            self.__setDirection(direction)     
            self.periodo=1/self.freq
            self.meioPeriodo=self.periodo/2
            self.modoComando(comando="frequencia")                  
         
    def moveVoltas(self,numeroVoltas,voltasPorSegundo=1):
        self.modoComando(comando="stop")
        if(abs(numeroVoltas)>0 and voltasPorSegundo>0):
            steepsVolta=200*self.miCrosteep
            steeps=numeroVoltas*steepsVolta
            tempo=abs(steeps)/(steepsVolta*voltasPorSegundo)
            self.moveNumberSteeps(steeps,tempo)


    #Função STEEP, recebe os passos e o tempo para executar os passos, com este valores calcula a velocidade e frequencia para atingir o target.

    def moveNumberSteeps(self,steeps,tempo):
        self.modoComando(comando="stop")                                            # Para todos os ciclos de comando
        if(tempo>0 and abs(steeps)>0):                                              # Se o tempo for superior a 0 e os steeps tambem, é valido
         
            self.freq=abs(steeps)/tempo                                             # Calcula a frequencia de controlo                                    
            self.periodo=1/self.freq                                                # calcula o periodo
            self.meioPeriodo=self.periodo/2                                         # Calcula T/2
            self.newPosition=self.MOTOR_POSITION+steeps                             # A nova posição são os steeps atuais + o target
            print(                                                                  # Imprime informações na consola
                "Numero de passos: ",steeps,
                " Periodo: ", self.periodo, 
                "Nova Posição: ",self.newPosition,
                "Frequencia: ",self.freq)
            time.sleep(0.01)                                                        # Espera 1/10 de segundo
            print("Move de: ", self.MOTOR_POSITION," para:", self.newPosition)      # Informação na consola do movimento
            self.modoComando(comando="steep")                                       # Permite o acesso aos ciclos de comando
            
        
            
    def moveToSteep(self,steepPos, rotPorSec):
        steeps=steepPos-self.MOTOR_POSITION
        tempo=abs(steeps)/(200*self.miCrosteep*rotPorSec)
        self.moveNumberSteeps(steeps,tempo)

    

    def funcThread(self):
        print("Entrei na Thread Motor", self.eixoMot)
        
        tic()
        tMovel=0
        while(True):

            #Ciclo concluido   
            tMovel=toc()
            i=0
            while(self.STARTmodoSTEEP):
                if(i==0):
                    newPosition=self.newPosition
                    meioPeriodo=self.meioPeriodo
                    STEEP_PIN=self.STEEP_PIN
                    DIR_PIN=self.DIR_PIN
                    i=2

                if(self.MOTOR_POSITION!=newPosition): 
                    # Contagem dos passos "Sentido" horario +1, antihorario -1
                    if(self.MOTOR_POSITION<newPosition):
                        self.MOTOR_POSITION=self.MOTOR_POSITION+1
                        GPIO.output(DIR_PIN,1)
                    else:
                        self.MOTOR_POSITION=self.MOTOR_POSITION-1
                        GPIO.output(DIR_PIN,0)

                    #Ciclo de comando STEEP
                    tMovel=meioPeriodo+tMovel
                    while(toc()<tMovel):
                        pass
                    GPIO.output(STEEP_PIN, 1)
                    tMovel=meioPeriodo+tMovel
                    while(toc()<tMovel):
                        pass
                    GPIO.output(STEEP_PIN, 0)
                else:
                    if(self.MotorEnableAfterMov==False):
                        GPIO.output(self.ENABLE_PIN,1)
                    self.STARTmodoSTEEP=False

            tMovel=toc()
            j=0
            while(self.STARTmodoFREQ):
                if(j==0):
                    direction=self.direction
                    meioPeriodo=self.meioPeriodo
                    STEEP_PIN=self.STEEP_PIN
                    j=1
                    print("Troca de variavei para VAR local")
                # Contagem dos passos "Sentido" horario +1, antihorario -1
                if(direction==1):
                    self.MOTOR_POSITION=self.MOTOR_POSITION+1
                else:
                    self.MOTOR_POSITION=self.MOTOR_POSITION-1

                #Ciclo de comando STEEP
                tMovel=meioPeriodo+tMovel
                while(toc()<tMovel):
                    pass
                GPIO.output(STEEP_PIN, 1)
                tMovel=meioPeriodo+tMovel
                while(toc()<tMovel):
                    pass
                GPIO.output(STEEP_PIN, 0)

            

            


        

