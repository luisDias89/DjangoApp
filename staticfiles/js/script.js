
//-------------- Relogio --------------------------------
setInterval(myTimer, 1000);

function myTimer() {
  const d = new Date();
  document.getElementById("hora_atual").innerHTML = d.toLocaleTimeString();
}

//-------------- WebSocket --------------------------------


// Declaração dos caminhos e objetos WebSocket
let url = `ws://${window.location.host}/ws/socket-server/`;
const chatSocket = new WebSocket(url);

// ------------------ Joystick ----------------------------------
var joy1InputPosX;
var joy1InputPosY;
var joy1Direcao;
var joy1X;
var joy1Y;

var btn_rolo_esq_subir=document.getElementById("btn_rolesq_subir");         // Link para os objeto html a partir do ID, botão dos rolos
var btn_rolo_esq_desc=document.getElementById("btn_rolesq_descer");         // Link para o projeto html a partir do ID
var btn_rolo_dir_subir=document.getElementById("btn_roldir_subir");         // Link para os objeto html a partir do ID
var btn_rolo_dir_desc=document.getElementById("btn_roldir_descer");         // Link para o projeto html a partir do ID

var txt_rolo_esq_subir=document.getElementById("roloesq");                  // Recebe o texto que fica em cima da imagem para o atulizar
var txt_rolo_dir_subir=document.getElementById("rolodir");                  // Recebe o texto que fica em cima da imagem para o atulizar
var txt_inclina=document.getElementById('id_inclina');                      // Y 
var rangeTorce=document.getElementById('id_inclinador');                    // Objeto !Slider inclinador, para receber o valor
var RoloTorce=document.getElementById('RoloTorce');                         // Recebe o objeto Texto, Z(do GRBL)
var txt_rotacao=document.getElementById('id_rotacao');                      // X


// Sempre que recebo uma mensagem do WebSocket é despoletado um evento que decide o que vai fazer com a informação recebida
chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    //console.log('Data:', data);

    if('X' in data)
    {
        txt_rotacao.innerHTML=data['X'];
    }
    if('Y' in data)
    {
        txt_inclina.innerHTML=data['Y']
    }
    if('Z' in data)
    {
        RoloTorce.innerHTML=data['Z']
    }
    if('rolEsq' in data)
    {
        txt_rolo_esq_subir.innerHTML=data['rolEsq']+ "%";
    }
    if('rolDir' in data)
    {
        txt_rolo_dir_subir.innerHTML=data['rolDir']+ "%";
    }
}



//Inicializar variaveis Globais
var novoValor=0;
var novoValorInclina=0;
var novoValorRotacao=0;
var bufferjoy1Y=0;
var bufferjoy1X=0;

//########################JOYSTICK###################################
// 
// 
// 

//setInterval(funcIterador, 200); 
/*                                               // Intervalo de 200 ms entre cada ciclo
let bufferValorY=0;
let bufferValorX=0;

function funcIterador() {
    if((bufferValorY-bufferjoy1Y)!=0){                                                              // Se ouver uma alteração no joystick
        bufferValorY=parseInt(bufferjoy1Y);                                                         // guarda o valor anterior
        var valor = parseInt(txt_inclina.textContent.slice(0, txt_inclina.textContent.length-1));   // Recebe o valor atual(não necessario agora)
        novoValorInclina=parseInt(bufferjoy1Y);                                                     // novoValor igual ao valor atual do Joystick
        if (novoValorInclina>100){                                                                  // Caso seja maior que 100 então é 100, (Prevent BUG JS)
            novoValorInclina=100;
        }
        //txt_inclina.textContent = novoValorInclina.toString()+"º";                                  // Constroi a mensagem e envia para a tela.
        
    }              // se a valor for diferente de 0 ou a diferença entre a atual e o ultimo for dif de zero executa

    if((bufferValorX-bufferjoy1X)!=0){
        bufferValorX=parseInt(bufferjoy1X);
        var valor = parseInt(txt_rotacao.textContent.slice(0, txt_rotacao.textContent.length-1));
        novoValorRotacao=parseInt(bufferjoy1X);
        if (novoValorRotacao>100){
            novoValorRotacao=100;
        }
        //txt_rotacao.textContent = novoValorRotacao.toString()+"º";
        // se a valor for diferente de 0 ou a diferença entre a atual e o ultimo for dif de zero executa
    }
}
*/

