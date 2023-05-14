/*-------------------------------------------
          @ Luís Dias 2022
 O presente ficheiro implementa metodos para chamadas AJAX

-------------------------------------------*/

// https://docs.djangoproject.com/en/3.2/ref/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }


  // -----------------------------  CHAMADA ASSINCRONA COM INPUT DE FUNÇÃO --------------------------
  // Função geral para chamadas AJAX com ao backEND
  // Chamada assincrona AJAX somente com Javascript, (Implementaão para subtituir a biblioteca Jquery)
  // Funções programadas : 
  //  "NOVO_LANCE", 
  //  "LANCAR_BOLA", 
  //  "DOWNLOAD_JSON", 
  //  "UPLOAD_JSON",
  //  "REFERENCIAR_LANCADOR"
  //  "ASK-EIXOS-REF"

function ajaxRequest(data) {
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/ajax_request/');
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.onload = function() {
        if (xhr.status === 200) {
            var dataReceived = JSON.parse(xhr.responseText);
            //console.log(dataReceived)
            if(dataReceived.message!="OK")
            {
               if(dataReceived.message.hasOwnProperty("configs_lb"))          // se receber um objeto com configs_lb então inseres novo FORM JSON
               {
                cria_formularioJSON(dataReceived.message);                    // Chama uma função que vai inserir um novo formulário
               }
               else if(dataReceived.message=="REFERENCIADO")
               {
                  callback_referenciado();
               }
               else if(dataReceived.message=="N_REFERENCIADO")
               {
                  callback_n_referenciado();
               }
               else if(dataReceived.message=="refTRUE")
               {
                refTRUE();
               }
               else if(dataReceived.message=="refFALSE")
               {
                refFALSE();
               }
               else{
                callback(dataReceived);
               }
            }
        }
        else{
            var dataReceived = JSON.parse(xhr.responseText);
            callback(dataReceived);
        }
    };
    xhr.send(JSON.stringify(data));
}

function callback(data) {

    alert(data.message);
    
}
