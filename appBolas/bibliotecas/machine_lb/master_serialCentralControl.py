from .node_eixos_lancador import controloEixos
from .node_Rolos import controloRolos
from .funcoesGerais import SendToEsp32_waitResponse
import serial
import time
import threading

class serCentralControl():
    lock = threading.Lock()

    # O objeto serial porte é somente declarado dentro desta classe, 
    # ligação Serial com o ESP32, estatico, pertence a toda aplicação!
    ser = serial.Serial(
            port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
    )
    time.sleep(0.5)

    # Sempre que o strobeCALL for diferente de 0, não executa a função, e aguarda em loop até ter acesso.
    # Cada verificação de loop deve aguardar 0.01 segundos no maximo.
    strobeCALL = 0                       

    def __init__():
        pass


    @staticmethod
    def requestFunction_GRBL(request):
        with serCentralControl.lock:
            return serCentralControl.process_requests(request)  

    @staticmethod
    def process_requests(request):
        #Thread STROBE!! Somentes esta Thread pode comunicar com o GRBL, e uma mensagem de cada vez
        while serCentralControl.strobeCALL>0:
            pass
        serCentralControl.strobeCALL +=1

            #-------- Referenciação de eixo ---------#   
        if request == "refEixos":
            result = controloEixos.referenciarEixos(serCentralControl.ser)

            #--------- Eixos referenciados? --------#
        elif request == "getInfo_eixos_ref":
            result = controloEixos.eixos_referenciados

            #--------- Ober cotas atuais X,Y,Z,A --------#
        elif request == "get_Coordenadas":
            result = controloEixos.get_Coordenadas(serCentralControl.ser) 

            #--------- Obter coordenadas sem questionar GRBL--------#
        elif request == "get_NotSyncPosMotor":
            result = controloEixos.get_NotSyncPosMotor()  

            #--------- Envia uma mensagem para o GRBL GRBL--------#
        elif request.startswith("send_toGRBL:"):
            msg = request.split(":")[1]             # Obtem a mensagem que vem à frente dos :
            result = SendToEsp32_waitResponse(serCentralControl.ser, msg)

            #--------- Atribuir velocidade ao Rolo GRBL--------#
        elif request.startswith("set_velocityRolo:"):
            params = request.split(":")[1].split(",")
            velocidade = int(params[0])
            qualRolo = params[1]
            '''
            Rolo esquerdo -> "esq"
            Rolo direito  -> "dir"
            '''
            if(qualRolo == "dir"):
                controloRolos.set_velocidadeRolo_Dir(serCentralControl.ser, velocidade)
                result = "Success"
            elif(qualRolo == "esq"):
                controloRolos.set_velocidadeRolo_Esq(serCentralControl.ser, velocidade)
                result = "Success"
            else:
                result = "ERROR - WRONG message"

            #--------- Atribuir velocidade aos Rolos GRBL--------#
        elif request.startswith("set_velocityRolos:"):
            params = request.split(":")[1].split(",")
            velocidadeRolEsq = int(params[0])
            velocidadeRolDir = int(params[1])
            controloRolos.set_velRolosRampa(serCentralControl.ser,targetVelocityRolEsq=int(velocidadeRolEsq), targetVelocityRolDir=int(velocidadeRolDir))
            result = "Success"

            #--------- Retorna a velocidade do Rolo esquerdo e Rolo direito-------#
        elif request == "get_velocityRolos":
            result = (controloRolos.velActRoloEsq,controloRolos.velActRoloDir)

            #--------- Obtem a velocidade do Rolo esquerdo ou rolo direito -------#
        elif request.startswith("get_velocityRolo:"):
            rolo = request.split(":")[1]
            '''
            Rolo esquerdo -> "esq"
            Rolo direito  -> "dir"
            '''
            if(rolo == "dir"):
                result = controloRolos.velActRoloDir
            elif(rolo == "esq"):
                result = controloRolos.velActRoloEsq
            else:
                result = "ERROR - WRONG message"

        else:
            result = "Invalid request"
        serCentralControl.strobeCALL -=1
        return result

    
        
      
