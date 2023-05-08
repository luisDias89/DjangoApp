from .settingsLB import configLB
import time
import numpy

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
            time.sleep(0.05)

            if ser.inWaiting() > 0:                             # Se tiver algum caracter então executa
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
                    ser.flushInput()
                    return dic
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
def send_to_GRBL(ser, msg):
    """
    Ser -> Objeto Serial Port
    msg -> String de envio
    Instruões: envia e aguarda resposta sempre, retorna a primeira
    mensagem de n possiveis.
    """
    if ser.isOpen():                                   # se a porta com esta aberta
        ser.flushInput()                                    # Remove o buffer de entrada, caso existam mensagens                                  
        mensagem= msg + '\n'                                     # Contrução da mensagem, não apagar o '\n', senão não funciona
        #print('Sending: ' + mensagem)                           # Bloco de depuração
        ser.write(mensagem.encode())                        # Bloco de envio de G-CODE
        time.sleep(0.1)                                     
        grbl_out = ser.readlines()                          # Lee todas as linhas que gera como resposta do GRBL
        resposta=grbl_out[0].decode()
        return resposta                                     # Quando pretendemos só o ok, ficamos apenas pela primeira linha [0]