var Joy1 = new JoyStick('joy1Div', {}, function (stickData) {
    //
    joy1InputPosX = stickData.xPosition;                    // Recebe a posição X do Joystick
    joy1InputPosY = stickData.yPosition;                    // Recebe a posição Y do JoyStick
    joy1Direcao = stickData.cardinalDirection;              // Recebe qual o sentido
    
    //rotação para alcançarX
    joy1X = bufferjoy1X = stickData.x;

    //Inclinação
    joy1Y = bufferjoy1Y = stickData.y;                       //Atualiza a TextBox com o valor atual do Joystick      
    
    // Envia a mensagem de comando para Back End
    chatSocket.send(JSON.stringify({
        'deslHorizontal': joy1X,
        'deslVertical':joy1Y,
    }))
});

//============================================
//====== Controlador de eventos do rangeTorce, SLIDE
// Quando o controlador do movimento rongeTorce muda de avlor envia a mensagem por WebSocket
rangeTorce.onchange=()=>
{
    chatSocket.send(JSON.stringify({
        'RoloTorce': (rangeTorce.value-50),
    }))
    //RoloTorce.innerHTML=(rangeTorce.value-50) + "º";        // Atualiza o valor no HTML
}
//=========================================



//========================================================
// Envia um conjunto de informações por WebSocket via JSON
function sendWebSocket(){
    chatSocket.send(JSON.stringify({
        'xPosition': joy1InputPosX,
        'yPosition': joy1InputPosY,
        'deslHorizontal': joy1X,
        'deslVertical':joy1Y,
        'joy1Direcao':joy1Direcao,
        'rol_esq_value': novoValor,
    }))
}

//________________________________________________________

//##########################################################################
// Função onclick para subir o valor da velocidade do motor do rolo direito
// esta função recebe o valor atual que se encontra no HTML processa e envia
// para o máquina qual o valor da velocidade do rolo pretendida
btn_rolo_dir_subir.onclick = function(){
    //console.log("Subir velocidade rolo");
    var tamnho = txt_rolo_dir_subir.textContent.length;
    var valor = parseInt(txt_rolo_dir_subir.textContent.slice(0, tamnho-1));

    if(valor<100){
        novoValor= valor+1;
        //txt_rolo_dir_subir.textContent = novoValor.toString()+ "%";

        chatSocket.send(JSON.stringify({
            'comando_rolo_dir': (novoValor.toString()),
        }))

    }else
    {
        novoValor= "100"
        //txt_rolo_dir_subir.textContent= "100%";

    }
    
}
//##########################################################################
// Função onclick para descer o valor da velocidade do motor do rolo direito
// esta função recebe o valor atual que se encontra no HTML processa e envia
// para o máquina qual o valor da velocidade do rolo pretendida
btn_rolo_dir_desc.onclick= function(){
    //console.log("Descer velocidade rolo direito");
    var tamnho = txt_rolo_dir_subir.textContent.length;
    var valor = parseInt(txt_rolo_dir_subir.textContent.slice(0, tamnho-1));
    if(valor>0){
        novoValor = valor-1;
        //txt_rolo_dir_subir.textContent= novoValor.toString()+ "%";
        chatSocket.send(JSON.stringify({
            'comando_rolo_dir': (novoValor.toString()),
        }))
    }else
    {
        novoValor= "0"
        //txt_rolo_dir_subir.textContent= "0%";

    }
}


