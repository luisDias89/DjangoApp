from .settingsLB import configLB
import time
import numpy


def retorna_zero_Lancabolas_mm(eixo):
        '''
         Eixos possiveis declarados no ficheiro JSON
         Até à data da Versão existe eixo: X - Y -  Z  - A 
        '''
    # Encontra o zero em mm da maquina
        somaAngulos = abs(configLB.angulo["min_" + str(eixo)]) + configLB.angulo["max_" + str(eixo)]
        retorno = (abs(configLB.angulo["min_" + str(eixo)])*configLB.maximo[str(eixo)])/somaAngulos
        #print(str(eixo) + " " + str(round(retorno, 2)))
        return round(retorno, 2)
def retorna_retemBolaDispensador():
        '''
        Retorna a posição em mm do dispensador de bolas, eixo A 
        '''
        return ConversorGrausToMM(configLB.graus_desl_a["retemBola"],"A")

def ConversorGrausToMM(Valorangulo, eixo):
    # Garante que o valor do angulo não ultrapassa o valor minimo ou maximo definido nos settingsLB.py
    if (Valorangulo > configLB.angulo["max_" + str(eixo)]):
        Valorangulo = configLB.angulo["max_" + str(eixo)]
    elif (Valorangulo < configLB.angulo["min_" + str(eixo)]):
        Valorangulo = configLB.angulo["min_" + str(eixo)]

    # Encontra o zero em mm da maquina
    somaAngulos = abs(configLB.angulo["min_" + str(eixo)]) + configLB.angulo["max_" + str(eixo)]
    anguloNormalizado = abs(configLB.angulo["min_" + str(eixo)]) + Valorangulo
    # (Valor do angulo *maximo do eixo) / maximo de angulos
    retorno = (anguloNormalizado*configLB.maximo[str(eixo)])/somaAngulos
    return round(retorno, 2)


def getCoordenadas(ser):
        if ser.isOpen():                                        # Se a porta serial está aberta
            # remove toda a data na fila de entrada, só para se focar no pedido seguinte
            ser.flushInput()
            # Pergunta quais as coordenadas atuais (Comando GRBL "?\n")
            mensagem = "?\n"
            # Escreve na SerialPort "?\n" para receber as coordenadas
            ser.write(mensagem.encode())
            # Espera a resposta do arduino
            time.sleep(0.05)     # Não retirar é obrigatório!!!!                           
            if ser.inWaiting() > 10:                             # Se tiver mais de 50 caracteres então
                # recebe a mensagem e insere na variavel
                mensagemlida = ser.readline()
                
                SerialPort = mensagemlida.decode()                   # Passa de Byte para string
                SerialPort = SerialPort.replace('<Run|MPos:', "")
                SerialPort = SerialPort.replace('<Idle|MPos:', "")
                SerialPort = SerialPort.replace('<Home|MPos:', "")
                # Replaces seguintes é para limpar a mensagem
                SerialPort = SerialPort.replace("|FS:", ",")
                SerialPort = SerialPort.replace(">\r\n", "")
                SerialPort = SerialPort.replace("|WCO:", ",")
                SerialPort = SerialPort.replace("|Ov:", ",")
                SerialPort = SerialPort.replace("<Alarm|MPos:", ",")
                arrayEstadoMaquina = SerialPort.split(",")

                try:
                    if (numpy.size(arrayEstadoMaquina) > 2):
                        dic = {
                            'X': float(arrayEstadoMaquina[0]),
                            'Y': float(arrayEstadoMaquina[1]),
                            'Z': float(arrayEstadoMaquina[2]),
                            "A": float(arrayEstadoMaquina[3]),
                            # "rolDir":float(arrayEstadoMaquina[4])
                        }
                        # remove data after reading     # Limpa o buffer do SerialPort
                        ser.flushInput()
                        return dic
                    # remove data after reading     # Limpa o buffer do SerialPort
                    ser.flushInput()
                    return False
                except Exception as e:
                    print("Erro em funçes Gerais getCoordenadas com a mensagem:", str(e))
                    return False


def get_Coordenadas(ser):
        if ser.isOpen():                                        # Se a porta serial está aberta
            # remove toda a data na fila de entrada, só para se focar no pedido seguinte
            ser.flushInput()
            # Pergunta quais as coordenadas atuais (Comando GRBL "?\n")
            mensagem = "?\n"
            # Escreve na SerialPort "?\n" para receber as coordenadas
            ser.write(mensagem.encode())
            # Espera a resposta do arduino
            time.sleep(0.04)     # Não retirar é obrigatório!!!!                           
            if ser.inWaiting() > 0:                             # Se tiver mais de 50 caracteres então
                # recebe a mensagem e insere na variavel
                mensagemlida = ser.readline()
                
                SerialPort = mensagemlida.decode()                   # Passa de Byte para string
                SerialPort = SerialPort.replace('<Run|MPos:', "")
                SerialPort = SerialPort.replace('<Idle|MPos:', "")
                SerialPort = SerialPort.replace('<Home|MPos:', "")
                # Replaces seguintes é para limpar a mensagem
                SerialPort = SerialPort.replace("|FS:", ",")
                SerialPort = SerialPort.replace(">\r\n", "")
                SerialPort = SerialPort.replace("|WCO:", ",")
                SerialPort = SerialPort.replace("|Ov:", ",")
                SerialPort = SerialPort.replace("<Alarm|MPos:", ",")
                arrayEstadoMaquina = SerialPort.split(",")

                if (numpy.size(arrayEstadoMaquina) > 2):
                    ser.flushInput()
                    return float(arrayEstadoMaquina[0]),float(arrayEstadoMaquina[1]),float(arrayEstadoMaquina[2]),float(arrayEstadoMaquina[3])
                # remove data after reading     # Limpa o buffer do SerialPort
                ser.flushInput()
                return False

