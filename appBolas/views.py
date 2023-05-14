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
from .metodos import engineLancador
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .bibliotecas.machine_lb import configLB                        

@csrf_exempt
def modoauto(request):
    # request.is_ajax() is deprecated since django 3.1
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    

    if is_ajax:                                                                 # Se o metodo for ajax, então a resposta é em JSON
        if request.method=="GET":                                                # Se GET então
            todos = list(treino.objects.all().values())                             # Recebe os valores da base de dados
            return JsonResponse({'context': todos}, status=200)                     # Envia os valores por JSON, e retorna 200(ok)

        if request.method=="POST":                                              # Se o methodo for POST então
            dataFromPost=json.load(request)                                         # recebe os valores de POST
            
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
                        engineLancador.start((dataFromPost["id_treino"]), tipo="treino")

                    if "id_lance" in dataFromPost:
                        dictLance= { "cadencia": dataFromPost["cadencia_lance"],
                                      "qtBolas": dataFromPost["qtBolas"]  }
                        engineLancador.start((dataFromPost["id_lance"]), tipo="lance", dataLance=dictLance  )
                        print("START LANCE")
                        pass
                    respostaJson={'status': "ok",}

                elif(dataFromPost["tipoRequisicao"]=="STOP"):           # Pará o treino e envia o ID de paragem
                    if "id_treino" in dataFromPost:
                        engineLancador.stop(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancador.stop(tipo="lance")
                        pass
                    respostaJson={'status': "ok",}

                elif(dataFromPost["tipoRequisicao"]=="RESUME"):
                    if "id_treino" in dataFromPost:
                        engineLancador.resume(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancador.resume(tipo="lance")
                        print("RESUME LANCE")
                        pass
                    respostaJson={'status': "run",}
                    
                elif(dataFromPost["tipoRequisicao"]=="PAUSE"):
                    if "id_treino" in dataFromPost:
                        engineLancador.pause(tipo="treino")
                    if "id_lance" in dataFromPost:
                        engineLancador.pause(tipo="lance")
                        print("PAUSE LANCE")
                        pass
                    respostaJson={'status': "pause",}
                    pass

                #======================================================
                #=  USADO PARA OBTER INFORMAÇÃO CICLICA DO FRONT END  =  
                # =====================================================
                elif((dataFromPost["tipoRequisicao"]=="GET_INFO")):                             #  se a requisição for para infor do treino
                    respostaJson={                                                              #  responde com
                    'timeLeft': engineLancador.get_timeleft(tipo="treino"),                #  tempo restante do treino
                    'get_percentleft' : engineLancador.get_percentleft(tipo="treino"),     #  percentagem que falta para acabar o treino
                    'get_Aexecutar' : engineLancador.get_Aexecutar(),              #  Qual o lance que está a ser executado
                    'isStoped'    : engineLancador.isStoped(tipo="treino")
                    }
                elif((dataFromPost["tipoRequisicao"]=="GET_INFO_LANCE")):
                    if(engineLancador.threadLance.runing==False):
                        engineLancador.threadLance.stop()
                    respostaJson={
                    'qtBolasLeft': engineLancador.get_bolasLancadasLeft(tipo="lance"),
                    'get_percent' : engineLancador.get_percentleft(tipo="lance"),
                    'isStoped'    : engineLancador.isStoped(tipo="lance")
                    }
                else:                                                                           # Caso nenhuma opção seja válida
                    return JsonResponse({'status': 'Invalid request'}, status=400)              # responde com Invalid request

            
                return JsonResponse(respostaJson, status=200)

        return JsonResponse({'status': 'Invalid request'}, status=400)

    else:                                       # else não é AJAX, e devolve a página.

        if str(request.user) == 'AnonymousUser':                                # Se o usuario não estiver logado
            msgQuemEstaLogado='Utilizador não logado'                            # Constroi uma mensagem que indica se está logado ou não            
        else:
            msgQuemEstaLogado= 'Utilizador logado' 


        dbTreinos= treino.objects.all()
        dblances = LanceDB.objects.all()
        context={
            "treinos": dbTreinos,
            "lances":dblances,
            'logado': msgQuemEstaLogado,
            'showLogedIcons': request.user.is_authenticated,                    # Retorna um valor boleano para mostrar ou não o menu de settings
        }
        return render(request, 'modoauto.html', context)
        # return render(request, "chat/index.html")



def post(self,request):
    variavel = request.POST



def index(request):
    if request.method =="GET":                                                  # Se receber o metodo GET então retorno a app index somente
        #print(request.user)                                                    # Imprime o usuario que est a fazer a requisião de index na consola    
        
        if str(request.user) == 'AnonymousUser':                                # Se o usuario não estiver logado
            msgQuemEstaLogado='Utilizador não logado'                            # Constroi uma mensagem que indica se está logado ou não            
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
        


#Página onde é definidos as configurações do GRBL,os parâmetros podem ser adicionador progressivamente
@login_required
def settingsReturn(request):
    #Passa um dicionario que contem a informação da base de dados sobre os SettingsGRBL
    if str(request.user) == 'AnonymousUser':                                # Se o usuario não estiver logado
            msgQuemEstaLogado='Utilizador não logado'                            # Constroi uma mensagem que indica se está logado ou não            
    else:
        msgQuemEstaLogado= 'Utilizador logado' 
    context ={
            'logado': msgQuemEstaLogado,
            'SettingsGRBL': SettingsGRBL.objects.all(),         # passa uma query com todos os objetos contidos nesta tabela
        }
    return render(request, 'settings.html', context)


def contato(request):       
    return render(contato,'contato. ')


# Sempre que alguem entra na página de controlo do lançador de bolas, é redirecionado para esta página
def homepage(request):
    if str(request.user) == 'AnonymousUser':                                # Se o usuario não estiver logado
            msgQuemEstaLogado='Utilizador não logado'                            # Constroi uma mensagem que indica se está logado ou não            
    else:
        msgQuemEstaLogado= 'Utilizador logado' 

    context={
        'logado': msgQuemEstaLogado,
        'showLogedIcons': request.user.is_authenticated,                    # Retorna um valor boleano para mostrar ou não o menu de settings
    }
    return render(request, 'homepage.html', context)


#@login_required
@csrf_exempt
def ajaxRequest(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Se não for ajax então retorna um erro ao front end que não é uma chamada AJAX
    if not is_ajax:
        return HttpResponseBadRequest('This is not an AJAX request')

    # Caso contrario é uma chama Ajax e Verifica se é POST ou GET
    if request.method == 'POST':                                                # Se for POST, verifica os dados passados
        
        try:
            data = json.loads(request.body)
            #==============================================
            #================ NOVO_LANCE ==================
            #==============================================
            if data["identificador"] == "NOVO_LANCE":                           # Se novo lance
                nomeLance = data["nomeLance"]
                anguloX = data["anguloX"]
                anguloY = data["anguloY"]
                anguloInclinacao = data["anguloInclinacao"]
                velocidadeRoloEsq = data["velocidadeRoloEsq"]
                velocidadeRoloDir = data["velocidadeRoloDir"]
                
                # código para salvar os dados na base de dados
                
                if nomeLance and anguloX and anguloY and anguloInclinacao and velocidadeRoloEsq and velocidadeRoloDir:
                    lance = LanceDB.objects.create(nomeLance=nomeLance, anguloX=anguloX, anguloY=anguloY,
                                                    anguloInclinacao=anguloInclinacao, velocidadeRoloEsq=velocidadeRoloEsq,
                                                    velocidadeRoloDir=velocidadeRoloDir)
                    response_data = {
                        'message': 'Lance salvo com sucesso!'
                    }
                    status_code = 200  # OK
                else:
                    response_data = {
                        'message': 'Erro ao salvar o lance. Preencha todos os campos!'
                    }
                    status_code = 400  # Bad Request

            #==============================================
            #================ LANCAR_BOLA =================
            #==============================================
            elif data["identificador"] == "LANCAR_BOLA":                       # Se pedido para lançar bola
                engineLancador.MM_lancar_bola()

                response_data = {
                        'message': 'OK'
                }
                status_code = 200  

            #==============================================
            #=========== DOWNLOAD_JSON TO FE ==============
            #==============================================
            elif data["identificador"] == "DOWNLOAD_JSON":
                config = configLB.get_configJSON()
                response_data = {
                        'message': config
                }
                status_code = 200
            
            #==============================================
            #============ UPLOAD_JSON TO FILE =============
            #==============================================
            elif data["identificador"] == "UPLOAD_JSON":
                configLB.set_configJSON(data["config_JSON"])
                configLB.sincronizar_dados()
                
                response_data = {
                        'message': 'OK'
                }
                status_code = 200
            
            #==============================================
            #=========== REFERENCIAR_LANCADOR =============
            #==============================================
            elif data["identificador"] == "REFERENCIAR_LANCADOR":
                resposta = engineLancador.Ref_lancador()
                if(resposta==True):
                    resposta="REFERENCIADO"
                else:
                    resposta="N_REFERENCIADO"
                response_data = {
                        'message': resposta
                }
                status_code = 200
            #==============================================
            #=========== ASK-EIXOS-REFERENCIADOS =============
            #==============================================    
            elif data["identificador"] == "ASK-EIXOS-REF":
                resposta = engineLancador.getInfo_eixos_ref()
                if(resposta==True):
                    resposta="refTRUE"
                else:
                    resposta="refFALSE"
                response_data = {
                        'message': resposta
                }
                status_code = 200

                
            
            #==============================================
            #========== SE NÃO EXISTIR A FUNCAO ===========
            #==============================================
            else:
                response_data = {
                    'message': 'Identificador inválido!'
                }
                status_code = 400  # Bad Request

        except json.JSONDecodeError:
            response_data = {
                'message': 'Dados inválidos. JSON inválido!'
            }
            status_code = 400  # Bad Request
            
    elif request.method == 'GET':
        response_data = {
            'name': 'Luis Dias 2023',
            'age': 34
        }
        status_code = 200  # OK
    else:
        response_data = {
            'message': 'Método inválido!'
        }
        status_code = 400  # Bad Request    
    return JsonResponse(response_data, status=status_code)

