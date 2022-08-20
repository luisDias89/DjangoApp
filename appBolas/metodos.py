import math
import json
import time
import numpy
import threading
from time import time as Time
from .controlo_PID.PID import PID


start = 0
def tic():
    global start
    start = Time()
    return Time()

def toc():
    delta_t = Time() - start
    #print("Elapser ime is " + str(delta_t) + " second.")
    return delta_t


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
#=============================================================#

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
#=============================================================#


#=============================================================#
#           Comanda a velocide Z no ciclo de controlo         #
#   EX: (1000mm/s / 60 seg=16.666) * tempo de ciclo           #
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


velocidade_rolo = {
        'esquerdo': 0, 
        'direito': 0, 
        }    

#Comando para atribuir velocidade nos consumers
def comando_rolos_esquerdo(velocidade):
    global Flag_comandoMotoresRolEsq                                # Assim estou a receber a variavel Global
    velocidade_rolo['esquerdo']=velocidade
    # Só ativa a flag depois do novo valor de velocidade ser atribuido
    print("estou aqui esquerd,vel :",velocidade)   
    Flag_comandoMotoresRolEsq=True 

#Comando para atribuir velocidade nos consumers
def comando_rolos_direito(velocidade):
    global Flag_comandoMotoresRolDir
    velocidade_rolo['direito']=velocidade 
    # Só ativa a flag depois do novo valor de velocidade ser atribuido 
    Flag_comandoMotoresRolDir=True 
    print("estou aqui direito - vel :",velocidade)         
#=============================================================#


#Função de teste
def hello(meu_nome):
    print('Olá',meu_nome)


# ------ Thread de controlo ---------
# Metodo para comunicar com GRBL e receber coordenadas em formato dicionario, 
def funcComandoGRBL(ser):
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
            print(mensagem)
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
    time.sleep(2)
    delta_DZ=0.00
    vel_z=0
    TentaComunicar=False
    
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
    pidObj= PID(Ki=0.025, Kd=0.001, Kp=50, setpoint=0.00)
    pidObj.output_limits = (-VelocidadeMaximaEmZ, VelocidadeMaximaEmZ)

    while(True):
        
        if(toc()>(tmovel)):   # Garante que respeita a base de tempo
            
            tmovel=tmovel+timeSleep                     # Atualiza a nova base de tempo n+1
            #Setpoint -> valor inserido pelo usuario * fato de correção graus para milietros

            setpoint=Z_USUARIO*FatorDeCoorecaoGrausMilimetros
            presentValue= dicCordenadasControlador['Z']
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
                    
                   
                    dicCordenadasControlador=getCoordenadas()
                    while(type(dicCordenadasControlador)==bool):
                        dicCordenadasControlador=getCoordenadas()
                    #WebsocketConsumer.send(text_data=json.dumps({
                    #    'posReal_RoloTorce': str(presentValue/FatorDeCoorecaoGrausMilimetros),
                    #}))
                    
                    #print(difEntreZ)
                    #print("Sai com o type: ",type(dicCordenadasControlador))
                    
                    
                else:
                    delta_DZ=0.00
                    vel_z=0.00
                
                    
                # Velocidade a 3 dimensões
                vectorialVel=math.sqrt(numpy.square(vel_x*factorVelocidade)+numpy.square(vel_y*factorVelocidade)+numpy.square(abs(vel_z)))       
                
                # Construção das mensagens
                mensagem="G91 G01 X" + str(float(f'{delta_DX:.2f}')) + " Y" + str(float(f'{delta_DY:.2f}')) + " Z" + str(float(f'{delta_DZ:.3f}')) +" F" + str(abs(vectorialVel)) +"\n"
                __SendToEsp32_waitResponse(mensagem)
                # Se existir informação para ser enviada, envia pela SerialPort
                #time.delay(1)

            if(getFlagRoloEsq()==True):
                mensagem="M67 E0 Q"+ velocidade_rolo['esquerdo']
                __SendToEsp32_no_waitResponse(mensagem)
                setFalse_FlagRoloEsq()
            if(getFlagRoloDir()==True):
                mensagem="M67 E1 Q"+ velocidade_rolo['direito']
                __SendToEsp32_no_waitResponse(mensagem)
                setFalse_FlagRoloDir()
    



        
