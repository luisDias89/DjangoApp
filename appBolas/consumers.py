import json
from channels.generic.websocket import WebsocketConsumer
import serial
import threading
from . import metodos
import time


#Variaveis auxiliares
velHorizontal=0

# ligação Serial com o Arduino, initilizado após biblioteca de Motor com RaspBery
ser = serial.Serial(
        port='/dev/ttyUSB0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

time.sleep(0.5)
mensagem="G91 G01 X10 F1000\n"
ser.write(mensagem.encode())


class ConsumerJoystick(WebsocketConsumer): 

    def connect(self):
        self.accept()

        self.send(text_data=json.dumps({
            'type': 'conexão com sucesso',
            'message': 'Tu estás agora conectado!'
        }))
    


    #def init(self):
    threading.Thread(target=metodos.funcComandoGRBL, args=(ser,)).start()
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


        if 'comando_rolo_esq' in text_data_json:
            print(text_data_json['comando_rolo_esq'])
            metodos.comando_rolos_esquerdo(text_data_json['comando_rolo_esq'])
        if 'comando_rolo_dir' in text_data_json:
            print(text_data_json['comando_rolo_dir'])
            metodos.comando_rolos_direito(text_data_json['comando_rolo_dir'])
            
         

        # Recebe as mensagem em espera do WebSocket
        if 'message' in text_data_json:
             if(text_data_json['message']!= "100"):
                
                #mensagem="G01 X10 F1000\n"
                #ser.write(mensagem.encode())
                print("enviei ao motor a mensagem" + mensagem)
        
        
        
        #============= Se existir deslHorizontal e deslVertical na mensagem JSON então ===============
        if 'deslHorizontal' in text_data_json and 'deslVertical' in text_data_json:
            # Se um dos valores for diferente de 0, então devemos enviar um comando de velocidade joystick
            if((text_data_json['deslHorizontal'])!="0") or ((text_data_json['deslVertical'])!="0"):    
                
                #Atualiza os indicadores de velocidade com o estado atual da velocidade
                metodos.vel_x=float(text_data_json['deslHorizontal'])
                metodos.vel_y=float(text_data_json['deslVertical'])
                self.send(text_data=json.dumps({
                    'cordenadas X': metodos.dicCordenadasControlador['X'],
                    'cordenadas Y': metodos.dicCordenadasControlador['Y'],
                }))
                #print(metodos.vel_x,metodos.vel_y)


                #Tenta receber as cordenadas 3 vezes
                #dicCoordenadas=metodos.getCoordenadas(ser)              # Recebo as coordenadas
                #if(type(dicCoordenadas)!=bool):                         # Testar se vem um dicionario, senão da erro de runtime!
                #print("O Valor")
                #mensagem="G01 X10 F2000\n"
                #ser.write(mensagem.encode())
                #metodos.X=float(text_data_json['deslHorizontal'])
                #metodos.Y=float(text_data_json['deslVertical'])

            else:   #Caso as duas velocidades sejão 0 então coloca os ponteiros de velocidade a 0
                metodos.vel_x=float(0)
                metodos.vel_y=float(0)

                #print(metodos.vel_x,metodos.vel_y)
                #mensagem="G01 X-10 F2000\n"
                #ser.write(mensagem.encode())
                #mensagem="!"
                #ser.write(mensagem.encode())
                #time.sleep(0.1)
                #mensagem="$~\n"
                #ser.write(mensagem.encode())
                

        if 'RoloTorce' in text_data_json:                                   # Se contiver a mensagem do rolo então
            
            # A Inclinação atual do lançador é enviada para a coordenada Z
            # Internamnte o metodo consumers está constantemente a monitorizar a posição
            # e a corrigila
            # Recebe a inclinação do lançador
            print("Recebo do pagina Web: ",text_data_json['RoloTorce'])
            metodos.Z_USUARIO=int(text_data_json['RoloTorce'])              # Atribui o angulo
            

            




            # O GRBL é que controla a posição dos eixos e portanto todos o valores 
            # são atualizados com a pergunta ao controlador da posição dos mesmos.
            
            #if self.varPosicaoInic==False:                                  # Se for a primeira vez e ainda não ouver registo da posição inicial
            #    while(type(self.dicCoordenadas)==bool):                     # Enquato for bool tenta receber as coordenadas, só precisa receber 1 vez
            #        self.dicCoordenadas=metodos.getCoordenadas(ser)         # É preciso obter coordenadas mas agora com a função do motor
            #        print(self.dicCoordenadas)
            #        pass
            #    self.varPosicaoInic=self.dicCoordenadas['Z']                # Recebe as coordenadas iniciais
            #metodos.Z=text_data_json['RoloTorce']                      # Recebo a atualização do RoloTorce
            


            #print("Posição em Z atual",self.varPosicaoInic )
            #print("Comando RoloTorce Recebido:", metodos.Z)                 # Nos metodos tenho uma função que retorna a posição e Z

            '''
            else:
                
                if ser.isOpen():
                    ser.flushInput()                                    #remove data after reading
                    mensagem="G90"
                    ser.write(mensagem.encode())                        # Escreve na SerialPort "?\n" para receber as coordenadas
                    time.sleep(0.1)
                    ser.flushInput() 
                    mensagem="G01 " + "Z" + str(int(self.m*text_data_json['RoloTorce']+float(self.varPosicaoInic))) + " F" + str(1000) +"\n"
                    print(mensagem)
                    ser.write(mensagem.encode())                        # Escreve na SerialPort "?\n" para receber as coordenadas
                    time.sleep(0.1)                                     # Espera a resposta do arduino
                    ser.flushInput()
            '''

    
   