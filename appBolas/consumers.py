import json
from channels.generic.websocket import WebsocketConsumer
import threading
from . import metodos
import time
from .bibliotecas.machine_lb import serCentralControl


#Variaveis auxiliares
velHorizontal=0


class ConsumerJoystick(WebsocketConsumer): 

    def connect(self):
        self.accept()                           # Aceita conexão WebSocket
        self.envioObjetoSendParaThread()        # Cria link do Objeto para metodos, de forma a ser acessivel
        
        '''
        metodos.enviaPorWebSocket()
        self.send(text_data=json.dumps({
            'type': 'conexão com sucesso',
            'message': 'Estás agora conectado!'
        }))
        '''
        
    
    #Função responsavel por linkar o objeto de envio de mensagem para poder ser acedida na Thread
    def envioObjetoSendParaThread(self):
        metodos.objWebSocket=self



    #def init(self):
    threading.Thread(target=metodos.funcComandoGRBL, args=()).start()
    #init            #Inicio da Thread

    


    #inicio de variaveis auxiliares
    varPosicaoInic=False   
    dicCoordenadas=False 
    tickrate=0.2

    
    #Equação para construir a equação do roloTorce
    #rolo_torceMaximo=770                                     #Valor definido experimentalmente, maximo desde o meio até à ponta.
    #mdwa=rolo_torceMaximo/50

    #Inicio do temporizador que envia as velocidades, este temporizador so executa 1 vez, após 2 segundos
    #t = threading.Timer(2, metodos.funcVelocidade(ser,X,Y,Z))      # Temporizador, a cada tickrate executa a função contida em metodos    
    print('inicio da thread')


    def receive(self, text_data=None, bytes_data=None): 
        text_data_json = json.loads(text_data)                          # Recebe a mensagem atravez do Websocket

        # Recebe qual o comando que quer enviar ao GRBL, e reenvia a resposta
        if 'enviaComando_toGRBL' in text_data_json:
            # Pergunta ao GRBL, caso tenha valor entra na primeira função que envia  recebe a confirmação, caso contrario só pergunta
            comando = text_data_json['enviaComando_toGRBL']                     # Guarda na variavel o valor do comando
            if 'newValue' in text_data_json:
                novoValor = text_data_json['newValue']                          # Guarda na variavel o novo valor a ser atribuido
                if metodos.setGRBL(comando, novoValor) == "ok\r\n":             # Se a resposta da atribuição for ok, então envia o novo valor
                    self.send(text_data=json.dumps({
                        'DoComandoGRBL' :  text_data_json['enviaComando_toGRBL'],                      
                        'resposta': str(novoValor),
                    }))  
            else:
                self.send(text_data=json.dumps({
                'DoComandoGRBL' :  comando,                      
                'resposta': str(metodos.askGRBL(text_data_json['enviaComando_toGRBL'])),
                }))       

    
        # Envia a velocidade pretendida para os rolos
        if 'comando_rolo_esq' in text_data_json:
            metodos.comando_rolos_esquerdo(text_data_json['comando_rolo_esq'])
            time.sleep(0.2)                    #Espero pelo processamento


        if 'comando_rolo_dir' in text_data_json:
            metodos.comando_rolos_direito(text_data_json['comando_rolo_dir'])
            time.sleep(0.2)
            
            
        # Recebe as mensagem em espera do WebSocket
        if 'message' in text_data_json:
             if(text_data_json['message']!= "100"):
                pass
                #mensagem="G01 X10 F1000\n"
                #ser.write(mensagem.encode())
                #print("enviei ao motor a mensagem" + mensagem)
        
        
        
        #============= Se existir deslHorizontal e deslVertical na mensagem JSON então ===============
        if 'deslHorizontal' in text_data_json and 'deslVertical' in text_data_json:
            # Se um dos valores for diferente de 0, então devemos enviar um comando de velocidade joystick
            if((text_data_json['deslHorizontal'])!="0") or ((text_data_json['deslVertical'])!="0"):    
                
                #Atualiza os indicadores de velocidade com o estado atual da velocidade
                metodos.vel_x=float(text_data_json['deslHorizontal'])
                metodos.vel_y=float(text_data_json['deslVertical'])
                

            else:   #Caso as duas velocidades sejão 0 então coloca os ponteiros de velocidade a 0
                metodos.vel_x=float(0)
                metodos.vel_y=float(0)
                

        if 'RoloTorce' in text_data_json:                                   # Se contiver a mensagem do rolo então
            
            # A Inclinação atual do lançador é enviada para a coordenada Z
            # Internamnte o metodo consumers está constantemente a monitorizar a posição
            # e a corrigila
            # Recebe a inclinação do lançador
            
            metodos.Z_USUARIO=int(text_data_json['RoloTorce'])              # Atribui o angulo

        if 'LANCAR_BOLA' in text_data_json:                                  # Se contiver a mensagem para LANÇAR BOLA
            metodos.lancar_bola()                                            # Seta a função para lançar a bola
            

    

    # Função para enviar valores do dicCordenadas Controlador para o interface
    # inclui a função de bloquear as variaveis para não entrar em conflito com 
    # a thread paralela de processamento da maquina.
    def sendToInterface(self,comando):
        
        metodos.memoryLOCK.acquire()
        #X,Y,Z,A = metodos.serCentralControl.get_Coordenadas()
        X,Y,Z,A = serCentralControl.requestFunction_GRBL("get_Coordenadas")
        metodos.memoryLOCK.release()

        if comando == "X":
            bufferValor = X
        elif comando == "Y":
            bufferValor = Y
        elif comando == "Z":
            bufferValor = Z
        elif comando == "A":
            bufferValor = A
        metodos.objWebSocket.send(text_data=json.dumps({comando : bufferValor}))
        
    
   