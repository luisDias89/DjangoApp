#  Luís Dias @ 2022  #

'''
Este ficheiro contem as configurações da máquina na qual o software é instalado.
Devemos inserir no dicionario o valor maximo em mm do curso de navegação dos eixos, este valor
deve ser inferiores aos soft switch se ativado nas configurações GRBL de modo a não haver
um bloquei da maquina em RUNTIME.
Nos angulos devemos inserir qual o angulo minimo e maximo de cada eixo de modo 
a que o algoritmo consiga calcular qual o ponto 0 em milimetros, após o reset da máquina 
o software envia os motores para o angulo 0, que  o angulo de repouso
X-> É o eixo horizontal do lançador de bolas.
Y-> É o eixo vertival do lançador de bolas.
Z-> É o eixo de inclinação do lançador de bolas.
A-> motor que libera as bolas.
'''

import os
import json


# Recebe o path real deste script
dir_path = os.path.dirname(os.path.realpath(__file__))

# Lê o arquivo JSON
with open(dir_path + "/config.json", "r") as f:
    config = json.load(f)

class configLB:
    # Atualiza os dicionários e variáveis
    maximo = config["configs_lb"]["maximo"]
    angulo = config["configs_lb"]["angulo"]
    graus_desl_a = config["configs_lb"]["graus_desl_a"]
    velocidadeAvancoGate = config["configs_lb"]["velocidadeAvancoGate"]
    velocidadeZeroMaquina = config["configs_lb"]["velocidadeZeroMaquina"]
    print("A leer configurações do lançador de bolas:")

    @staticmethod
    # Usar para sincronizar configs !
    def sincronizar_dados():
        with open(dir_path + "/config.json", "r") as f:
            dados = json.load(f)
        configLB.maximo = dados["configs_lb"]["maximo"]
        configLB.angulo = dados["configs_lb"]["angulo"]
        configLB.graus_desl_a = dados["configs_lb"]["graus_desl_a"]
        configLB.velocidadeAvancoGate = dados["configs_lb"]["velocidadeAvancoGate"]
        configLB.velocidadeZeroMaquina = dados["configs_lb"]["velocidadeZeroMaquina"]
        print("Sincronismo de configuração")

    @staticmethod
    def get_configJSON():
        # Lê o arquivo JSON
        with open(dir_path + "/config.json", "r") as f:
            config = json.load(f)
        return config
    
    @staticmethod
    def set_configJSON(json_dict):
        # Escreve o arquivo JSON com o novo dicionário
        with open(dir_path + "/config.json", "w") as f:
            json.dump(json_dict, f)

