import math
import json
import time
import numpy
import threading
from time import time as Time
from .controlo_PID.PID import PID
memoryLOCK = threading.Lock()
from .models import treino, lance

from .bibliotecas.machine_lb import configLB, ConversorGrausToMM 
from .bibliotecas.machine_lb import serCentralControl

# Declara os 3 objetos que são controladors pelo enginelançador
from .bibliotecas.threadLance import ClasseThreadLance
from .bibliotecas.threadTreino import threadTreino
from .bibliotecas.threadManual import threadManualMode

"""
Duas funções de temporização, a tic() guarda o tempo no momento em que ela é chamada
a função toc() retorna o tempo entre o tic() e o toc() 
"""
start = 0
def tic():
    global start
    start = Time()
    return Time()

def toc():
    delta_t = Time() - start
    return delta_t


# ============================================================#
#              ENGINE DO LANCADOR DE BOLAS UA                 #

#=============================================================#

# ============================================================#
#   TODOS OS MOVIMENTOS E PEDIDOS DE TREINOS E LANCES SAO     #
#  GERIDOS POR ESTA CLASSE, que lança THREAD's DE CONTROLO    #
#  MM -> MANUAL MODE
#  AM -> AUTOMATIC MODE
#  LM -> LANCE MODE

class engineLancador:
    
    '''
    CLASSE ESTATICA, GLOBAL
    Variaveis Globais da função
    '''
    
    ser = serCentralControl.ser                         # Recebe o porta serie de centro de controlo de comandos SerialPort


    threadManMode = threadManualMode(ser)
    tempoTreino=0
    timeLeft=0
    tempoInicial=0
    tempoNormalizadoSegundos=0
    id_treino=0
    th_egineTreino=None
    
    def __init__():
        # Inicia o objeto sem qualquer informação, só após o metodo start é que podemos arrancar com a Thread
        #self.th_egineTreino=threadTreino(engineLancador.ser,tempoTreino=0, qtLancamentos=0,objLances=0, cadencia=0, tipoSequencia=0, MaxBolasTreino=0)
        pass

    # Inicio de um lance ou Treino, tipo pode ser "treino" ou "lance"
    @staticmethod
    def start(id_selected, tipo, dataLance={}):
                                                                       # Link para o objeto global do serialPort
        if (tipo=="treino"):
            engineLancador.dbTreino = treino.objects.get(id=id_selected)          # Consulta a base de dados, e obtem o objeto tabela com toda a informação                                   

            # -----------  Construção da THREAD com os dados do treino -------------------
            engineLancador.th_egineTreino=threadTreino(
                engineLancador.ser,
                tempoTreino=engineLancador.dbTreino.tempoTreino,
                qtLancamentos= engineLancador.dbTreino.Qt_bolas_lance,        # Quantidade de bolas lançadas por lance
                objLances=engineLancador.dbTreino.lances.all(),               # Recebe o objeto dos lances da base de dados
                cadencia=engineLancador.dbTreino.cadenciaTreino,              # recebe a cadencia da base de dados  
                tipoSequencia=engineLancador.dbTreino.SequenciaLances,        # Qual o tipo de sequencia , (ALEATORIA = 1 SEQUENCIAL = 2)
                MaxBolasTreino= engineLancador.dbTreino.maxBolasTreino)       # Maximo de bolas por cada treino
            print("\n\n\n" + "Start treino nos metodos: " + str(id_selected) + "\n\n\n")
            engineLancador.th_egineTreino.start()

        if (tipo=="lance"):                                         # Se for do tipo lance
            if "cadencia" in dataLance:
                engineLancador.threadLance=ClasseThreadLance(engineLancador.ser)                 # Cria uma nova instancia do objeto  lance  
                engineLancador.dbLance = lance.objects.get(id=id_selected)        # vai a base de dados consultar os dados com o id selecionado  
                engineLancador.threadLance.startLance(                            # e chama o metodo para configurar e iniciar o lance no novo objeto criado
                    nomeLance="random",                                 # ???
                    velRoloEsq=int(engineLancador.dbLance.velocidadeRoloEsq),     # atribui a velocidade do ROLO esquerdo
                    velRoloDir=int(engineLancador.dbLance.velocidadeRoloDir),     # atribui a velocidade do ROLO Direito
                    angulo_X=int(engineLancador.dbLance.anguloX),                 # ... e por ai fora.
                    angulo_Y=int(engineLancador.dbLance.anguloY), 
                    angulo_Z=int(engineLancador.dbLance.anguloInclinacao), 
                    cadencia=int(dataLance["cadencia"]), 
                    qtBolasLancadas=int(dataLance["qtBolas"]))
            else:
                print("Erro de Runtime, não inseriu cadencia e qtBolas nos lances corretamente")

    @staticmethod
    def stop(tipo):
        if (tipo=="treino"):
            engineLancador.th_egineTreino.stop()
            print("Stop Treino")
        if (tipo=="lance"):
            engineLancador.threadLance.stop()

    @staticmethod
    def pause(tipo):
        if (tipo=="treino"):
            engineLancador.th_egineTreino.set_pause()
            print("pause treino")
        if (tipo=="lance"):
            engineLancador.threadLance.pausar()

    @staticmethod
    def resume(tipo):
        if (tipo=="treino"):
            engineLancador.th_egineTreino.set_resume()
            print("resume treino")
        if (tipo=="lance"):
            engineLancador.threadLance.resume()

    @staticmethod    
    def get_timeleft(tipo):                     
        return engineLancador.th_egineTreino.get_timeleft()                                             # Retorna o tempo restante do treino

    @staticmethod
    def get_percentleft(tipo):
        if (tipo=="treino"):
            return engineLancador.th_egineTreino.get_percentleft()                                      # Retorna a percentagem faltante do treino
        if (tipo=="lance"):
            return engineLancador.threadLance.get_percentLeft_porbolas()

    # Somenta válido para treinos
    @staticmethod
    def get_Aexecutar():
        return engineLancador.th_egineTreino.get_Aexecutar()

    @staticmethod
    def get_bolasPorLance(tipo):
        pass

    @staticmethod
    def isStoped(tipo):
        if (tipo=="lance"):
            return engineLancador.threadLance.stopped()
        if (tipo=="treino"):
            return engineLancador.th_egineTreino.stopped()
            
    @staticmethod
    def get_bolasLancadasLeft(tipo):
        if (tipo=="lance"):
            return engineLancador.threadLance.get_bolasLeft()    
        pass


    # ===== Metodos para controlo do MODO MANUAL, POWERED BY ENGINE =====
    #  MM -> MANUAL MODE
    @staticmethod
    def MM_lancar_bola():
        engineLancador.threadManMode.set_LANCAR_BOLA()
        if engineLancador.threadManMode.stopped:                      # Se a tinha Thread estiver parada inicializa-a
            engineLancador.threadManMode.start()
    
    @staticmethod
    def Ref_lancador():
        return serCentralControl.requestFunction_GRBL("refEixos")

    @staticmethod    
    def MM_mover_eixo_x(velocidade):
        pass

    def MM_mover_eixo_y(velocidade):
        pass
    
    @staticmethod
    def MM_mover_eixo_a(posicao):
        pass
    
    @staticmethod
    def MM_mover_rolo_esquerdo(percentagemVEL):
        pass
    
    @staticmethod
    def MM_mover_rolo_direito(percentagemVEL):
        pass
    
    @staticmethod
    def MM_stop():
        pass

    @staticmethod
    def getInfo_eixos_ref():
        return serCentralControl.requestFunction_GRBL("getInfo_eixos_ref")




