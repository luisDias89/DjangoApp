//-------------- WebSocket --------------------------------

// Declaração dos caminhos e objetos WebSocket
let url = `ws://${window.location.host}/ws/socket-server/`;
const chatSocket = new WebSocket(url);

// Sempre que recebo uma mensagem do WebSocket é despoletado um evento que decide o que vai fazer com a informação recebida
chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    console.log('Data:', data);

    console.log(data);

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


// Função que testa se é numero e se não tem letras
function validaNumber(stringTeste, nNumeros){
    var valido = false;
    if(!(stringTeste.length > nNumeros) && !isNaN(stringTeste) )
    {
        if(parseInt(stringTeste)>0){
            valido=true
        }
    }
    return valido;
}


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



window.addEventListener('load',function(){                   // Se o documento estiver pronto, então executa os scripts
    
    var Present_id_treino=0;                    // variavel auxiliar de ciclo  
    $('#id_table').DataTable({

        paging: true,           // Paginação
        pageLenght: 10,         // Linhas por página
        lengthChange: false,    // Alterar tanhamos de visualização
        autoWidth: true,        // Width automatico
        searching: true,        // Seletor procurar
        bInfo: true,            // 
        bSort : true,
    });

    $('#id_table2').DataTable({

        paging: true,           // Paginação
        pageLenght: 10,         // Linhas por página
        lengthChange: false,    // Alterar tanhamos de visualização
        autoWidth: true,        // Width automatico
        searching: true,        // Seletor procurar
        bInfo: true,            // 
        bSort : true,
    });


    var ID_selected;                     // Nota este ID_selected foi adicionado para resolver o BUG do jquery que não recebe os novos valores dentro da data.
    var SG_ASK_TREINOorLANCE = "none"    // Quando alquem carrega na tabela, aqui fica guardado se é um treino ou lance que vai ser executado
    const myModal = new bootstrap.Modal('#myModal', { keyboard: false, backdrop: 'static' });           // Declaração global do modal
    const modalLance = new bootstrap.Modal('#modalLance', { keyboard: false, backdrop: 'static' });           // Declaração global do modal
    const modalTreino = new bootstrap.Modal('#modalTreino', { keyboard: false, backdrop: 'static' });           // Declaração global do modal
    //const modalTreino = new bootstrap.Modal('#modalTreino', { keyboard: false, backdrop: 'static' });            // Declaração global do modal
    
    var btn_FecharModal=$("#btn_fecharModal");
    var btn_closeSuperior=$("#btn_closeSuperior");
    var btn_FecharModal_js=document.getElementById("btn_fecharModal");
    var btn_PauseResume= document.getElementById('btn_PauseResume');
    var btn_closeSuperior_js=document.getElementById("btn_closeSuperior");
    let botaoInserirLances = document.getElementById('id_inserirLance');
    let botaoInserirTreino = document.getElementById('id_inserirTreino');
    var flag_sincronizaTreino=false;                                                // Variavel que o timer espera para iniciar a sincronização do treino na tela
    var flag_sincronizaLance=false;
    let treinoPausado = false;
    //Junção JavaScript para tratamento do botão de inicio de treino e inicio de lance
    

    // ======================== TRATAMENTO DO BOTÃO PAUSE/RESUME ============================

    btn_PauseResume.onclick = function()  {                                         // Quando o utilizador carrega na tecla PAUSE/RESUME
        if(SG_ASK_TREINOorLANCE=="TREINO")                                              // Primeiro verifica se é um treino
        {
            if (treinoPausado) {                                                            // e se for um treino, verifica se esta Pausado
                init_stop_Treino(url, ID_selected, "RESUME");                                   // se estiver pausado então envia informação ao Back end para andar
                treinoPausado = false;                                                          // Assinala novamente não esta pausado
                btn_PauseResume.textContent = "Pause";                                          // e troca o texto do botão para Pause
              } else {                                                                      // caso esteja em running o
                init_stop_Treino(url, ID_selected, "PAUSE");                                    // envia PAUSE ao back END
                treinoPausado = true;                                                           // assinala que esta em estado de PAUSE    
                btn_PauseResume.textContent = "Resume";                                         // e troca o nome do botão para Resume
              }    
        }

        if(SG_ASK_TREINOorLANCE=="LANCE")                                            // Primeiro verifica se é um Lance
        {   
            if (treinoPausado) {                                                        // e se for um Lance, verifica se esta Pausado
                init_stop_lance(url, ID_selected, {comando: "RESUME",});                    // se estiver pausado então envia informação ao Back end para andar
                treinoPausado = false;                                                      // Assinala novamente não esta pausado
                btn_PauseResume.textContent = "Pause";                                      // e troca o texto do botão para Pause
              } else {                                                                  // caso esteja em running o
                init_stop_lance(url, ID_selected, {comando: "PAUSE",});                     // envia PAUSE ao back END
                treinoPausado = true;                                                       // assinala que esta em estado de PAUSE      
                btn_PauseResume.textContent = "Resume";                                     // e troca o nome do botão para Resume
              } 
        }
      };
    
    document.getElementById('btn_iniciarTreino').onclick = function() 
    {
        let btn_widgetHTML = document.getElementById('btn_iniciarTreino');
        let data = btn_widgetHTML.getAttribute('data-tipo');
        let id_atual = btn_widgetHTML.getAttribute('data-id');                      // Recebe o ID da base de dados, que foi recebido na contrução da tabela
        let textoAtual = btn_widgetHTML.textContent;                                // Recebe o valor de texto do botão
        url=document.getElementById("id_table").getAttribute('data-url');           // vai à tabela buscar o URL inserido a partir do template DJANGO

        switch (textoAtual) {

            case 'Iniciar treino':
                var request = init_stop_Treino(url,id_atual,"START");       // Faz um request AJAX para iniciar o treino BACKEND
                request.done(function( ) {                                              // Se a comunicação for bem executada 
                    btn_widgetHTML.textContent = 'Parar treino'                         // então muda o botão e inicia o treino
                    btn_PauseResume.style.display = 'block';                            // Mostr o botão Pause/resume    
                    btn_FecharModal_js.classList.remove("active");      // inativa o botão Close
                    btn_FecharModal_js.classList.add("disabled");
                    btn_closeSuperior.removeClass("active").addClass("disabled");       // Desativa o botão X (close()
                    flag_sincronizaTreino=true; 
                    });
                    
                request.fail(function( jqXHR, textStatus ) {                            // Caso a ligação for mal sucedida, aborta e avisa
                    alert("Falha de comunicação com o controlador")
                });    
                break;

            case 'Parar treino':                                                    // se o texto do botão for Parar treino
                init_stop_Treino(url, id_atual,"STOP");                                 // entao envia mensagem ao brack end para fazer STOP ao treino
                btn_widgetHTML.textContent = 'Iniciar treino'                           // passo o texto do botão para "Iniciar treino" 
                btn_PauseResume.style.display = 'none';                                 // Esconde o botão toogle de Pause/resume
                btn_FecharModal_js.classList.remove("disabled");          // Ativa o botão close
                btn_FecharModal_js.classList.add("active");
                btn_closeSuperior.removeClass("disabled").addClass("active");           // o botão close superiorDireito passa ao estado de ativo
                flag_sincronizaTreino=false;
                break;

            case 'Iniciar lance':                               // Controlo do botão Iniciar lance(Javascript)
                let objcadencia=document.getElementById("seletor_cadencia");
                let cadencia_selecionada=String(objcadencia[objcadencia.selectedIndex].text);
                cadencia_selecionada=parseInt(cadencia_selecionada.replace(" Segundos", ""));
                qtBolas= document.getElementById("seletor_bolas").value;
                let bufferError="Por favor ";

                if(objcadencia.selectedIndex!=0 && validaNumber(qtBolas, 3)){
                    data_lances={
                        comando: "START",
                        cadencia: cadencia_selecionada,
                        qt_bolas: qtBolas
                    };

                    init_stop_lance(url,id_atual,data_lances);
                    btn_widgetHTML.textContent = 'Parar lance'
                    btn_FecharModal_js.classList.remove("active");
                    btn_FecharModal_js.classList.add("disabled");
                    document.getElementById('btn_PauseResume').style.display = 'block'; // Mostr o botão Pause/resume  
                    btn_closeSuperior.removeClass("active").addClass("disabled");     // Desativa o botão X (close()
                    flag_sincronizaLance=true;
                }
                else{
                    if((!objcadencia.selectedIndex!=0))
                        {
                            bufferError+="selecione a cadencia "
                        };
                    if((!objcadencia.selectedIndex!=0) && !validaNumber(qtBolas, 3)){
                        bufferError+="e ";
                    }
                    if(!validaNumber(qtBolas, 3))
                        {
                            bufferError+="insira a quantidade de bolas corretamente."
                        };
                    alert(bufferError);
                };
                    
                break;
            case 'Parar lance':                                                     // Controlo do botão Parar lance(Javascript)
                flag_sincronizaLance=false;
                init_stop_lance(url,id_atual,{comando: "STOP"});
                btn_widgetHTML.textContent = 'Iniciar lance'
                btn_FecharModal_js.classList.remove("disabled");
                btn_FecharModal_js.classList.add("active");
                btn_closeSuperior.removeClass("disabled").addClass("active");
                document.getElementById('btn_PauseResume').style.display = 'none'; // Mostr o botão Pause/resume 
                
                break;
            default:
                console.log(`Erro no botão inicio stop do treino/lance ${expr}.`);
        }
    };



    $('#tableLanceBody').children("tr").on('click', function(){

        ID_selected= $(this).children("th").text();                      // Recebe o ID do lance para poder utilizar globalmente
        SG_ASK_TREINOorLANCE="LANCE"

        $.ajax({                                                         // Chamada Ajax
            url: $("#id_table2").data('url'),                            // Qual o URL definido para a chamada desta tabela, está no html data-url
            type: "post",                                                // Metodo POST
            dataType: "json",                                            // Transmissão de DATA por JSON format
            data: JSON.stringify({idlance: $(this).data("id"),}),        // Envio de uma mensagem com chave returnID-> ID(da linha BD)
            headers: {                                                   // Cabeçalhos
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),                   // Não esquecer de criar a função 'getCookie'
            },
            success: (data) => {
                
                console.log("Envio ajax");              
                //alert(typeof(Nome_selected));
                
                var HTMLtitulo = $("#TituloModal");                     // Recebo o componente HTML 
                HTMLtitulo.empty();
                HTMLtitulo.append(`A executar o lance ${data["nomeLance"]}`);                // Insere o titulo do treino selecionado no modal
                
                let HTMLsubcabeçalho=$("#modelData_treino");
                HTMLsubcabeçalho.empty();
                HRcontrol=$("#HR");
                HRcontrol.empty();

                let HTMLlances=$("#modelData_Exec_treino");     // Lances, inserção da lista
                HTMLlances.empty();

                let HTMLinformacao=$("#InformacaoLabel");
                HTMLinformacao.html(`
                <h5 class="card-header" style="margin-bottom: 3px;">Informações do Lance:</h5>
                        <ul class="list-group list-group-horizontal" >
                            <li class="list-group-item " style="width: 50%;">
                                <h6 class="card-title lbBold" style="margin-bottom: 10px;">Coordenadas:</h6>
                                <h6>X: ${data["anguloX"]}<br></h6>
                                <h6>Y: ${data["anguloY"]}<br></h6>
                                <h6>Inclinação: ${data["anguloInclinacao"]}</h6>
                            </li>
                            <li class="list-group-item " style="width: 50%;">
                                <h6 class="card-title lbBold" style="margin-bottom: 10px;">Velocidade dos rolos:</h6>
                                <h6>Esquerdo: ${data["velocidadeRoloEsq"]}</h6>
                                <h6>Direito: ${data["velocidadeRoloDir"]}</h6>
                            </li> 
                        </ul>
                `);

                
                // Atualização da cadencia de treino no HTML
                let HTMLcandencia=$("#modelData_Cadencia");
                HTMLcandencia.html(`
                <h5 style="margin-bottom: 3px;">Cadencia de lançamento:</h5>

                <select class="form-select" id="seletor_cadencia" aria-label="Default select example">
                <option selected>Selecione a cadência de lançamento</option>
                <option value="1">2 Segundos</option>
                <option value="1">4 Segundos</option>
                <option value="1">6 Segundos</option>
                <option value="1">8 Segundos</option>
                <option value="1">10 Segundos</option>
                <option value="1">12 Segundos</option>
                <option value="1">14 Segundos</option>
                <option value="1">16 Segundos</option>
                <option value="1">18 Segundos</option>
                <option value="1">20 Segundos</option>
                </select>
                
                `);
                
                let HTMLtiposelecao=$("#modelData_Tiposelecao");
                HTMLtiposelecao.empty();
                let HTMLTempoRestanteTreino=$("#modelData_timeleft");
                HTMLTempoRestanteTreino.html(`

                    <div class="form-row align-items-center">
                        <div class="col-sm my-1">
                        <label class="sr-only" for="inlineFormInputName"><b>Quantas bolas pretende lançar? (max 999)</b></label>
                        <input type="text" class="form-control" id="seletor_bolas" placeholder="">
                        </div>
                    </div>
                    
                `)
                

                let HTMLbottomIDlance= $("#id_treino");
                HTMLbottomIDlance.html(`
                    <h6>Lance ${ID_selected} </h6>
                `);

                
                document.getElementById("btn_iniciarTreino").textContent="Iniciar lance"
                $("#btn_iniciarTreino").attr('data-tipo',"lance");   
                $("#btn_iniciarTreino").attr('data-id',$(this).data("id"));   
                Present_id_treino=$(this).data("id");
                

                myModal.show()
            },
            error: (error) => {
              console.log(error);
            }
          });

    });
    

    $('#tableTreinoBody').children("tr").on('click',                           // Se clicar na tabela em cima do seu filho TR, executa:
        function()
            {
                ID_selected= $(this).children("th").text();                     // Recebe o ID do treino para poder utilizar globalmente
                SG_ASK_TREINOorLANCE="TREINO"

                //Nome_selected=$(this).children("td").text();
                var lines = $('td', this).map(function(index, td){
                    return $(td).text();
                });
                
                //alert($(this).data("id")); Retorna o ID da linha da tabela.
                
                $.ajax({                                                        // Chamada Ajax
                    url: $("#id_table").data('url'),                            // Qual o URL definido para a chamada desta tabela, está no html data-url
                    type: "post",                                               // Metodo POST
                    dataType: "json",                                           // Transmissão de DATA por JSON format
                    data: JSON.stringify({id: $(this).data("id"),}),            // Envio de uma mensagem com chave returnID-> ID(da linha BD)
                    headers: {                                                  // Cabeçalhos
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken"),                   // Não esquecer de criar a função 'getCookie'
                    },

                    success: (data) => {
                        //console.log(data);// troubleshoting

                        // Titulo do modal atualizada para cada Treino
                        var HTMLtitulo = $("#TituloModal");             // Recebo o componente HTML 
                        HTMLtitulo.empty();
                        HTMLtitulo.append(data["tituloTreino"]);        // Insere o titulo do treino selecionado no modal
                        
                        let HTMLdataCriacao=$("#modelData_treino");
                        HTMLdataCriacao.empty();

                        var createdAt = new Date(data['dataCriacao'])
                        var months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro','Dezembro']
                        var formated = createdAt.getDate() + ' de ' + months[createdAt.getMonth()] + ' de ' + createdAt.getFullYear()
                        
                        HRcontrol=$("#HR");
                        HRcontrol.html("<hr>")
                        HTMLdataCriacao.append(`Inserido a: ` + formated );
                        

                        let HTMLinformacao=$("#InformacaoLabel");
                        HTMLinformacao.empty();
                        HTMLinformacao.append("Lista de lances a executar:");

                        // Tratamento do HTML do ID modal
                        const HTMLmodal = $("#id_treino");              // ID_treino footer
                        HTMLmodal.empty();                              

                        let HTMLlances=$("#modelData_Exec_treino");     // Lances, inserção da lista
                        HTMLlances.empty();
                        Object.entries(data.lances).map(item => {
                            HTMLlances.append( "<li>" + item[1]  + "</li>"  );
                        })

                        // Atualização da cadencia de treino no HTML
                        let HTMLcandencia=$("#modelData_Cadencia");
                        HTMLcandencia.empty();
                        var dictCadencia = ['Elevada', 'Alta', "Media", "Baixa"];
                        HTMLcandencia.append( "<strong>Cadencia de treino: </strong>" + dictCadencia[data["cadenciaTreino"]-1]);
                        
                        // Tempo de treino
                        let HTMLtempoDeTreino=$("#modelData_timeleft");
                        HTMLtempoDeTreino.empty();

                        let HTMLtiposelecao=$("#modelData_Tiposelecao");
                        HTMLtiposelecao.empty();
                        var dictSequencia=['Aleatória', 'Sequencial'];
                        var insertHTMLdict=dictSequencia[Number(data['sequenciaLances']) - 1 ];
                        HTMLtiposelecao.append( ` <b>Sequência de lances: </b> ${insertHTMLdict} ` );
                        
                             
                        var insertHTML= `Treino ` + data["statusID"] ;      //Footer id Treino
                        HTMLmodal.append(insertHTML);
                        // o botão fica com o id do treino para transmitir o id ao botão no onclick
                        //$("#btn_iniciarTreino").show()                              // Necessário porque no Modal lance, este é escondido
                        
                        
                        document.getElementById("btn_iniciarTreino").textContent="Iniciar treino"
                        $("#btn_iniciarTreino").attr('data-tipo',"treino"); 
                        $("#btn_iniciarTreino").attr('data-id',$(this).data("id"));   
                        Present_id_treino=$(this).data("id");
                        
                    },
                    error: (error) => {
                      console.log(error);
                    }
                  });

                for (let index = 0; index < lines.length; ++index) {
                   //alert(lines[index]);
                   i=1;
                }

                //alert(typeof(Nome_selected));
                myModal.show()
            }
    );

   
    botaoInserirLances.onclick = function() {
        // Lógica para lidar com o clique no botão de inserir lances
        modalLance.show()
        // Coloque aqui o código que você deseja executar quando o botão for clicado
    };

   
    botaoInserirTreino.onclick = function() {
        // Lógica para lidar com o clique no botão de inserir treino
        modalTreino.show()
        // Coloque aqui o código que você deseja executar quando o botão for clicado
    };


    //-------------- Timer para Relgio e GET_INFO ciclico--------------------------------
    setInterval(myTimer, 1000);
    
    function myTimer() {
        const d = new Date();
        document.getElementById("hora_atual").innerHTML = d.toLocaleTimeString();
        
        if(flag_sincronizaTreino)
        {
            var request = init_stop_Treino($("#id_table").data('url'),Present_id_treino,"GET_INFO");

            request.done(function( ) {                                                                          // Se a comunicação for bem executada então muda o botão e inicia o treino
                console.log(` TimeLeft do treino: ${request.responseJSON.timeLeft}`);
                console.log(` Percentagem para acabar o teino ${request.responseJSON.get_percentleft}%`);
                console.log(` Lance em execução ${request.responseJSON.get_Aexecutar}`);
                // Tempo de treino
                var HTMLtempoDeTreino=$("#modelData_timeleft");
                HTMLtempoDeTreino.html(
                    `<div id="amostrador">
                        <p id="lbl_tempoTreino"> <strong> Treino termina em: </strong> ${request.responseJSON.timeLeft} segundos</p>
                        <p id="lance-executando">A executar: ${request.responseJSON.get_Aexecutar}</p>
                        <div class="progress">
                        <span id="label_percentagem"> ${request.responseJSON.get_percentleft} % </span>
                        <br>
                        <div class="progress-bar" role="progressbar" style="width: ${request.responseJSON.get_percentleft}%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                     </div>
                    `
                );
                if( request.responseJSON.isStoped==true)
                    {
                        let btn_widgetHTML = document.getElementById('btn_iniciarTreino');
                        var btn_FecharModal_js=document.getElementById("btn_fecharModal");
                        var btn_closeSuperior_js=document.getElementById("btn_closeSuperior");
                        btn_widgetHTML.textContent = 'Iniciar treino'
                        btn_FecharModal_js.classList.remove("disabled");
                        btn_FecharModal_js.classList.add("active");
                        btn_closeSuperior_js.classList.remove("disabled");
                        btn_closeSuperior_js.classList.add("active");
                        treinoPausado = false;                                                           // assinala que esta em estado de PAUSE    
                        btn_PauseResume.textContent = "Pause";                                           // e troca o nome do botão para Resume
                        btn_PauseResume.style.display = 'none';                                          // Esconde o botão toogle de Pause/resume

                        flag_sincronizaTreino=false;
                    }
            
        });
            request.fail(function( jqXHR, textStatus ) {                        // Caso a ligação mal sucedida, aborta e avisa
                console.log("Falha de comunicação")
            });
        }
        else
        {   
            amostrador=$("#amostrador");
            amostrador.empty();
        };


        if(flag_sincronizaLance)
        {
                var request = init_stop_lance($("#id_table").data('url'),Present_id_treino,{comando:"GET_INFO_LANCE"});

                request.done(function( ) {                                                                          // Se a comunicação for bem executada então muda o botão e inicia o treino
                    // Tempo de treino
                    var HTMLprogressBar=$("#amostradorLance");
                    HTMLprogressBar.html(
                        `
                            <strong> Faltam lançar ${request.responseJSON.qtBolasLeft} bolas </strong>
                            
                            <div class="progress">
                                <br>
                                <div class="progress-bar" role="progressbar" style="width: ${request.responseJSON.get_percent}%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        `
                    );
                    if( request.responseJSON.isStoped==true)
                    {
                        let btn_widgetHTML = document.getElementById('btn_iniciarTreino');
                        var btn_FecharModal_js=document.getElementById("btn_fecharModal");
                        var btn_closeSuperior_js=document.getElementById("btn_closeSuperior");
                        btn_widgetHTML.textContent = 'Iniciar lance'
                        btn_FecharModal_js.classList.remove("disabled");
                        btn_FecharModal_js.classList.add("active");
                        btn_closeSuperior_js.classList.remove("disabled");
                        btn_PauseResume.style.display = 'none';                                          // Esconde o botão toogle de Pause/resume
                        btn_PauseResume.textContent = "Pause";                                           // e troca o nome do botão para Pause

                        flag_sincronizaLance=false;                                                      // Encerra a sincronização
                    }




            });
                request.fail(function( jqXHR, textStatus ) {                        // Caso a ligação mal sucedida, aborta e avisa
                    console.log("Falha de comunicação")

            });
        
        }else{
            var HTMLprogressBar=$("#amostradorLance");
            HTMLprogressBar.empty();
        };
    }
});

