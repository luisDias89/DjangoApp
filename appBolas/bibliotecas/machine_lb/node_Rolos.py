#  Luís Dias @ 2023  #

'''
Classe estatica que guarda o estado atual dos ROLOS

!!  Esta classe não é para ser instanciada  !!

1º - A inicialização é feita após referenciação.
2º - As mudanças de velocidade acontecem sempre em relação ao valor anterior
3º - SettingsLB contem valor de aceleração, que é comum aos dois rolos
4º - Existe um bit de targetReached(estatic)

#Sempre que alterar uma variavel dentro de uma THREAD não esquercer bloquer para escrever#
'''
from .funcoesGerais import SendToEsp32_no_waitResponse
import time

class controloRolos:
    velActRoloEsq=0
    velActRoloDir=0

    @staticmethod
    def set_velocidadeRolo_Dir(ser, velocidadeRolo):
        controloRolos.set_velRolosRampa(ser,targetVelocityRolEsq=controloRolos.velActRoloEsq,targetVelocityRolDir=int(velocidadeRolo))
        #mensagem="M67 E1 Q"+ str(velocidadeRolo)
        #SendToEsp32_no_waitResponse(ser,mensagem)
        #print(mensagem)

    @staticmethod
    def set_velocidadeRolo_Esq(ser, velocidadeRolo):
        controloRolos.set_velRolosRampa(ser,targetVelocityRolEsq=int(velocidadeRolo), targetVelocityRolDir=controloRolos.velActRoloDir)
        #mensagem="M67 E0 Q"+ str(velocidadeRolo)
        #SendToEsp32_no_waitResponse(ser,mensagem)
        #print(mensagem)    

    @staticmethod
    def set_velRolosRampa(ser,targetVelocityRolEsq, targetVelocityRolDir):
        
        #Calcula a diferença de velocidade entre a atual guardada na memoria com a nova velocidade
        difVelRolEsq = controloRolos.velActRoloEsq-targetVelocityRolEsq
        difVelRolDir = controloRolos.velActRoloDir-targetVelocityRolDir
        
        t=1             # segundos
        tickRate=0.1    # Divisão de tempo de cada iteração, atenção, tem que ser divisor do t!!
        acel = acelRolEsq = acelRolDir= 30

        TIMEOUT= (100/acel)+2               
        # V  =  V0 + at
        # V  -> é a velocidade final
        # V0 -> é a velocidade inicial
        # a  -> é a aceleração
        # t  -> é o tempo decorrido desde o início do movimento.
        # targetVelocityRolEsq  =  controloRolos.velActRoloEsq + a*t

        # Garante que se a velocidade do ROLO não mudar então, não divide por 0, nem atualiza
        if(difVelRolEsq != 0):
            #calculo o sentido da aceleração
            acelRolEsq *= (targetVelocityRolEsq-controloRolos.velActRoloEsq)/abs(targetVelocityRolEsq-controloRolos.velActRoloEsq)      
        if(difVelRolDir != 0 ):
            #calculo o sentido da aceleração
            acelRolDir *= (targetVelocityRolDir-controloRolos.velActRoloDir)/abs(targetVelocityRolDir-controloRolos.velActRoloDir)
        tempo=0
        start_time = time.time()
        targetFinishEsq = targetFinishDir = False                                                 # Variaveis para marcam quando é que chegaram ao set point
        if(difVelRolDir != 0  or difVelRolEsq != 0):
            while(True):
                                    
                # Comanda o rolo esquerdo
                if(difVelRolEsq != 0 and not targetFinishEsq):                                                                      # Se existe espaço para comando de velocidade
                    velAcionamento = controloRolos.velActRoloEsq + acelRolEsq*tempo  # V = V0 + a.t             # Calcula em função do tempo quando é a nova velocidade  
                    # Bloco de envio de G-CODE
                    mensagem = "M67 E0 Q" + str(velAcionamento)                                                 # Constroi a mensagem NC
                    SendToEsp32_no_waitResponse(ser, mensagem)                                                  # Envia para o comando a mensagem NC
                    if (abs(targetVelocityRolEsq-velAcionamento)<2):                                            # Se atingir o Setpoint, então   
                        targetFinishEsq=True                                                                           # marca a sua chegada
                elif (not targetFinishEsq):                                                                     # caso não exista espaço para comando, então levanta logo o targeFinish 
                    targetFinishEsq=True

                # Comanda o rolo direito
                if(difVelRolDir != 0 and not targetFinishDir):                                                                      # Se existe espaço para comando de velocidade
                    velAcionamento = controloRolos.velActRoloDir + acelRolDir*tempo  # V = V0 + a.t             # Calcula em função do tempo quando é a nova velocidade
                    # Bloco de envio de G-CODE                                                                  # Constroi a mensagem NC        
                    mensagem = "M67 E1 Q" + str(velAcionamento)                                                 # Envia para o comando a mensagem NC
                    SendToEsp32_no_waitResponse(ser, mensagem)                                                             
                    if (abs(targetVelocityRolDir-velAcionamento)<2):                                            # Se atingir o Setpoint, então  
                        targetFinishDir=True                                                                           # marca a sua chegada
                elif(not targetFinishDir):                                                                      # caso não exista espaço para comando,                 
                    targetFinishDir=True                                                                           # então levanta logo o targeFinish 

                # o loop é atrasado pelos Send, a cada send para o GRBL usa 1/20 de segundo
                tempo = time.time() - start_time    # Calcula quanto tempo já passou    

                if(targetFinishDir and targetFinishEsq):                      # Quando os dois atingem o setpoint, sai do controlo
                    break

                # Sai por TimeOut
                if tempo > TIMEOUT:
                    print("Timeout! Ultrapasou o tempo maximo para comandar o ROLOS.")
                    break


            if(difVelRolEsq != 0):            
                # Bloco de envio de G-CODE - E1 ROLO ESQUERDO
                mensagem = "M67 E0 Q"+ str(targetVelocityRolEsq)
                print(mensagem)
                SendToEsp32_no_waitResponse(ser, mensagem)
                controloRolos.velActRoloEsq=targetVelocityRolEsq
            if(difVelRolDir != 0):
                # Bloco de envio de G-CODE - E0 ROLO DIREITO
                mensagem = "M67 E1 Q"+ str(targetVelocityRolDir)
                print(mensagem)
                SendToEsp32_no_waitResponse(ser, mensagem)
                controloRolos.velActRoloDir=targetVelocityRolDir
        return True