# Variaveis que definem a posição atual dos motores
global varThread,X,Y,Z,velEsq,velDir
Flag_comandoMotoresRolEsq = False
Flag_comandoMotoresRolDir = False
Flag_lancarBola           = False
varThread=False
X_USUARIO=0.00             # Comando recebido pelo usuario
Y_USUARIO=0.00             # Comando recebido pelo usuario
Z_USUARIO=0.00             # Comando recebido pelo usuario
velEsq=0
velDir=0
objWebSocket=None          # Cria apenas memoria pois é atribuida no consumers-> on connect



# ============================================================#
#   Define os limites de passos maximos e minimos do eixo     #

#=============================================================#

presentValue= 0.00
#=============================================================#

# Função criada com o proposito de enviar dados por WebSocket
def enviaPorWebSocket(comando):

    memoryLOCK.acquire()
    X,Y,Z,A = serCentralControl.requestFunction_GRBL("get_NotSyncPosMotor")
    
    memoryLOCK.release()

    try:
        if comando == "X":
            bufferValor = X
        elif comando == "Y":
            bufferValor = Y
        elif comando == "Z":
            bufferValor = Z
        elif comando == "A":
            bufferValor = A
        elif comando == "rolEsq":
            rolEsq=serCentralControl.requestFunction_GRBL("get_velocityRolo:esq")
            bufferValor = rolEsq
        elif comando == "rolDir":
            rolDir=serCentralControl.requestFunction_GRBL("get_velocityRolo:dir")
            bufferValor = rolDir
        if objWebSocket is not None:
            objWebSocket.send(text_data=json.dumps({comando: bufferValor}))
    except Exception as e:
        print("Encontrado erro em -> FUNC: enviaPorWebSocket")
        print(str(e))
    

