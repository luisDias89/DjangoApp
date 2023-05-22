
// ================  Botão Download config JSON  =======================================//
// Função para carregar configurações JSON do ficheiro através de chamada AJAX          //
// Após retorno é atualizado o FrontEnd com a criação de campos para alterar valores    //
// e liberação do botão upload                                                          //
function btn_downloaJsonConfigs()
{
    ajaxRequest({'identificador':'DOWNLOAD_JSON'});
}

// ================  Botão Upload config JSON  =========================================//
// Ao carregar Upload é feito uma requisição Ajax                                       //   
// com os dados do FrontEnd para atualizar o ficheiro                                   //
// e carregar novas configurações                                                       //
function btn_uploadJsonConfigs()
{   
    
    ajaxRequest({'identificador':'UPLOAD_JSON','config_JSON': reconstruirJsonConfigs()});
}

function reconstruirJsonConfigs() {
    const jsonConfig = {};
  
    // Percorre todos os elementos com a classe form-control
    const inputs = document.querySelectorAll('#form_container .form-control');
    inputs.forEach(input => {
      
      auxiliarVAR= input.id.split('#TYPE#');                   // Começa por dividir para saber qual é o tipo de variavel
      const tipo = auxiliarVAR[1]; 
      auxiliarVAR_sub = auxiliarVAR[0].split("#SUB#");
      const sub = auxiliarVAR_sub[1];
      const grupo = auxiliarVAR_sub[0];
      
      // Cria o grupo pai de todos
      if (!jsonConfig["configs_lb"]) {
         jsonConfig["configs_lb"] = {};
      }
      if (!sub) {                                                                           // Se não houver subgrupo
        jsonConfig["configs_lb"][grupo] = (tipo === 'str' ? input.value : parseInt(input.value));             // então atribui string ou value dpendedo do tipo
      } else {  // Se houver subgrupo                                                       // Senão
        if (!jsonConfig["configs_lb"][grupo]) {                                                              // se ainda não existir o grupo, cria-o         
            jsonConfig["configs_lb"][grupo] = {};
        }                                                                                      // se ja existir só adiciona mais items  lista
        jsonConfig["configs_lb"][grupo][sub] = tipo === 'str' ? input.value : parseInt(input.value);         // e atribui string ou value dependedo do tipo
      }
    });
  
    return jsonConfig;
  }

// ============== CRIA FORMULARIO JSON ATRAVÉS DO CALBACK AJAX =========================//
// A FUNCAO RECEBE AS CONFIGS JSON DO BACK END                                          //   
// E CRIA UM FORMULARIO DINAMICO EM TEMPO DE EXECUÇÃO                                   //
// LIBERA O BOTAO UPLOAD JSON                                                           //
function cria_formularioJSON(config_json) {

    
    const formContainer = document.getElementById("form_container");            // Obtem o FORMULÁRIO para um objeto javascript.
    formContainer.innerHTML = "";                                               // Força a limpeza de qualquer lixo contido dentro do FORM


    // Percorre todos os grupos dentro do objeto JSON
    Object.keys(config_json["configs_lb"]).forEach((grupo) => {                 // para cada grupo dentro do Objeto JSON executa:
        const grupoObj = config_json["configs_lb"][grupo];                          // Cria um novo objeto

        // ====== CRIA O CABEÇALHO DE CADA GRUPO ==============
        // Cria um elemento fieldset para cada grupo
        const fieldset = document.createElement("fieldset");                      // Cada grupo contem um elemento container pai de todo do tipo fieldset
        fieldset.className = "text-primary col-sd m-4 rounded";                   // Que é da classe 
        // Cria uma div para inserir os filhos do cabeçalho
        const legend = document.createElement("div");                             // Cria uma div que inserir a legenda do cabeçalho
        legend.textContent = grupo;                                               // Atruibui o nome que vem do JSON ao texto do cabeçalho                                        
        legend.className = "bg-light text-primary col-md-5 p-2 mx-auto text-center rounded";  // Atribui alguns estilos para ficar bonito
        fieldset.appendChild(legend);                                             // e adiciona a legenda ao container do Grupo

        // Cria um elemento div com classe row para agrupar as form-group
        const divRow = document.createElement("div");
        divRow.classList.add("row", "d-flex", "justify-content-center"); // adiciona as classes d-flex e justify-content-center para centralizar os itens


        //====== COMEÇA A ANALISAR OS CAMPOS DO GRUPO PARA SABER SE OS VAIS ITERAR OU São CAMPOS DIRETOS
        if (typeof grupoObj === "string") {                                     // SE FOR UM CAMPO STRING ENTÃO            
            // Cria um elemento input para o valor da chave                 
            const divFormGroup = document.createElement("div");
            divFormGroup.classList.add("form-group", "col-md-3", "mt-3");
            const input = document.createElement("input");
            input.classList.add("form-control");
            input.type = "text";
            input.name = grupo;
            input.value = grupoObj;
            // Adiciona o id ao input
            input.id = `${grupo}#TYPE#${"str"}`;                                // Identificação para reconstrução do form em JSON  


            // Adiciona o label e o input ao form-group
            divFormGroup.appendChild(input);

            // Adiciona o form-group ao divRow
            divRow.appendChild(divFormGroup);
        } 
        else if(Object.keys(grupoObj).length === 0){                    // SE FOR UM CAMPO COM ZERO FILHOS  
             // Cria um elemento input para o valor da chave
             const divFormGroup = document.createElement("div");
             divFormGroup.classList.add("form-group", "col-md-3", "mt-3");
             const input = document.createElement("input");
             input.classList.add("form-control");
             input.type = "text";
             input.name = grupo;
             input.value = grupoObj;
             input.id = `${grupo}#TYPE#${"value"}`;                     // Identificação para reconstrução do form em JSON 

             // Adiciona o label e o input ao form-group
             divFormGroup.appendChild(input);

             // Adiciona o form-group ao divRow
             divRow.appendChild(divFormGroup);   
        }
        else{     // Senão é um grupo que contem subgrupos e tem que ser pecorrido por um for
            
            Object.keys(grupoObj).forEach((mensagem) => {         // Percorre todas as mensagens dentro do grupo
                const valor = grupoObj[mensagem];   

                // Cria um elemento input para cada mensagem
                const divFormGroup = document.createElement("div");
                divFormGroup.classList.add("form-group", "col-md-3");
                const label = document.createElement("label");
                label.classList.add("col-form-label");
                label.textContent = mensagem;
                const input = document.createElement("input");
                input.classList.add("form-control");
                input.type = "text";
                input.name = mensagem;
                input.value = valor;

                // Adiciona o label e o input ao form-group
                divFormGroup.appendChild(label);
                divFormGroup.appendChild(input);

                // Adiciona o form-group ao divRow
                divRow.appendChild(divFormGroup);
                input.id = `${grupo}#SUB#${mensagem}#TYPE#${"value"}`;        // Identificação para reconstrução do form em JSON 
            });

    
        }

        // Adiciona o divRow ao fieldset
        fieldset.appendChild(divRow);

        // Adiciona o fieldset ao formulário
        formContainer.appendChild(fieldset);
    });
    
    // Libera o botão UPLOAD JSON
    document.getElementById("btn_UPLOAD_JSON").removeAttribute("disabled");


}


// Função para gerar IDs únicos
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
}
  