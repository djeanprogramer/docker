from flask import jsonify
import SZChat_funcoes
import SynSuite_funcoes
import StayBox_funcoes
import json
import bd_conecta
from hora import getIsTimeSend


#b = bd_conecta.conecta_db_aux()
#StayBox_funcoes.setFilaEnvio(10,10,'jean','55999083699','0','teste jean','8',0,b)
#b.close
#print('foi pra conta')

retorno = getIsTimeSend
print(retorno)

#rs = SynSuite_funcoes.getAtivacoesDoDiaMovel()
#for i in rs:
#    lista = json.loads(str(i['final_checklist']))
#    portabilidade = None
#    data_portabilidade = None
#    hora_portabilidade = None
#    celular_portabilidade = None
#
#    if lista != None:
#        for campo in lista:
#            print(lista[campo]['label'])
#
#            if lista[campo]['label'] == 'PORTABILIDADE':
#                portabilidade = lista[campo]['value']
#            elif lista[campo]['label'] == 'DATA AGENDADA':
#                data_portabilidade = lista[campo]['value']
#            elif lista[campo]['label'] == 'HORA AGENDADA':
#                hora_portabilidade = lista[campo]['value']
#            elif lista[campo]['label'] == 'CELULAR':
#                celular_portabilidade = lista[campo]['value']
#
#            print(portabilidade)
#            print(data_portabilidade)