def enviaMsgWebSocket(tagMensagem,Valor):
    objWebSocket.send(text_data=json.dumps({
            tagMensagem : Valor,
    }))

# ============================================================#
#   Variaveis que definem a velocidade atual dos motores      #
#   São atualizadas pelo consumers diretamente da receção     #
#   do valor recebido pelo websocket, a thread trata de       #
#   converter em movimento. Nota: motores Joystick            #
global vel_x, vel_y
vel_x = 0
vel_y = 0
#=============================================================#


#=============================================================#
#           Fator de conversão velocidade JoyStick            #
#   Multiplica a velocidade recebida pelo joystick por        #
#   esta constante, quanto maior for a constante mais         #
#   velocidade atinje no modo Joystick                        # 
factorVelocidade= 10        
#=============================================================#


#=============================================================#
#           Intervalo de comunicação com GRBL                 #
#   Esta variavel é muito importante, é o que dita o          #
#   intervalo de atualização da velocidade dos moores em      #
#   tempo real, envia G-CODE para o GRBL a cada timeSleep     # 
timeSleep=0.1
timeSleepMsg=0.5
#=============================================================#


#=============================================================#
#           Comanda a velocide Z no ciclo de controlo         #
#   EX: (1000mm/s / 60 seg = 16.666) * tempo de ciclo         #
VelocidadeMaximaEmZ=1000
#=============================================================#

#=============================================================#
#           Variaveis que controlam o comando de velocidade   #
#           dos motores do rolos                              #
#           para comando só é necessario atribuir primeiro 
#
# Declaração de variaveis: 
#Flag_comandoMotoresRolEsq=False
#Flag_comandoMotoresRolDir=False

def getFlagRoloEsq():
    global Flag_comandoMotoresRolEsq
    return Flag_comandoMotoresRolEsq
def getFlagRoloDir():
    global Flag_comandoMotoresRolEsq
    return Flag_comandoMotoresRolDir
def setFalse_FlagRoloEsq():
    global Flag_comandoMotoresRolEsq
    Flag_comandoMotoresRolEsq=False
def setFalse_FlagRoloDir():
    global Flag_comandoMotoresRolDir
    Flag_comandoMotoresRolDir=False

#=============================================================#
#    Função lançar bola atravez da comunicação WebSocket      #
#         Manda pulso, e a função depois de lançar a bola     #
#                Coloca o pulso a zero                        #

def lancar_bola():
    global Flag_lancarBola
    memoryLOCK.acquire()
    Flag_lancarBola=True
    memoryLOCK.release()
    

# Como a velocidade dos rolos não pertence ao comandos dos eixos, nas variaveis auxiliares, existe novo DICT
velocidade_rolo = {
        'esquerdo': 0, 
        'direito': 0, 
        }    

#Comando para atribuir velocidade nos consumers
def comando_rolos_esquerdo(velocidade):
    global Flag_comandoMotoresRolEsq                                # Assim estou a receber a variavel Global
    serCentralControl.requestFunction_GRBL("set_velocityRolo:" + velocidade +",esq")
    # Só ativa a flag depois do novo valor de velocidade ser atribuido - Proxima implementaão, ativa FLAG quando está no menu manual mode
    Flag_comandoMotoresRolEsq=True 

#Comando para atribuir velocidade nos consumers
def comando_rolos_direito(velocidade):
    global Flag_comandoMotoresRolDir
    serCentralControl.requestFunction_GRBL("set_velocityRolo:" + velocidade +",dir")
    
    # Só ativa a flag depois do novo valor de velocidade ser atribuido 
    Flag_comandoMotoresRolDir=True        
#=============================================================#

