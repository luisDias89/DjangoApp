import math
import json
import time
import numpy
import threading
from time import time as Time
from .controlo_PID.PID import PID
c = threading.Condition()
from .models import treino, lance
import serial
from .bibliotecas.objLance import ClasseThreadLance
from .bibliotecas.engineThread import threadTreino

"""
Objeto que se conecta e contem uma serie de metodos para comunicar via serial com o GRBL
"""
# ligação Serial com o Arduino, initilizado após biblioteca de Motor com RaspBery
# ligação Serial com o Arduino, initilizado após biblioteca de Motor com RaspBery
ser = serial.Serial(
        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)
time.sleep(0.5)


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
    #print("Elapser ime is " + str(delta_t) + " second.")
    return delta_t


class engineTreino:
    
    '''
    Variaveis Globais da função
    '''
    tempoTreino=0
    timeLeft=0
    tempoInicial=0
    tempoNormalizadoSegundos=0
    id_treino=0
    def __init__(self):
        global threadOP
        # Inicia o objeto sem qualquer informação, só após o metodo start é que podemos arrancar com a Thread
        #threadOP=threadTreino(ser,tempoTreino=0, qtLancamentos=0,objLances=NULL, cadencia=0, tipoSequencia=0)
    
    # metodos acessiveis
    def start(self, id_selected, tipo, dataLance={}):
                                                                        # Link para o objeto global do serialPort
        global threadOP
        if (tipo=="treino"):
            self.dbTreino = treino.objects.get(id=id_selected)          # Consulta a base de dados, e obtem o objeto tabela com toda a informação                                   

            # -----------  Construção da THREAD com os dados do treino -------------------
            threadOP=threadTreino(
                ser,
                tempoTreino=self.dbTreino.tempoTreino,
                qtLancamentos= self.dbTreino.Qt_bolas_lance,        # Quantidade de bolas lançadas por lance
                objLances=self.dbTreino.lances.all(),               # Recebe o objeto dos lances da base de dados
                cadencia=self.dbTreino.cadenciaTreino,              # recebe a cadencia da base de dados  
                tipoSequencia=self.dbTreino.SequenciaLances)        # Qual o tipo de sequencia , (ALEATORIA = 1 SEQUENCIAL = 2)
            print("\n\n\n" + "Start treino nos metodos: " + str(id_selected) + "\n\n\n")
            threadOP.start()

        if (tipo=="lance"):                                         # Se for do tipo lance
            if "cadencia" in dataLance:
                self.threadLance=ClasseThreadLance(ser)                 # Cria uma nova instancia do objeto  lance  
                self.dbLance = lance.objects.get(id=id_selected)        # vai a base de dados consultar os dados com o id selecionado  
                self.threadLance.startLance(                            # e chama o metodo para configurar e iniciar o lance no novo objeto criado
                    nomeLance="random",                                 # ???
                    velRoloEsq=int(self.dbLance.velocidadeRoloEsq),     # atribui a velocidade do ROLO esquerdo
                    velRoloDir=int(self.dbLance.velocidadeRoloDir),     # atribui a velocidade do ROLO Direito
                    angulo_X=int(self.dbLance.anguloX),                 # ... e por ai fora.
                    angulo_Y=int(self.dbLance.anguloY), 
                    angulo_Z=int(self.dbLance.anguloInclinacao), 
                    cadencia=int(dataLance["cadencia"]), 
                    qtBolasLancadas=int(dataLance["qtBolas"]))
            else:
                print("Erro de Runtime, não inseriu cadencia e qtBolas nos lances corretamente")

    def stop(self,tipo):
        if (tipo=="treino"):
            global threadOP
            threadOP.stop()
            print("Stop Treino")
        if (tipo=="lance"):
            self.threadLance.stop()

    def pause(self,tipo):
        if (tipo=="treino"):
            global threadOP
            threadOP.set_pause()
            print("pause treino")
        if (tipo=="lance"):
            self.threadLance.pausar()

    def resume(self,tipo):
        if (tipo=="treino"):
            global threadOP
            threadOP.set_resume()
            print("resume treino")
        if (tipo=="lance"):
            self.threadLance.resume()
        
    def get_timeleft(self,tipo):                     
        return threadOP.get_timeleft()                                             # Retorna o tempo restante do treino


    def get_percentleft(self,tipo):
        if (tipo=="treino"):
            return threadOP.get_percentleft()                                      # Retorna a percentagem faltante do treino
        if (tipo=="lance"):
            return self.threadLance.get_percentLeft_porbolas()

    def get_LanceAexecutar(self,tipo):
        pass

    def get_bolasPorLance(self,tipo):
        pass

    def isStoped(self,tipo):
        if (tipo=="lance"):
            return self.threadLance.stopped()
        pass

    def get_bolasLancadasLeft(self,tipo):
        if (tipo=="lance"):
            return self.threadLance.get_bolasLeft()    
        pass



