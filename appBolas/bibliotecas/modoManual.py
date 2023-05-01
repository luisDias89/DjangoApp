# ============================================================#
#      CLASE THREAD MODO MANUAL DO LANÇADOR DE BOLAS UA       #
#                     @ Luís Dias 2023   
#=============================================================#

# ============================================================#
#   TODOS OS MOVIMENTOS EM MODO MANUAL SÃO GERIDOS POR ESTA   #
#  CLASSE E AS BIBLIOTECAS FILHAS QUE A COMPOEM               #

'''
A classe threading.Thread é uma subclasse da classe threading._Verbose. Ela herda os seguintes métodos:

    start(): inicia a execução da thread;
    run(): método que será executado na thread;
    join(timeout=None): espera pela finalização da thread;
    is_alive(): retorna True se a thread estiver em execução, False caso contrário;
    getName(): retorna o nome da thread;
    setName(name): define o nome da thread;
    ident: retorna o identificador da thread;
    daemon: um booleano que indica se a thread é um daemon;
    isDaemon(): retorna True se a thread for um daemon, False caso contrário.

Além desses métodos, também é possível acessar algumas propriedades, como name, ident, daemon, is_alive.
'''

import threading
import time
from .machine_lb import *
memoryLOCK = threading.Lock()

# Declaração de memorias devem ser feitas fora da classe para serem imutaveis entre declaraçes

class threadManualMode(threading.Thread):
    iterador = 0

    # Variaveis de pedidos, PIPE-LINE
    LANCAR_BOLA=False

    def __init__(self, ser):
        super(threadManualMode, self).__init__()
        self.stopped = True
        self.ser = ser
    
    def stop(self):
        print("passei pelo metodo Stop")
        memoryLOCK.acquire()
        self.stopped = True
        memoryLOCK.release()
    
    def start(self):
        print("passei pelo metodo start")
        memoryLOCK.acquire()
        self.stopped = False
        memoryLOCK.release()
        if not self.is_alive():
            super(threadManualMode, self).start()
    
    def set_LANCAR_BOLA(self):
        global memoryLOCK
        memoryLOCK.acquire()
        self.LANCAR_BOLA=True
        memoryLOCK.release()

    def run(self):
        self.stopped = False                                                    # Não retirar do código, garante que só salta do While externamente à Thread
        global iterador
        print("Nova thread MANUALMODE iniciada")
        while True:                                                 # Enquato não houver um pedido para parar a THREAD
            if not self.stopped:                                    # se não estiver parada então executa
                if (self.LANCAR_BOLA == True):
                    print("Enviei valor ao GRBL")
                    # nota o dicionario vem do settingsLB.py 
                    mensagem = "G90 G01 A" + \
                        str(ConversorGrausToMM(graus_desl_a["lancaBola"], "A")) + " F" + velocidadeAvancoGate  + "\n"
                    
                    #self.send_to_GRBL(mensagem)
                    self.ser.flushInput()
                    self.ser.write(mensagem.encode())                      # Bloco de envio de G-CODE
                    mensagem = "G90 G01 A" + \
                        str(ConversorGrausToMM(graus_desl_a["retemBola"], "A")) + " F" + velocidadeAvancoGate  + "\n"
                    # Bloco de envio de G-CODE
                    self.ser.write(mensagem.encode())
                    print("Entrei no While")
                    
                    self.LANCAR_BOLA = False    
                    
            else:
                pass

    


