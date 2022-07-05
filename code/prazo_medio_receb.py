import sys
import logging
import random
from time import sleep
import SZChat_funcoes
import SynSuite_funcoes
import bd_conecta
#import funcoes
import pyparsing
import time
import hora
from sqlescapy import sqlescape

def setPrazoMedioRecebimento(client_id, atraso_dias, qtd_bloqueio, serasa_spc, contract_id, client_name, data_inicio_contrato, saldo_devedor,valor_mensalidade, data_vencimento, data_pagamento: str, vBD):
  if atraso_dias == None:
    atraso_dias = 'NULL'

  if data_pagamento == None:
    sql = f"""INSERT INTO prazo_medio_recebimento(
            client_id, 
            qtd_bloqueio, 
            data_cad, 
            serasa_spc, 
            contract_id, 
            client_name, 
            data_inicio_contrato, 
            saldo_devedor,
            valor_mensalidade,
            data_vencimento,
            atraso_dias)
	       VALUES ({client_id}, 
                 {qtd_bloqueio}, 
                 now(), 
                 {serasa_spc}, 
                 {contract_id}, 
                 '{client_name}', 
                 '{data_inicio_contrato}', 
                 {saldo_devedor},
                 {valor_mensalidade},
                 '{data_vencimento}',
                 {atraso_dias});              
      """
  else:
    sql = f"""INSERT INTO prazo_medio_recebimento(
            client_id, 
            qtd_bloqueio, 
            data_cad, 
            serasa_spc, 
            contract_id, 
            client_name, 
            data_inicio_contrato, 
            saldo_devedor,
            valor_mensalidade,
            data_vencimento,
            data_pagamento,
            atraso_dias)
	       VALUES ({client_id}, 
                 {qtd_bloqueio}, 
                 now(), 
                 {serasa_spc}, 
                 {contract_id}, 
                 '{client_name}', 
                 '{data_inicio_contrato}', 
                 {saldo_devedor},
                 {valor_mensalidade},
                 '{data_vencimento}',
                 '{data_pagamento}',
                 {atraso_dias});              
      """
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    logging.debug('PRAZO MEDIO RECEBIMENTO -  INSERIU REGISTROS. Cliente/Contrato:' + str(client_id) + '/' + str(contract_id) )
    return True
  except Exception as e:
    vBD.rollback()
    logging.error(sql)
    logging.debug('ERRO: ' + str(client_id) + '/' + str(contract_id) )
    print(str(e))
    return False

def main():
  print('START')    
  retorno = SynSuite_funcoes.getPrazoMedioRecebimento()
  if retorno != None:
    b = bd_conecta.conecta_db_aux()
    #r['name'].encode('utf8')
    for r in retorno:
      setPrazoMedioRecebimento(r['client_id'],
                               r['vDias'],
                               r['qtd_bloqueios'],
                               r['spc'],
                               r['contract_id'],
                               sqlescape(r['name']),
                               r['beginning_date'],
                               r['vSaldo'],
                               r['vValor'],
                               r['expiration_date'],
                               r['vData_Pagamento'],
                               b)

      print('Inseriu: ' + str(r['client_id']))
    b.close()

if __name__ == '__main__':
  Log_Format = "%(levelname)s %(asctime)s - %(message)s"
  #Log_Level = logging.debug #logging.ERROR

  logging.basicConfig(filename = "logTT.log",
                    #filemode = "w",
                    format = Log_Format, 
                    #level = logging.DEBUG,
                    level = logging.INFO,
                    encoding='utf-8')

  logging.info('PROCESSAMENTO PRAZO MEDIO PAGAMENTO')
  
  print('PROCESSAMENTO PRAZO MEDIO PAGAMENTO - EXECUTANDO AGORA...')
  logging.info('PROCESSAMENTO PRAZO MEDIO PAGAMENTO - EXECUTANDO AGORA...')
  main()
  