from time import sleep
from flask import jsonify
import SZChat_funcoes
import SynSuite_funcoes
import StayBox_funcoes
import json
import bd_conecta
import Zenvia_funcoes

#import docker
#client = docker.from_env()
#client.containers.run('serviceszchat', environment=['script=exec_fila_aviso_bloqueio.py'] , detach=True, remove=True, name='EXEC_AvisoB')

#b = bd_conecta.conecta_db_aux()
#StayBox_funcoes.setFilaEnvio(10,10,'jean','55999083699','0','teste jean','8',0,b)
#b.close
#print('foi pra conta')
#retorno = getIsTimeSend
#print(retorno)
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

vTokenAPI = 'yBy1f97YFIb7P191X-ajJKRlsw9GU920GaNF'
res = SynSuite_funcoes.getSMS_Zenvia()
for r in res:
    vMsgSMS = f"TCHE TURBO: Sua fatura esta disponivel para pagamento! Vcto {r['vencimento']}, {r['valor']} Linha digitavel: {r['linha_digitavel']}"
    print(r['celular'])
    print(vMsgSMS)
    Zenvia_funcoes.fZenviaSendSMS(vTokenAPI, '', r['celular'] ,vMsgSMS)
    print('-------------------')
#Zenvia_funcoes.fZenviaSendSMS(vTokenAPI, '', '5555996515339',vMsgSMS)