def askGRBL(comandoAsk):
    if engineLancador.ser.isOpen():
        engineLancador.ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens.                                  
        engineLancador.ser.write(comandoAsk.encode() + str.encode('\n'))   # Bloco de envio de G-CODE
        # Espera 1/10 de segundo pela resposta do GRBL
        time.sleep(0.1)
        grbl_out = engineLancador.ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
        resposta=grbl_out[0].decode()
        resposta = resposta.replace(comandoAsk+"=", "")     # Substitui do comando + "=" por nada e fica só o valor
        return resposta

def setGRBL(comandoSet, novoValor):
    if engineLancador.ser.isOpen():
        engineLancador.ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens                                  
        mensagem= comandoSet+ "=" + novoValor + '\n'        # Contrução da mensagem, não apagar o '\n', senão não funciona
        engineLancador.ser.write(mensagem.encode())                        # Bloco de envio de G-CODE
        time.sleep(0.1)                                     
        grbl_out = engineLancador.ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
        resposta=grbl_out[0].decode()
        return resposta
 

# ------ Thread de controlo MODO MANUAL, FUTURAMENTE PARA RETIRAR PARA UM FICHEIRO SEPARADO ---------
# Metodo para comunicar com GRBL e receber coordenadas em formato dicionario, 
def funcComandoGRBL():
    
    tic()                                               # Retira o primeiro tempo quando inicia a Thread
    tmovel=toc()                                        # Inicia a variavel  
    tmovelMsg=toc()                                     # Inicia a variavel
    time.sleep(2)                                       # Espera 2 segundos para iniciar a THREAD, dar tempo ao GRBL de iniciar
    delta_DZ=0.00                                       
    vel_z=0                                             
    flag_AtualizaInterface=False                        
    X=0                 
    Y=0
    Z=0
    A=0

    cortaVelX=0
    cortaVelY=0
    cortaVelZ=0

    # Link com variaveis Globais
    global timeSleepMsg                                   
    global presentValue
    global Flag_lancarBola

    # Recebe a posiço atual do lançador de bolas, X,Y,Z,A
    X,Y,Z,A = serCentralControl.requestFunction_GRBL("get_Coordenadas")
    
    # Imprime para debug quais são as coordenadas Iniciais do lançador de bolas
    print("Coordenadas maquina x iniciais: ", X)
    print("Coordenadas maquina Y iniciais: ", Y)
    print("Coordenadas maquina Z iniciais: ", Z)
    print("Coordenadas maquina A iniciais: ", A)

    # Define qual é a constantes de controlo do PID
    pidObj= PID(Ki=0.025, Kd=0.0009, Kp=90, setpoint=0.00)
    pidObj.output_limits = (-VelocidadeMaximaEmZ, VelocidadeMaximaEmZ)

    # Inicia o CICLO INFINITO
    while(True):
        
        #Rotina de atualização da interface
        #Função que a cada timeSleepMsg envia para o front o valor dos eixos, ou então por request.
        if(toc()>tmovelMsg):
            tmovelMsg+=timeSleepMsg                     
            enviaPorWebSocket('X')
            enviaPorWebSocket('Y')
            enviaPorWebSocket('Z')
            enviaPorWebSocket('rolEsq')
            enviaPorWebSocket('rolDir')
        elif(flag_AtualizaInterface):
            enviaPorWebSocket('X')
            enviaPorWebSocket('Y')
            enviaPorWebSocket('Z')
            flag_AtualizaInterface=False
        if(getFlagRoloEsq()==True):
            enviaPorWebSocket('rolEsq')
            setFalse_FlagRoloEsq()
        if(getFlagRoloDir()==True):
            enviaPorWebSocket('rolDir')
            setFalse_FlagRoloDir()
                    
        if(toc()>(tmovel)):   # Garante que respeita a base de tempo
            
            # Atualiza a nova base de tempo n+1
            tmovel+=timeSleep 

            # Setpoint -> valor inserido pelo usuario * fato de correção graus para milietros
            # o Z_USUARIO é sempre de 0 a 100, e portanto é preciso acertar o valor com os maximo e minimons
            # mecanicos do lança bolas
            # Y=a*b+b
            # Como temos um valor de 0 a configLB.maximo["Z"] então :
            setpoint = int((Z_USUARIO / 100) * configLB.maximo["Z"])  
            
            # 
            difEntreZ=float(f'{(presentValue-setpoint):.3f}') # padronizado em milimetros
            
            if ((vel_x!=0 or vel_y!=0 or abs(difEntreZ)>0.20) and not serCentralControl.requestFunction_GRBL("get_ModoLance")):                  # Se X ou Y for diferente de 0, então encerra o algoritmo e comunicaçâo
                if not serCentralControl.requestFunction_GRBL("getInfo_eixos_ref"):                  # Caso alguem queira mover e ainda não esta referenciado, referencia
                   BL_temp = serCentralControl.requestFunction_GRBL("refEixos")
                
                
                #===========================================================================================================================================
                #Algoritmo de calculo de passo em X
                delta_DX=(vel_x*float(timeSleep))*factorVelocidade      #       Equaçâo: velocidade * tempoCiclo * 10 / 60 
                delta_DX=delta_DX/60                                    #       Notas: o fator de velocidade(10-padrão) é para passar de 100 mm/s para 1000 mm/s
                
                
                delta_DY=vel_y*float(timeSleep)*factorVelocidade     
                delta_DY=delta_DY/60
                # Algoritmo de cálculo de passo em Y (60 é para passar de mm/min para mm/segundo)
                
                    
                #Algoritmo de calculo de passo em Z, vai andar semper à velocidade maxima definida
        

                if(abs(difEntreZ)>0.005):
                    pidObj.setpoint=setpoint
                    vel_z=float(f'{pidObj(presentValue):.3f}')
                    PassoParaVelocidadeZ=vel_z/60*timeSleep
                    delta_DZ=float(f'{PassoParaVelocidadeZ:.3f}')
                else:
                    delta_DZ=0.00
                    vel_z=0.00

                #Adquire coordenadas dos eixos X,Y,Z,A
                memoryLOCK.acquire()
                X,Y,Z,A = serCentralControl.requestFunction_GRBL("get_Coordenadas")
                memoryLOCK.release()

                # Inicio de corte de velocidade a 0
                cortaVelX=cortaVelY=cortaVelZ=1
                # Controlo de limites de X
                if X < (0.0+3.0) and delta_DX < 0.0:
                    delta_DX = 0.0
                    cortaVelX=0
                elif (configLB.maximo["X"]) < X and delta_DX > 0.0:
                    delta_DX = 0.0
                    cortaVelX=0
                # Controlo de limites de Y
                if Y < (0.0+3.0) and delta_DY < 0.0:
                    delta_DY = 0.0
                    cortaVelY=0
                elif (configLB.maximo["Y"]) < Y and delta_DY > 0.0:
                    delta_DY = 0.0
                    cortaVelY=0
                # Controlo de limites de Z
                if Z < (0.0) and delta_DZ < 0.0:
                    delta_DY = 0.0
                    cortaVelZ=0
                elif (configLB.maximo["Z"]) < Z and delta_DZ > 0.0:
                    delta_DZ = 0.0
                    cortaVelZ=0
                else:
                    presentValue=Z    


                # Atualiza o valor anterior com a atual
                

                    
                # Velocidade a 3 dimensões
                vectorialVel=math.sqrt(numpy.square(vel_x*cortaVelX*factorVelocidade)+numpy.square(vel_y*cortaVelY*factorVelocidade)+numpy.square(abs(vel_z*cortaVelZ)))       

                # Construção das mensagens
                mensagem="G91 G01 X" + str(float(f'{delta_DX:.2f}')) + " Y" + str(float(f'{delta_DY:.2f}')) + " Z" + str(float(f'{delta_DZ:.3f}')) +" F" + str(abs(vectorialVel))
                
                # Envi a mensagem por GRBL
                serCentralControl.requestFunction_GRBL("send_toGRBL:" + mensagem)

                # Print da mensagem para debug
                #print("send_toGRBL:" + mensagem)
                
                # Marca que existe informação para atualizar na interface
                flag_AtualizaInterface=True

            if (Flag_lancarBola):
                print("Bola lançada")
                
                #Constroi mensagem para GRBL
                mensagem = "G90 G01 A" + \
                    str(ConversorGrausToMM(configLB.graus_desl_a["lancaBola"], "A")) + " F" + configLB.velocidadeAvancoGate
                
                # Bloco de envio de G-CODE
                serCentralControl.requestFunction_GRBL("send_toGRBL:" + mensagem)                                         
                
                #Constroi mensagem para GRBL
                mensagem = "G90 G01 A" + \
                    str(ConversorGrausToMM(configLB.graus_desl_a["retemBola"], "A")) + " F" + configLB.velocidadeAvancoGate
                
                # Bloco de envio de G-CODE
                serCentralControl.requestFunction_GRBL("send_toGRBL:" + mensagem)                                        
                Flag_lancarBola=False
                pass