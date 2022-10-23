import json
from channels.generic.websocket import WebsocketConsumer
import threading
from . import metodos
import time


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
            'message': 'Tu estás agora conectado!'
        }))
        '''
        
    
    #Função responsavel por linkar o objeto de envio de mensagem para poder ser acedida na Thread
    def envioObjetoSendParaThread(self):
        metodos.objWebSocket=self

    # O Objeto Thread conditions tem que ser partilhado pelas duas Threads
    c = metodos.c

    #def init(self):
    threading.Thread(target=metodos.funcComandoGRBL, args=()).start()
    #init            #Inicio da Thread

    


    #inicio de variaveis auxiliares
    varPosicaoInic=False   
    dicCoordenadas=False 
    tickrate=0.2

    
    #Equação para construir a equação do roloTorce
    rolo_torceMaximo=770                                     #Valor definido experimentalmente, maximo desde o meio até à ponta.
    m=rolo_torceMaximo/50

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
                if metodos.setGRBL(comando, novoValor) == "ok\r\n":             #Se a resposta da atribuição for ok, então envia o novo valor
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
            #self.sendToInterface('rolDir')


        if 'comando_rolo_dir' in text_data_json:
            metodos.comando_rolos_direito(text_data_json['comando_rolo_dir'])
            time.sleep(0.2)
            #self.sendToInterface('rolDir')     # Caso queimaros enviar diretamente 
            
            
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
            print("Recebo do pagina Web: ",text_data_json['RoloTorce'])
            metodos.Z_USUARIO=int(text_data_json['RoloTorce'])              # Atribui o angulo
            
            #print("Posição em Z atual",self.varPosicaoInic )
            #print("Comando RoloTorce Recebido:", metodos.Z)                 # Nos metodos tenho uma função que retorna a posição e Z

    

    # Função para enviar valores do dicCordenadas Controlador para o interface
    # inclui a função de bloquear as variaveis para não entrar em conflito com 
    # a thread paralela de processamento da maquina.
    def sendToInterface(self,comando):
        self.c.acquire()
        if metodos.flag==1:
            metodos.flag=0
            self.send(text_data=json.dumps({
                comando: metodos.dicCordenadasControlador[comando],
            }))
            #print(metodos.vel_x,metodos.vel_y)
            metodos.flag=1
            self.c.notify_all()
        else:
            self.c.wait()
        self.c.release()
    
   