# Variaveis que definem a posição atual dos motores
global varThread,X,Y,Z,velEsq,velDir
Flag_comandoMotoresRolEsq = False
Flag_comandoMotoresRolDir = False
varThread=False
X_USUARIO=0.00             # Comando recebido pelo usuario
Y_USUARIO=0.00             # Comando recebido pelo usuario
Z_USUARIO=0.00             # Comando recebido pelo usuario
velEsq=0
velDir=0
flag = 1
objWebSocket=None          # Cria apenas memoria pois é atribuida no consumers->on connect


# ============================================================#
#   Define os limites de passos maximos e minimos do eixo     #

#=============================================================#

# ============================================================#
#   Dicionario atualizado pelo controlador para saber a pos   #
#   atual dos eixos no GRBL                                   #
dicCordenadasControlador = {
       'X': 0.00, 
       'Y': 0.00, 
       'Z': 0.00, 
       "rolEsq": 0.00, 
       "rolDir": 0.00
    }
presentValue= 0.00
#=============================================================#

# Função criada com o proposito de enviar dados por WebSocket
def enviaPorWebSocket(comando):
    objWebSocket.send(text_data=json.dumps({
            comando : dicCordenadasControlador[comando],
    }))
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
FatorDeCoorecaoGrausMilimetros=2.0
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

# Como a velocidade dos rolos não pertence ao comandos dos eixos, nas variaveis auxiliares, existe novo DICT
velocidade_rolo = {
        'esquerdo': 0, 
        'direito': 0, 
        }    

#Comando para atribuir velocidade nos consumers
def comando_rolos_esquerdo(velocidade):
    global Flag_comandoMotoresRolEsq                                # Assim estou a receber a variavel Global
    velocidade_rolo['esquerdo']=velocidade
    # Só ativa a flag depois do novo valor de velocidade ser atribuido
    Flag_comandoMotoresRolEsq=True 

#Comando para atribuir velocidade nos consumers
def comando_rolos_direito(velocidade):
    global Flag_comandoMotoresRolDir
    velocidade_rolo['direito']=velocidade 
    # Só ativa a flag depois do novo valor de velocidade ser atribuido 
    Flag_comandoMotoresRolDir=True        
#=============================================================#

def askGRBL(comandoAsk):
    if ser.isOpen():
        ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens.                                  
        #print('Sending: ' + comandoAsk)
        ser.write(comandoAsk.encode() + str.encode('\n'))   # Bloco de envio de G-CODE
        # Espera 1/10 de segundo pela resposta do GRBL
        time.sleep(0.1)
        grbl_out = ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
        resposta=grbl_out[0].decode()
        resposta = resposta.replace(comandoAsk+"=", "")     # Substitui do comando + "=" por nada e fica só o valor
        return resposta

def setGRBL(comandoSet, novoValor):
    if ser.isOpen():
        ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens                                  
        mensagem= comandoSet+ "=" + novoValor + '\n'        # Contrução da mensagem, não apagar o '\n', senão não funciona
        #print('Sending: ' + mensagem)                      # Bloco de depuração
        ser.write(mensagem.encode())                        # Bloco de envio de G-CODE
        time.sleep(0.1)                                     
        grbl_out = ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
        resposta=grbl_out[0].decode()
        return resposta
 