#=========================================================================================================================#
# ========= A seguinte função confirma se a posição foi atingida ou o conjuntos das posições passadas foram atingidas ====#
#   Para não verificar possição deve ser passado o parametro "n" na posição não verificada para não realizar a comparação #   
#                                                                                                                         #
def confirmaPosicaoFinal(ser, X="n", Y="n", Z="n", A="n"):
        # Garante que vem o dicionario e não ocorre um erro de RUNTIME
        posAtual = getCoordenadas(ser)
        while (posAtual == False):
            posAtual = getCoordenadas(ser)     
        # Caso não seja passado o valor por parametro, então fica "n" e não entra nos calculos.
        if ((posAtual["X"] == X or X == "n") and (posAtual["Y"] == Y or Y == "n") and (posAtual["Z"] == Z or Z == "n") and (posAtual["A"] == A or A == "n")):
            return True
        else:
            return False


      
         
#================================================#
#       Metodo para comunicar com o GRBL         #
#       Recebe o parâmetro mensagem em "msg"     #
#       envia com \n, retorna a primeira msg de  #
#       resposta do GRBL                         #
def SendToEsp32_waitResponse(ser,mensagem):
        """
        Ser -> Objeto Serial Port
        mensagem -> String de envio
        Instruões: envia e aguarda resposta sempre, retorna a primeira
        mensagem de n possiveis.
        """
        if ser.isOpen():
            SerialPort=""                           # Sem isto existir dá erro o PYTHON, a variavel não é subscrevida.
            mensagem= mensagem + '\n'                   # Contrução da mensagem, não apagar o '\n', senão não funciona
            ser.write(mensagem.encode())            # Envia a mensagem por RS232
            TentaComunicar=True                     # Tenta comunicar a True para iniciar a comunicação, repetidamente até receber "OK"
            # Loop de controlo , só este loop (obrigatoriamente) tem que fazer a comunicação por RS232
            timeout=10
            start_time = time.time()
            while(TentaComunicar and (time.time() - start_time) < timeout):                                  
                time.sleep(0.01)
                if  ser.inWaiting()>0 :                             # Se se algum caracter já estiver no buffer executa
                    mensagemlida=ser.readline()                     # recebe a mensagem e insere na variavel
                    SerialPort = mensagemlida.decode()              # Passa de Byte para string e imprim na tela
                    return SerialPort
                if("ok" in SerialPort):
                    #print("fiquei no segundo IF")
                    TentaComunicar=False
                    ser.flushInput() 
                    return "OK"
                if((time.time() - start_time) > timeout):
                    print("TIMEOUT - FUNCAO SendToEsp32_waitResponse (machine_lb/funcoesGerais)" )
                    return "TIMEOUT"

def SendToEsp32_no_waitResponse(ser,mensagem):
    if ser.isOpen():
        mensagem= mensagem + '\n'               # Obrigatorio para no bloquear o GRBL
        ser.write(mensagem.encode())            # Envia a mensagem por RS232  
        time.sleep(0.05)                           
        ser.flushInput() 

def gotTo_mm(serialPort,X="n", Y="n", Z="n", A="n", F=1000):
        mensagem = "G90 G01"
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
        SendToEsp32_waitResponse(serialPort,mensagem)

def gotTo_graus(serialPort, X="n", Y="n", Z="n", A="n", F=1000):                  # Se não chegar nenhum valor, a posição do eixo que é atribuido é n -> nenhum valor
        # send_to_GRBL("G90")
        mensagem = "G90 G01"
        if (X != "n"):
            mensagem += " X" + str(ConversorGrausToMM(X, "X"))
        if (Y != "n"):
            mensagem += " Y" + str(ConversorGrausToMM(Y, "Y"))
        if (Z != "n"):
            mensagem += " Z" + str(ConversorGrausToMM(Z, "Z"))
        if (A != "n"):
            mensagem += " A" + str(ConversorGrausToMM(A, "A"))
        mensagem += " F" + str(F)
        SendToEsp32_waitResponse(serialPort,mensagem)

def goToZeroAng(serialPort):
    X0=retorna_zero_Lancabolas_mm("X")
    Y0=retorna_zero_Lancabolas_mm("Y")
    Z0=retorna_zero_Lancabolas_mm("Z")
    A0=retorna_retemBolaDispensador()
    gotTo_mm(serialPort,X=X0, Y=Y0, Z=Z0, A=A0, F=configLB.velocidadeZeroMaquina)
    while (not confirmaPosicaoFinal(serialPort,X=X0, Y=Y0, Z=Z0, A=A0)):
        time.sleep(0.3)

