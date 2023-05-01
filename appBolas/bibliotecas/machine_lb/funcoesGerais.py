from .settingsLB import angulo, maximo
import time
import numpy

def ConversorGrausToMM(Valorangulo, eixo):
    # Garante que o valor do angulo não ultrapassa o valor minimo ou maximo definido nos settingsLB.py
    if (Valorangulo > angulo["max_" + str(eixo)]):
        Valorangulo = angulo["max_" + str(eixo)]
    elif (Valorangulo < angulo["min_" + str(eixo)]):
        Valorangulo = angulo["min_" + str(eixo)]

    # Encontra o zero em mm da maquina
    somaAngulos = abs(angulo["min_" + str(eixo)]) + angulo["max_" + str(eixo)]
    anguloNormalizado = abs(angulo["min_" + str(eixo)]) + Valorangulo
    # (Valor do angulo *maximo do eixo) / maximo de angulos
    retorno = (anguloNormalizado*maximo[str(eixo)])/somaAngulos
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

# ========= A seguinte função confirma se a posição foi atingida ou o conjuntos das posições passadas foram atingidas =====
#   Para não verificar possição deve ser passado o parametro "n" na posição não verificada para não realizar a comparação    
#   
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

