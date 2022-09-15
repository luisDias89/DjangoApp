from ast import Try
from django.shortcuts import render
from django.http import HttpResponse
import time
import serial

from .models import SettingsGRBL

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
        
        if str(request.user) == 'AnonymousUser':
            teste='usuario nao logado'
        else:
            teste= 'usuario logado'

                                # Recebe a função declarada no forms.py

        context ={
            'curso': 'Passei esta informação a partir dos views',
            'mensagem':'o django é muito bom',
            'logado': teste,
            'showLogedIcons': request.user.is_authenticated,
            #'SerialPort':SerialPort,
        }

        return render(request, 'index.html', context)
    elif request.method =="POST":
        postVAR= request.POST
        print(postVAR)


def settingsReturn(request):
    #Passa um dicionario que contem a informação da base de dados sobre os SettingsGRBL
    context ={
            'SettingsGRBL': SettingsGRBL.objects.all(),         # passa uma query com todos os objetos contidos nesta tabela
        }
    return render(request, 'settings.html', context)


def contato(request):
    return render(contato,'contato.html')
