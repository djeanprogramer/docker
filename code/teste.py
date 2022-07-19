from flask import jsonify
import SZChat_funcoes
import SynSuite_funcoes
import json


string = """ 'access_token': b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGplYW5AdGNoZXR1cmJvLmNvbS5iciIsImV4cGlyZXMiOiIyMDIyLTA3LTIwVDEzOjI0OjUwLjA3MTE5NiJ9.-omYPOefwO7B-GxvsBrRn1ajKQcXFbmij_sdrnXbl9M' """
print(string)



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
