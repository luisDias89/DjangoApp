// Declaração dos caminhos e objetos WebSocket
let url = `ws://${window.location.host}/ws/socket-server/`;
const chatSocket = new WebSocket(url);


// Obter elementos por id do formulario stepPulse
var stepPulseValue=document.getElementById("stepPulseValue");
var stepPulseInput=document.getElementById("stepPulseInput");
var stepPulsebtn=document.getElementById("stepPulsebtn");
var botaoSlider1=document.getElementById("botaoSlider1");




// ----- Sempre o GRBL envia uma linha com valores reconhece qual o linha e atribui na interface gráfica ----------
chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    //Nos settings recebo um mensagem com o comando que foi passado e a resposta do GRBL, o seguinte switch case vai
    //interpretar qual o comando e fazer a respectiva atribuição do valor.
    if('DoComandoGRBL' in data)
    {
        switch(data['DoComandoGRBL']) {
            case "$0":
                stepPulseValue.innerHTML="Valor atual: " + String(data['resposta']);
              break;
            case y:
              // code block
              break;
            default:
              // code block
          }
    }
}


stepPulsebtn.onclick= ()=>
{
    {% for comando in SettingsGRBL %}

    console.log("{{comando}}")

    {% endfor %}
    newValue = stepPulseInput.value;
    if(validaNumber(newValue, 10))
    {
        set_settings_GRBL('$0', newValue);
    }
}

//Sempre que o user carregue no enviar comando para receber o valor atual.
botaoSlider1.onclick = ()=>
{
    enviaComando_toGRBL('$0');
}



// ----------------  Funções Globais -------------------------------------
// Função teste se é numero e se não tem letras
function validaNumber(stringTeste, nNumeros){
    var valido = false;
    if((stringTeste.length < nNumeros) && !isNaN(stringTeste))
    {
        valido=true
    }
    return valido;
}

function enviaComando_toGRBL(comandoEnviar)
{
        chatSocket.send(JSON.stringify({
            'enviaComando_toGRBL': comandoEnviar,
        }))
        
    
    return 10;
} 

function set_settings_GRBL(comandoEnviar, newValue)
{
        chatSocket.send(JSON.stringify({
            'enviaComando_toGRBL': comandoEnviar,
            'newValue' : newValue,
        }))
    return 10;
}