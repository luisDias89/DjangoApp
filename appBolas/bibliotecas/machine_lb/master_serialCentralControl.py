from .node_eixos_lancador import controloEixos
from .node_Rolos import controloRolos
from .funcoesGerais import SendToEsp32_waitResponse
import serial
import time

class serCentralControl():

    

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

    def __init__():
        pass

    @staticmethod
    def refEixos():
        return controloEixos.referenciarEixos(serCentralControl.ser)
    
    def getInfo_eixos_ref():
        return controloEixos.eixos_referenciados

    @staticmethod
    def get_Coordenadas():
        return controloEixos.get_Coordenadas(serCentralControl.ser)   

    @staticmethod   
    def get_NotSyncPosMotor():
        return controloEixos.get_NotSyncPosMotor()  
    
    @staticmethod
    def send_toGRBL(msg):
        SendToEsp32_waitResponse(serCentralControl.ser, msg)

    @staticmethod
    def set_velocityRolo(velocidade, QualRolo):
        if(QualRolo =="dir"):
            controloRolos.set_velocidadeRolo_Dir(serCentralControl.ser, velocidade)
        elif(QualRolo == "esq"):
            controloRolos.set_velocidadeRolo_Esq(serCentralControl.ser, velocidade)
    
    @staticmethod
    def set_velocityRolos(velocidadeRolEsq, velocidadeRolDir):
        controloRolos.set_velRolosRampa(serCentralControl.ser,targetVelocityRolEsq=int(velocidadeRolEsq), targetVelocityRolDir=int(velocidadeRolDir))

    
        
      
