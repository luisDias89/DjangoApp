#  Luís Dias @ 2023  #

'''
Classe estatica que contem os metodos para comandar os motores de passo a partir da SerialPort

!!  Esta classe não é para ser instanciada  !!

1º - A inicialização é feita após referenciação.
2º - Existe um bit de velocityReached(estatic).

# Sempre que alterar uma variavel dentro de uma THREAD não esquercer bloquer para escrever #
'''

from .funcoesGerais import retorna_zero_Lancabolas_mm, goToZeroAng, getCoordenadas, SendToEsp32_waitResponse
from . import funcoesGerais
import time

class controloEixos:
    
    X=0
    Y=0
    Z=0
    A=0

    #==== VARIAVEL GLOBAL QUE INDICA QUE O LANCADOR DE BOLAS ESTA REFERENCIADO ====
    eixos_referenciados=False

    @staticmethod
    def referenciarEixos(serialPort):

        print("A referenciar lançado de bolas")
        print("G90" + str(SendToEsp32_waitResponse(serialPort,"G90")))
        print("Homing X Y Z , is: " + str(SendToEsp32_waitResponse(serialPort,"$H")))
        print("Homing A , is:  " + str(SendToEsp32_waitResponse(serialPort,"$HA")))

        
        # vai para o centro de cada eixo, velocidadezeromaquina vem dos settingsLB
        goToZeroAng(serialPort)

        controloEixos.eixos_referenciados=True
                
        # enquanto não atinge não procegue

        return True

    @staticmethod
    def get_Coordenadas(serialPort):
        timeout=0.3
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            try:
                controloEixos.X,controloEixos.Y,controloEixos.Z,controloEixos.A = funcoesGerais.get_Coordenadas(serialPort)
                return controloEixos.X,controloEixos.Y,controloEixos.Z,controloEixos.A
            except Exception as e:
                print("retorno GRBL da funcao get_coordenadas com erro de sincronismo!! ", e)
            else:
                # Código a ser executado caso nenhum erro ocorra no bloco try
                pass
            finally:
                pass 
        return controloEixos.X,controloEixos.Y,controloEixos.Z,controloEixos.A
        print("TIMEOUT - FUNCAO get_Coordenadas (machine_lb/node_eixos_lancador)" )  
            
    @staticmethod   
    def get_NotSyncPosMotor():
        return controloEixos.X,controloEixos.Y,controloEixos.Z,controloEixos.A    


           