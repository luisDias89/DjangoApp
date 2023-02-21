#  Luís Dias @ 2022  #
'''
Este ficheiro contem as configurações da máquina na qual o software é instalado.
Devemos inserir no dicionario o maximo em mm do curso de navegação dos eixos, este valor
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

maximo = {"X": 25,
          "Y": 25,
          "Z": 25,
          "A": 15.5
         }

angulo = {
    "min_X": -45,
    "max_X": 45,
    "min_Y": -3,
    "max_Y": 20,
    "min_Z": -20,
    "max_Z": 18,
    "min_A": 0,
    "max_A": 90,
}

graus_desl_a={                  # Angulo de inicio de fim da porta do lançador de bolas
    "retemBola": 10,
    "lancaBola": 45
}

velocidadeAvancoGate="5000"   # em mm/min    # Velocidade de avanço da porta de bolas, nota que tambem é imposto pelas definições do GRBL

velocidadeZeroMaquina=3000

def soma(a,b):
    return a+b