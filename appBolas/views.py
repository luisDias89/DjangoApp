from django.shortcuts import render
from django.http import HttpResponse
import time
from .models import SettingsGRBL
import json
from django.core import serializers
from multiprocessing import context
from .models import treino
from .models import lance as LanceDB
from django.http import HttpResponseBadRequest, JsonResponse        # Importação bibliotecas para async ajax, resposta em JSON
from django.views.decorators.csrf import requires_csrf_token
from . import metodos
engineLancadorBolas= metodos.engineTreino()


def modoauto(request):
    # request.is_ajax() is deprecated since django 3.1
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    

    if is_ajax:                                                                 # Se o metodo for ajax, então a resposta é em JSON
        if request.method=="GET":                                                # Se GET então
            todos = list(treino.objects.all().values())                          # Recebe os valores da base de dados
            return JsonResponse({'context': todos}, status=200)                  # Envia os valores por JSON, e retorna 200(ok)

        if request.method=="POST":                                              # Se o methodo for POST então
            dataFromPost=json.load(request)                                      # recebe os valores de POST
            
            # Caso a mensagem pretenda obter informações da tabela de treino   
            if "idlance" in dataFromPost:                                       # idlance, é só para lances
                dbLance = LanceDB.objects.get(id=dataFromPost["idlance"])  
                print("Lance " + str(dataFromPost["idlance"]))

                respostaJson={
                    'nomeLance': dbLance.nomeLance,
                    'anguloX': dbLance.anguloX,
                    'anguloY': dbLance.anguloY,
                    'anguloInclinacao': dbLance.anguloInclinacao,
                    'velocidadeRoloEsq': dbLance.velocidadeRoloEsq,
                    'velocidadeRoloDir': dbLance.velocidadeRoloDir,
                }
                return JsonResponse(respostaJson, status=200)

            # Para os treinos é só id
            if "id" in dataFromPost:                                                        # se houver um pedido com id na mensagem então
                dbTreino = treino.objects.get(id=dataFromPost["id"])                           #  vou ao models buscar toda a informacao do treino    
                serialized_q = serializers.serialize('json', dbTreino.lances.all())            #  e serializo para poder enviar por ajax para o front
                lancesJson={}                                                                  #  cria um Dicionario para guardar os lances iterados
                i=0                                                                            #  declara um indice auxiliar
                lances = dbTreino.lances.all()                                                 #  recebe os lances dentro de uma estrutura
                #for lance in lances:                                                           # itera a estrutura dos lances e 
                #    lancesJson.update({'lance'+ str(i): lance.nomeLance})                      # adiciona ao Dicionario
                #    i=i+1                                                                      # incrementa o iterador

                lancesJson = {'lance' + str(i): lance.nomeLance for i, lance in enumerate(dbTreino.lances.all())}
                print(lancesJson)

                respostaJson={
                    'statusID': dbTreino.id,
                    'lances' : lancesJson,
                    'tituloTreino': dbTreino.nomeTreino,
                    'dataCriacao' : dbTreino.dataCriacao,
                    'cadenciaTreino'   : dbTreino.cadenciaTreino,
                    'sequenciaLances'  : dbTreino.SequenciaLances,
                }
                return JsonResponse(respostaJson, status=200)



            # Caso a mensagem seja de iniciar treino, tem o tipoRequisicao no formulario    
            if "tipoRequisicao" in dataFromPost:
                if(dataFromPost["tipoRequisicao"]=="START"):            # Inicia o treino e envia o ID
                    
                    if "id_treino" in dataFromPost:
                        print("START TREINO")
                        engineLancadorBolas.start((dataFromPost["id_treino"]), tipo="treino")

                    if "id_lance" in dataFromPost:
                        dictLance= { "cadencia": dataFromPost["cadencia_lance"],
                                      "qtBolas": dataFromPost["qtBolas"]  }
                        engineLancadorBolas.start((dataFromPost["id_lance"]), tipo="lance", dataLance=dictLance  )
                        print("START LANCE")
                        pass
                    respostaJson={'status': "ok",}

                elif(dataFromPost["tipoRequisicao"]=="STOP"):           # Pará o treino e envia o ID de paragem
                    if "id_treino" in dataFromPost:
                        engineLancadorBolas.stop(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancadorBolas.stop(tipo="lance")
                        pass
                    respostaJson={'status': "ok",}

                elif(dataFromPost["tipoRequisicao"]=="RESUME"):
                    if "id_treino" in dataFromPost:
                        engineLancadorBolas.resume(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancadorBolas.resume(tipo="lance")
                        print("RESUME LANCE")
                        pass
                    respostaJson={'status': "run",}
                    
                elif(dataFromPost["tipoRequisicao"]=="PAUSE"):
                    if "id_treino" in dataFromPost:
                        engineLancadorBolas.pause(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancadorBolas.pause(tipo="lance")
                        print("PAUSE LANCE")
                        pass
                    respostaJson={'status': "pause",}
                    pass

                #======================================================
                #=  USADO PARA OBTER INFORMAÇÃO CICLICA DO FRONT END  =  
                # =====================================================
                elif((dataFromPost["tipoRequisicao"]=="GET_INFO")):
                    respostaJson={
                    'timeLeft': engineLancadorBolas.get_timeleft(tipo="treino"),
                    'get_percentleft' : engineLancadorBolas.get_percentleft(tipo="treino"),
                    }
                elif((dataFromPost["tipoRequisicao"]=="GET_INFO_LANCE")):
                    if(engineLancadorBolas.threadLance.runing==False):
                        engineLancadorBolas.threadLance.stop()
                    respostaJson={
                    'qtBolasLeft': engineLancadorBolas.get_bolasLancadasLeft(tipo="lance"),
                    'get_percent' : engineLancadorBolas.get_percentleft(tipo="lance"),
                    'isStoped'    : engineLancadorBolas.isStoped(tipo="lance")
                    }
            
                return JsonResponse(respostaJson, status=200)

        return JsonResponse({'status': 'Invalid request'}, status=400)

    else:                                       # else não é AJAX, e devolve a página.
        dbTreinos= treino.objects.all()
        dblances = LanceDB.objects.all()
        context={
            "treinos": dbTreinos,
            "lances":dblances,
        }
        return render(request, 'modoauto.html', context)
        # return render(request, "chat/index.html")



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
    if request.method =="GET":                                                  # Se receber o metodo GET então retorno a app index somente
        print(request.user)                                                     # Imprime o usuario que est a fazer a requisião de index na consola    
        
        if str(request.user) == 'AnonymousUser':                                # Se o usuario não estiver logado
            msgQuemEstaLogado='Utilizado nao logado'                            # Constroi uma mensagem que indica se está logado ou não            
        else:
            msgQuemEstaLogado= 'Utilizador logado'

        # Recebe a função declarada no forms.py
        # context é a estrutura que é enviada para o template python, que vai ser interpretado pelo render HTML
        context ={
            'curso': 'Engenharia de Automação Industrial 2019 - 2023',
            'mensagem':'O Luís Dias é o melhor engenheiro do planeta!',
            'logado': msgQuemEstaLogado,
            'showLogedIcons': request.user.is_authenticated,                    # Retorna um valor boleano para mostrar ou não o menu de settings
            #'SerialPort':SerialPort,
        }

        return render(request, 'index.html', context)                           # A função retorna uma página HTML com a renderização de index.html
    elif request.method =="POST":                                               # Somente para testes, retorna página HTML segundo parmetros de entrada POST
        postVAR = request.POST
        print(postVAR)


#Página onde é definidos as configurações do GRBL,os parâmetros podem ser adicionador progressivamente
def settingsReturn(request):
    #Passa um dicionario que contem a informação da base de dados sobre os SettingsGRBL
    context ={
            'SettingsGRBL': SettingsGRBL.objects.all(),         # passa uma query com todos os objetos contidos nesta tabela
        }
    return render(request, 'settings.html', context)


def contato(request):       
    return render(contato,'contato. ')

# Sempre que alguem entra na página de controlo do lançador de bolas, é redirecionado para esta página
def homepage(request):
    return render(request, 'homepage.html')