//##########################################################################
// Função onclick para subir o valor da velocidade do motor do rolo esquerdo
// esta função recebe o valor atual que se encontra no HTML processa e envia
// para o máquina qual o valor da velocidade do rolo pretendida
btn_rolo_esq_subir.onclick = function(){
    //console.log("Subir velocidade rolo");
    var tamnho = txt_rolo_esq_subir.textContent.length;
    var valor = parseInt(txt_rolo_esq_subir.textContent.slice(0, tamnho-1));

    if(valor<100){
        novoValor= valor+1;
        //txt_rolo_esq_subir.textContent = novoValor.toString()+ "%";

        chatSocket.send(JSON.stringify({
            'comando_rolo_esq': (novoValor.toString()),
        }))

    }else
    {
        novoValor= "100"
        //txt_rolo_esq_subir.textContent= "100%";

    }
    
}
//##########################################################################
// Função onclick para descer o valor da velocidade do motor do rolo esquerdo
// esta função recebe o valor atual que se encontra no HTML processa e envia
// para o máquina qual o valor da velocidade do rolo pretendida
btn_rolo_esq_desc.onclick= function(){
    //console.log("Descer velocidade rolo");
    var tamnho = txt_rolo_esq_subir.textContent.length;
    var valor = parseInt(txt_rolo_esq_subir.textContent.slice(0, tamnho-1));
    if(valor>0){
        novoValor = valor-1;
        //txt_rolo_esq_subir.textContent= novoValor.toString()+ "%";
        chatSocket.send(JSON.stringify({
            'comando_rolo_esq': (novoValor.toString()),
        }))
    }else
    {
        novoValor= "0"
        //txt_rolo_esq_subir.textContent= "0%";

    }
}
//========================================================
// Recebe os dados do input, com a velocidade inserida, e envia 
// por websocket, atualiza no html, testa o valor inserido
// e apresenta uma mensagem se não for um numero de 0 a 100
    //-> recebo o objeto button do document
    var btn_Atribui_VelRoloEsq=document.getElementById("buttonRoloEsq");        // Btn Atribuir que fica ao lado das caixas de texto de entrada
    var btn_Atribui_VelRoloDir=document.getElementById("buttonRoloDir");        // Btn Atribuir que fica ao lado das caixas de texto de entrada
    //-> recebo o objeto input do document
    var input_valorRoloEsq=document.getElementById("inputValorID_rolEsq");      // Caixas de texto input
    var input_valorRoloDir=document.getElementById("inputValorID_rolDir");      // Caixas de texto input
    var newValor="0";
    //-> Evento onClick para processar a informação
    btn_Atribui_VelRoloEsq.onclick= ()=>
    {   
        newValor=input_valorRoloEsq.value;

        if(validaNumber(newValor,3))
        {
            newValor=Math.abs(newValor);                                            // Elimina valores negativos
            newValor > 100 ? newValor=100 : newValor=newValor                       // Se for maior que 100 define 100
            //txt_rolo_esq_subir.innerHTML = newValor.toString()+ "%";
            chatSocket.send(JSON.stringify({
                'comando_rolo_esq': (newValor.toString()),
            }))
        }
        else{ console.log("Não é um numero ou tem mais de 3 algarismos: " + newValor);}
    }

    btn_Atribui_VelRoloDir.onclick= ()=>
    {   
        newValor=input_valorRoloDir.value;

        if(validaNumber(newValor,3))
        {
            newValor=Math.abs(newValor);                                            // Elimina valores negativos
            newValor > 100 ? newValor=100 : newValor=newValor                       // Se for maior que 100 define 100
            chatSocket.send(JSON.stringify({
                'comando_rolo_dir': (newValor.toString()),
            }))
        }
        else{ console.log("Não é um numero ou tem mais de 3 algarismos: " + newValor);}
    }
//========================================================


// Função teste se é numero e se não tem letras
function validaNumber(stringTeste, nNumeros){
    var valido = false;
    if(!(stringTeste.length > nNumeros) && !isNaN(stringTeste))
    {
        valido=true
    }
    return valido;
}


// Linhas de codigo não utilizadas, exemplos uteis
/*

// Já tinha resolvido o problema, uso apen o onChange
var atualiza=false;
//
rangeTorce.onmousedown = ()=>{                              // Sempre que o mouse vai a baixo atualiza uma vez
    RoloTorce.innerHTML=(rangeTorce.value-50) + "º";        // Atualiza o valor no HTML
    atualiza=true;                                          // Abilita a atualizaçãodo valor no mousemove
}

rangeTorce.onmousemove = ()=>{                              // Sempre que o rato de move o valor é atualizado
    if(atualiza){
        RoloTorce.innerHTML=(rangeTorce.value-50) + "º"; 
    }
}

rangeTorce.onmouseup = ()=>{                                // Quando é libertado o mouse desabilita  atualização

    atualiza=false;
}
 */







