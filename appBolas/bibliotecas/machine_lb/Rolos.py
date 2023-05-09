#  Luís Dias @ 2023  #

'''
Classe estatica que guarda o estado atual dos ROLOS

!!  Esta classe não é para ser instanciada  !!

1º - A inicialização é feita após referenciação.
2º - As mudanças de velocidade acontecem sempre em relação ao valor anterior
3º - SettingsLB contem valor de aceleração, que é comum aos dois rolos
4º - Existe um bit de targetReached(estatic)

#Sempre que alterar uma variavel dentro de uma THREAD não esquercer bloquer para escrever#
'''

class controloRolos:
    velActRoloEsq=0
    velActRoloDir=0