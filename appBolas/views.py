from ast import Try
from django.shortcuts import render
from django.http import HttpResponse
import time
import serial

# Create your views here.

'''
ser = serial.Serial(
        port='/dev/ttyACM0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)
'''

def post(self,request):
    variavel = request.POST

def vel_mot_esq_aum(request):
    '''
    ser.write(b'G91')     # write a string
    
    try:
        nome=request.POST["subir"]
        mensagem="G00 X10  F500\n"
        ser.write(mensagem.encode())
        print("enviei ao motor a mensagem" + mensagem)
    except Exception as e:
        print("")
    try:
        nome=request.POST["descer"]
        mensagem="G00 X-10  F500\n"
        ser.write(mensagem.encode())
        print("enviei ao motor a mensagem" + mensagem)
    except Exception as e:
        print("")
    print("\n o nome é: " + nome )
    return render(request, 'index.html')
    '''


def index(request):
    if request.method =="GET":                                  # Se receber o metodo GET então retorno a app index somente
        print(request.user)
        '''
        ser.write(b'G91')     # write a string
        if ser.isOpen():
            SerialPort=("{} connected!".format(ser.port))
            mensagem="G00 X-10 Y10 Z10 F500\n"
            
            ser.write(mensagem.encode())
            time.sleep(0.05) #wait for arduino to answer
            if  ser.inWaiting()>0: 
                mensagemlida=ser.readline()
                SerialPort =mensagemlida.decode()
                print(SerialPort)
                ser.flushInput() #remove data after reading
        '''

        if str(request.user) == 'AnonymousUser':
            teste='usuario nao logado'
        else:
            teste= 'usuario logado'

                                # Recebe a função declarada no forms.py

        context ={
            'curso': 'Passei esta informação a partir dos views',
            'mensagem':'o django é muito bom',
            'logado': teste,
            #'SerialPort':SerialPort,
        }

        return render(request, 'index.html', context)
    elif request.method =="POST":
        postVAR= request.POST
        print(postVAR)




def contato(request):
    return render(contato,'contato.html')
