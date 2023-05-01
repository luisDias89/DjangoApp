/*-------------------------------------------
          @ Luís Dias 2022
 A seguinte função trata a comunicação
 necessária para que se dê inicio ao 
 treino, mensagens enviadas ao backend
 Parametros: 
 url: caminho da requisição
 id_treino: treino a ser executado
 ---------------------------------------------------------------------------
 tipoRequisição: "START" , "STOP" , "PAUSE" , "RESUME" , "GET_INFO"
 ---------------------------------------------------------------------------
 Notas:
 - O START e o STOP PAUSE E RESUME retornam "status": "ok" 
 - O "GET_INFO" retorna todos os valores necessários para atualizar o modal.
-------------------------------------------*/
function init_stop_Treino(url, id_treino, data_requisicao){
    return $.ajax({                                                   // Chamada Ajax
          url: url,                                                   // Qual o URL definido para a chamada desta tabela, está no html data-url
          type: "post",                                               // Metodo POST
          dataType: "json",                                           // Transmissão de DATA por JSON format
          data: JSON.stringify({
            "tipoRequisicao": data_requisicao, 
            "id_treino" : id_treino,
          }),               // Envio de uma mensagem com chave returnID-> ID(da linha BD)
          headers: {                                                  // Cabeçalhos
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": getCookie("csrftoken"),                   // Não esquecer de criar a função 'getCookie'
          },
          success: (data) => {
              jQuery.globalEval( "var mensagemResposta = true");
              mensagemResposta=true;
              //console.log("Mensagem da função init_stop_Treino() enviado com sucesso"); //debug
              
          },
          error: (error) => {
            
            jQuery.globalEval( "var mensagemResposta = false");
            console.log(error + " da função init_stop_Treino()");
            
          }
        }
      );
    }

/*========================================================================================
    Notas:
    - O START e o STOP PAUSE E RESUME retornam "status": "ok" 
    - O "GET_INFO" retorna todos os valores necessários para atualizar o modal.
==========================================================================================*/
function init_stop_lance(url, id_lance, data_requisicao){



  if( "cadencia" in data_requisicao){
    var cadencia=data_requisicao["cadencia"];
  }
  else{
    var cadencia=0;
  }
  if( "qt_bolas" in data_requisicao){
    var qt_bolas=data_requisicao["qt_bolas"];
  }
  else{
    var qt_bolas=0;
  }


  return $.ajax({                                                   // Chamada Ajax
    url: url,                                                   // Qual o URL definido para a chamada desta tabela, está no html data-url
    type: "post",                                               // Metodo POST
    dataType: "json",                                           // Transmissão de DATA por JSON format
    data: JSON.stringify({
      tipoRequisicao: data_requisicao["comando"], 
      id_lance : id_lance,
      cadencia_lance: cadencia,
      qtBolas: qt_bolas
    }),               // Envio de uma mensagem com chave returnID-> ID(da linha BD)
    headers: {                                                  // Cabeçalhos
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),                   // Não esquecer de criar a função 'getCookie'
    },
    success: (data) => {
        jQuery.globalEval( "var mensagemResposta = true");
        mensagemResposta=true;
        //console.log("Mensagem da função init_stop_Treino() enviado com sucesso"); //debug
        
    },
    error: (error) => {
      jQuery.globalEval( "var mensagemResposta = false");
      console.log(error + " dafunção init_stop_Treino()");
    }
  }
);


  /*
  var retorna ="Nada"
  
  fetch(url, {
    method: 'POST', // or 'PUT'
    headers: {                                                  // Cabeçalhos
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),                   // Não esquecer de criar a função 'getCookie'
    },
    body: JSON.stringify({
      "tipoRequisicao": tipoRequisicao, 
      "id_treino" : id_lance,
    }),
    })
    .then((response) => {response.json()})
    .then(function(data){                   // Transforma 
      //console.log('Success:', data);
      //console.log(data.status)
      
      retorna = data.status;
    })
    .catch(function(error) {
      console.error('Error:', error);
      retorna = error;
    });
    
    return retorna;
    */
  }
  
