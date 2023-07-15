//*-------------------------------------------
//          @ Luís Dias 2022
// Funções genericas para controlo da página manual

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

var myModal = new bootstrap.Modal(document.getElementById('myModal'), {
    keyboard: false
  });                                                                       // Declaração do MODAL para inserir novo lance                    

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

var Joy1 = new JoyStick('joy1Div', {}, function (stickData) {
    //
    joy1InputPosX = stickData.xPosition;                    // Recebe a posição X do Joystick
    joy1InputPosY = stickData.yPosition;                    // Recebe a posição Y do JoyStick
    joy1Direcao = stickData.cardinalDirection;              // Recebe qual o sentido
    
    //rotação para alcançarX
    joy1X = bufferjoy1X = stickData.x;                       // Recebe o valor de rotação a alcançarde X      

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
        'RoloTorce': (rangeTorce.value),
    }))
    //RoloTorce.innerHTML=(rangeTorce.value-50) + "º";        // Atualiza o valor no HTML
}
//=========================================



//========================================================
// Envia um conjunto de informações por WebSocket em formato JSON
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
        novoValor = valor-1;buttonRoloDir
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

//==================================================================================
//         Função link ao botão de criar lance a partir de posições atuais 
//  Esta função lança um modal que captura as coordenadas atuais do lançador de bolas
//  e velocidade dos rolos, é possivel editar os valore tanto de posições como de vel motores
//  O modal deve ter uma zona para poder inserir o nome do lance
//  CAMPOS:
//  Nome do lance: ____________
//  Angulo em X: Valor numérico com duas casas decimáis
//  Angulo em Y: Valor numérico com duas casa decimais
//  Angulo de inclinação: valor numérico com duas casa decimais
//  Velocidade do rolo esquerdo: Numero inteiro de 0 a 100
//  Velocidade do rolo direito: Numero inteiro de 0 a 100 

    //-> recebo o objeto button do document
    function createDialogToNewLance() {
        
        document.getElementById('nomeLance').value = '';                                // Garante que sempre que abre o modal o valor do nome é limpo
      
        var inputAngleX = document.getElementById('anguloX');                           // Recebe o objeto campo de entrada do modal para anguloX
        var angleX = document.getElementById('id_inclina').innerText;                   // Recebe o valor atual do angulo que está fixo no FrontEND
        if (angleX.endsWith('º')) {                                                     // se o valor vier com um º
          inputAngleX.value = angleX.slice(0, -1);                                          // Entrao trunca o valor e atribui ao campo
        } else {                                                                        // Senao
          inputAngleX.value = angleX;                                                       // o valor é inserido diretamente
        }
      
        var inputAngleY = document.getElementById('anguloY');                           // Recebe o objeto campo de entrada do modal para anguloY 
        var angleY = document.getElementById('id_rotacao').innerText;                   // Recebe o valor atual do anguloY que está fixo no FrontENd
        if (angleY.endsWith('º')) {                                                     // se o valor vier com um º
          inputAngleY.value = angleY.slice(0, -1);                                          // Entrao trunca o valor e atribui ao campo
        } else {                                                                        // Senao
          inputAngleY.value = angleY;                                                        // o valor é inserido diretamente
        }
      
        var inputInclination = document.getElementById('anguloInclinacao');             // MESMA COISA...
        var inclination = document.getElementById('RoloTorce').innerText;
        if (inclination.endsWith('º')) {
          inputInclination.value = inclination.slice(0, -1);
        } else {
          inputInclination.value = inclination;
        }
      
        var inputSpeedLeft = document.getElementById('velocidadeRoloEsquerdo');         // MESMA COISA...
        var speedLeft = document.getElementById('roloesq').innerText;
        if (speedLeft.endsWith('%')) {
          inputSpeedLeft.value = speedLeft.slice(0, -1);
        } else {
          inputSpeedLeft.value = speedLeft;
        }
      
        var inputSpeedRight = document.getElementById('velocidadeRoloDireito');         // MESMA COISA...
        var speedRight = document.getElementById('rolodir').innerText;
        if (speedRight.endsWith('%')) {
          inputSpeedRight.value = speedRight.slice(0, -1);
        } else {
          inputSpeedRight.value = speedRight;
        }
      
        myModal.show();                                                                 // Finalmente mostra o modal depois de atualizar os campos
      }

      function btn_lancarBola() {
        // Envia uma chamada assincrona AJAX para inserir o lance na DB
        // O tipo de ação da chamada é atruibuido ao identificador, ver na função ajaxRequest quais os programados
        // Preparação da clase para lançar a bola a partir de AJAX
        //ajaxRequest({identificador: "LANCAR_BOLA"}); 
        var id_lbl_bolasLan = document.getElementById("id_lbl_bolasLan");
        var bolasLan = parseInt(id_lbl_bolasLan.innerHTML) + 1;
        id_lbl_bolasLan.innerHTML = bolasLan.toString();
        // Lança bola por comunicação Websocket
        chatSocket.send(JSON.stringify({
            'LANCAR_BOLA': (novoValor.toString()),
        }))
       }


      function salvarLance() {                                                          // Funcao executada ao clicar no botão salvarLance
        // obter os valores dos inputs
        var nomeLance = document.getElementById('nomeLance').value;                     
        var inputAngleX = document.getElementById('anguloX').value;
        var inputAngleY = document.getElementById('anguloY').value;
        var inputInclination = document.getElementById('anguloInclinacao').value;
        var inputSpeedLeft = document.getElementById('velocidadeRoloEsquerdo').value;
        var inputSpeedRight = document.getElementById('velocidadeRoloDireito').value;
        
                // Verificar se o campo está vazio
        if (nomeLance.trim() === '') {
            alert('O campo "Nome do lance" é obrigatório!');    // se o lance estiver vazio envia um alert
            return;                                             // e sai da função
        }

        // Constroi a informação para enviar ao BACKEND
        var data = {
            identificador: "NOVO_LANCE",                        // Este  o campo que define o que o BACK END vai fazer com esta informação!!!
            nomeLance: nomeLance,
            anguloX: inputAngleX,
            anguloY: inputAngleY,
            anguloInclinacao: inputInclination,
            velocidadeRoloEsq: inputSpeedLeft,
            velocidadeRoloDir: inputSpeedRight
        };
        
        // fechar o modal
        ajaxRequest(data);                                      // Envia uma chamada assincrona AJAX para inserir o lance na DB
        myModal.hide();                                         // Esconde o MODAL
      }

      


/* ============================================================================================
    Controlo feito pelo modo automatico começa aqui, script de concatenação de projetos */