# ------ Thread de controlo ---------
# Metodo para comunicar com GRBL e receber coordenadas em formato dicionario, 
def funcComandoGRBL():
    def getCoordenadas():
        if ser.isOpen():                                        # Se a porta serial está aberta
            ser.flushInput()                                    # remove toda a data na fila de entrada, só para se focar no pedido seguinte    
            mensagem="?\n"                                      # Pergunta quais as coordenadas atuais (Comando GRBL "?\n")
            ser.write(mensagem.encode())                        # Escreve na SerialPort "?\n" para receber as coordenadas
            time.sleep(0.05)                                    # Espera a resposta do arduino
            if  ser.inWaiting()>0 :                             # Se tiver algum caracter então executa
                mensagemlida=ser.readline()                     # recebe a mensagem e insere na variavel
                SerialPort =mensagemlida.decode()               # Passa de Byte para string
                SerialPort=SerialPort[11:]                      # Elimina os primeiros 11 caracteres
                SerialPort = SerialPort.replace("|FS:", ",")    # Replaces seguintes é para limpar a mensagem 
                SerialPort = SerialPort.replace(">\r\n", "")
                SerialPort = SerialPort.replace("|WCO:", ",")
                SerialPort = SerialPort.replace("|Ov:", ",")
                arrayEstadoMaquina = SerialPort.split(",")      # Divide o que é separado por , em lista array
                
                if(numpy.size(arrayEstadoMaquina)>2):
                    dic = {
                    'X': float(arrayEstadoMaquina[0]), 
                    'Y': float(arrayEstadoMaquina[1]), 
                    'Z': float(arrayEstadoMaquina[2]), 
                    "rolEsq": float(arrayEstadoMaquina[3]), 
                    "rolDir":float(arrayEstadoMaquina[4])
                    }
                    return dic
                
                ser.flushInput() #remove data after reading     # Limpa o buffer do SerialPort
                return False

    def __SendToEsp32_no_waitResponse(mensagem):
        if ser.isOpen():
            #print(mensagem)
            ser.write(mensagem.encode())            # Envia a mensagem por RS232
            #print(mensagem)    # Squiser monotorizar a mensagem que enviar
            # Loop de controlo , só este loop (obrigatoriamente) tem que fazer a comunicação por RS232                              
            time.sleep(0.1)
            ser.flushInput() 

    def __SendToEsp32_waitResponse(mensagem):
        if ser.isOpen():
            SerialPort=""                           # Sem isto existir dá erro o PYTHON, a variavel não é subscrevida.
            #print(mensagem)
            ser.write(mensagem.encode())            # Envia a mensagem por RS232
            TentaComunicar=True                     # Tenta comunicar a True para iniciar a comunicação, repetidamente até receber "OK"
            # Loop de controlo , só este loop (obrigatoriamente) tem que fazer a comunicação por RS232
            while(TentaComunicar):                                  
                time.sleep(0.01)
                if  ser.inWaiting()>0 :                             # Se se algum caracter já estiver no buffer executa
                    mensagemlida=ser.readline()                     # recebe a mensagem e insere na variavel
                    SerialPort =mensagemlida.decode()               # Passa de Byte para string e imprim na tela
                    #print("Li dentro do inWait",SerialPort)                               # Imprime na tela.
                if("ok" in SerialPort):
                    #print("fiquei no segundo IF")
                    TentaComunicar=False
                    ser.flushInput() 
                    SerialPort=""

    
    iterAux=0
    tic()
    tmovel=toc()
    tmovelMsg=toc()
    time.sleep(2)
    delta_DZ=0.00
    vel_z=0
    TentaComunicar=False
    flag_AtualizaInterface=False

    global timeSleepMsg                         # por padrão é definido a 0.5 segundos
    global c                                    # Correnponde ao objeto de fechar a Thread
    global flag             
    global presentValue
    global dicCordenadasControlador
    dicCordenadasControlador=getCoordenadas()
    
    while(dicCordenadasControlador==False):
        dicCordenadasControlador=getCoordenadas()
        print(type(dicCordenadasControlador))
    print("Coordenadas maquina x iniciais: ", dicCordenadasControlador['X'])
    print("Coordenadas maquina Y iniciais: ", dicCordenadasControlador['Y'])
    print("Coordenadas maquina Z iniciais: ", dicCordenadasControlador['Z'])
    print("Coordenadas maquina velRoloEsq iniciais: ", dicCordenadasControlador['rolEsq'])
    print("Coordenadas maquina velRoloDir iniciais: ", dicCordenadasControlador['rolDir'])
    pidObj= PID(Ki=0.025, Kd=0.0009, Kp=60, setpoint=0.00)
    pidObj.output_limits = (-VelocidadeMaximaEmZ, VelocidadeMaximaEmZ)

    while(True):

        #Funo que a cada timeSleepMsg(tempo definido em cima) 
        if(toc()>tmovelMsg):
            tmovelMsg=tmovelMsg+timeSleepMsg
            if(flag_AtualizaInterface):
                enviaPorWebSocket('X')
                enviaPorWebSocket('Y')
                enviaPorWebSocket('Z')
                flag_AtualizaInterface=False
            
        
        if(toc()>(tmovel)):   # Garante que respeita a base de tempo
            
            tmovel=tmovel+timeSleep                     # Atualiza a nova base de tempo n+1
            #Setpoint -> valor inserido pelo usuario * fato de correção graus para milietros

            setpoint=Z_USUARIO*FatorDeCoorecaoGrausMilimetros
            
            difEntreZ=float(f'{(presentValue-setpoint):.2f}') # padronizado em milimetros

            if (vel_x!=0 or vel_y!=0 or abs(difEntreZ)>0.02):                  # Se X ou Y for diferente de 0, então execta o algoritmo e comunicaçâo
                #print("Vel_X: ", vel_x," Vel_y: ", vel_y," Dif_Z:", abs(difEntreZ), "vel_z: ", vel_z)
                #===========================================================================================================================================
                #Algoritmo de calculo de passo em X
                delta_DX=(vel_x*float(timeSleep))*factorVelocidade      #       Equaçâo: velocidade * tempoCiclo * 10 / 60 
                delta_DX=delta_DX/60                                    #       Notas: o fator de velocidade(10-padrão) é para passar de 100 mm/s para 1000 mm/s
                #Algoritmo de calculo de passo em Y                     #       60 é para passar de mm/min para mm/segundo
                delta_DY=vel_y*float(timeSleep)*factorVelocidade     
                delta_DY=delta_DY/60
                #Algoritmo de calculo de passo em Z, vai andar semper à velocidade maxima definida


                if(abs(difEntreZ)>0.01):
                    pidObj.setpoint=setpoint
                    vel_z=float(f'{pidObj(presentValue):.3f}')
                    PassoParaVelocidadeZ=vel_z/60*timeSleep
                    delta_DZ=float(f'{PassoParaVelocidadeZ:.3f}')
                    
                    #WebsocketConsumer.send(text_data=json.dumps({
                    #    'posReal_RoloTorce': str(presentValue/FatorDeCoorecaoGrausMilimetros),
                    #}))
                    
                    #print(difEntreZ)
                    #print("Sai com o type: ",type(dicCordenadasControlador))
                else:
                    delta_DZ=0.00
                    vel_z=0.00


                c.acquire()
                if flag==1:
                    flag=0
                    dicCordenadasControlador=getCoordenadas()
                    while(type(dicCordenadasControlador)==bool):
                        dicCordenadasControlador=getCoordenadas()
                    presentValue=dicCordenadasControlador['Z']
                    flag=1
                    c.notify_all()
                else:
                    c.wait()
                c.release()

                
                # Velocidade a 3 dimensões
                vectorialVel=math.sqrt(numpy.square(vel_x*factorVelocidade)+numpy.square(vel_y*factorVelocidade)+numpy.square(abs(vel_z)))       
                
                # Construção das mensagens
                mensagem="G91 G01 X" + str(float(f'{delta_DX:.2f}')) + " Y" + str(float(f'{delta_DY:.2f}')) + " Z" + str(float(f'{delta_DZ:.3f}')) +" F" + str(abs(vectorialVel)) +"\n"
                __SendToEsp32_waitResponse(mensagem)
                # Se existir informação para ser enviada, envia pela SerialPort
                #time.delay(1)
                flag_AtualizaInterface=True

            if(getFlagRoloEsq()==True):
                mensagem="M67 E0 Q"+ str(velocidade_rolo['esquerdo']) + "\n"
                __SendToEsp32_no_waitResponse(mensagem)
                print(mensagem)
                enviaMsgWebSocket('rolEsq',velocidade_rolo['esquerdo'])
                setFalse_FlagRoloEsq()
            if(getFlagRoloDir()==True):
                mensagem="M67 E1 Q"+ str(velocidade_rolo['direito']) + "\n"
                __SendToEsp32_no_waitResponse(mensagem)
                print(mensagem)
                enviaMsgWebSocket('rolDir',velocidade_rolo['direito'])
                setFalse_FlagRoloDir()