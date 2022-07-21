from flask import jsonify
import bd_conecta
import requests
import json
import logging
from datetime import date, datetime
from models.model import WhTelecallSchema
from fastapi import HTTPException

def getLogEnvios(data_envio: str):
  #to_char(l.data_envio , 'DD/MM/YYYY') as data_envio ,
  sql = f"""select l.id ,
                  l.contract_id ,
                  l.client_id ,
                  l.mensagem_id ,                  
                  l.status ,
                  l.nome ,
                  l.celular ,
                  l.frt_id ,
                  TO_CHAR(l.data_envio, 'DD.MM.YY') as data_envio,
                  TO_CHAR(l.data_envio, 'HH24:MI') as hora_envio
            from szchat_log_envio l
            where TO_CHAR(l.data_envio, 'DDMMYYYY')  = '{data_envio}'
            ORDER BY l.data_envio desc """        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    b.commit()
    cursor.close()
    return rs
  except Exception as e:
    logging.error('StayBox_funcoes.py ' + str(e))
    logging.error(sql)
    raise HTTPException(status_code=400, detail="Data informada inválida. Utilize DDMMYYYY.")

def getLogPortabilidades():
  #A VIEW Retorna toda a fila do dia corrente.
  sql = f"""select * from vw_telecall_sac """        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    b.commit()
    cursor.close()
    if rs == None:
        return {"status_code": 404, "Mensagem": "Não encontrou resultados para a data informada."} 
    else:
        return rs
  except Exception as e:
    logging.error('StayBox_funcoes getLogPortabilidades' + str(e))
    logging.error(sql)
    return {"status_code": 402, "Mensagem": "Data informada inválida. Utilize DDMMYYYY."}

def getLogPortabilidadesErros():
  sql = f"""select * from vw_telecall_erros """        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    b.commit()
    cursor.close()
    if rs == None:
        return {"status_code": 404, "Mensagem": "Não encontrou resultados para a data informada."} 
    else:
        return rs
  except Exception as e:
    logging.error('StayBox_funcoes getLogPortabilidadesErros' + str(e))
    logging.error(sql)
    return {"status_code": 402, "Mensagem": "Data informada inválida. Utilize DDMMYYYY."}

def getCardCabecalho():
  #A VIEW Retorna os cards do dia corrente
  sql = f"""select * from vw_szchat_dash  """        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    b.commit()
    cursor.close()
    if rs == None:
        return {"status_code": 404, "Mensagem": "Não encontrou resultados para a data informada."} 
    else:
        return rs
  except Exception as e:
    logging.error('StayBox_funcoes.py ' + str(e))
    logging.error(sql)
    return {"status_code": 402, "Mensagem": "Não foi possível buscar as informações."}

def getCardCabecalhoTelecall():
  #A VIEW Retorna os cards do dia corrente
  sql = f"""select * from vw_telecall_dash  """        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    b.commit()
    cursor.close()
    if rs == None:
        return {"status_code": 404, "Mensagem": "Não encontrou resultados para a data informada."} 
    else:
        return rs
  except Exception as e:
    logging.error('StayBox_funcoes getCardCabecalhoTelecall ' + str(e))
    logging.error(sql)
    return {"status_code": 402, "Mensagem": "Não foi possível buscar as informações."}


def setFilaEnvio(vContratoID, vClienteID, vNome, vCelular, vStatus, vMsgm, vMsgmID, vFrtID: str, vBD, vData_Agendada = '' ):
  if vData_Agendada == '':
    data_atual = date.today()
    vData = data_atual.strftime('%Y-%m-%d')
  else:
    vData = datetime.strptime(vData_Agendada, '%d/%m/%Y').date()

  sql = f"""INSERT INTO szchat_fila_envio(
                contract_id, 
                client_id, 
                mensagem_id, 
                msgm, 
                data_fila, 
                status, 
                nome, 
                celular,
                frt_id, 
                data_agendada)
              VALUES ({vContratoID},
                      {vClienteID},
                      {vMsgmID},
                      '{vMsgm}', 
                      now(),
                      '{vStatus}',
                      '{vNome}',
                      '{vCelular}',
                      {vFrtID},
                      '{vData}');              
        """
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    return True
  except Exception as e:
    logging.error('STAYBOX - setAtivacoesDoDia() ' + str(e))
    logging.error(sql)
    print(str(e))
    return False

def getFilaEnvio(vMsgmID: str, vBD):
  sql = f"""SELECT f.* 
            FROM szchat_fila_envio f
            WHERE f.mensagem_id = {vMsgmID}
            ORDER BY f.data_fila """        
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    if rs == None:
        return None
    else:
        return rs
  except Exception as e:
    logging.error('StayBox_funcoes.py ' + str(e))
    logging.error(sql)
    print(str(e))
    return None

def getFilaEnvioPortabilidade(vBD):
  sql = f"""SELECT f.* 
            FROM szchat_fila_envio f
            WHERE f.mensagem_id = '8'
              and f.data_agendada = current_date + 1
            ORDER BY f.data_fila """        
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    if rs == None:
        return None
    else:
        return rs
  except Exception as e:
    logging.error('getFilaEnvioPortabilidade ' + str(e))
    logging.error(sql)
    print(str(e))
    return None

def dropFilaEnvioItem(vIDFila: str, vBD):
  sql = f"""delete from szchat_fila_envio f 
           where f.id = {vIDFila} """        
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    logging.debug('delete ok ID: %s', vIDFila )
    print('delete ok ID: %s', vIDFila )
    return True
  except Exception as e:
    logging.error('StayBox_funcoes.py DROP Fila' + str(e))
    logging.error(sql)
    print(str(e))
    return False

def setLogEnvio(vIdMsgm, vContratoID, vClienteID, vNome, vCelular, vStatus, vFrtID: str, vBD):
  sql = f"""INSERT INTO public.szchat_log_envio(
                contract_id, 
                client_id, 
                mensagem_id, 
                status,
                data_envio,
                nome,
                celular,
                frt_id)
              VALUES ({vContratoID},
                      {vClienteID},
                      '{vIdMsgm}', 
                      {vStatus},
                      now(),
                      '{vNome}',
                      '{vCelular}',
                      {vFrtID});              
        """
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    logging.debug('INSERIU REGISTROS. Contrato/Cliente:' + str(vContratoID) + '/' + str(vClienteID) )
    return True
  except Exception as e:
    logging.error('setLogEnvio() ' + str(e))
    logging.error(sql)
    return False

def setWebHookTelecall(vDados: WhTelecallSchema):
  sql = f"""INSERT INTO wh_telecall(
                "PORTABILITY",
                "STATUS",
                "NAME",
                "DOCUMENT_ID",
                "IS_LEGAL_ENTITY",
                "MSISDN",
                "REQUESTED_DATE",
                "SCHEDULED_DATE",
                "OPERATION_DATE",
                "MESSAGE")
              VALUES (
                '{vDados.PORTABILITY}',
                '{vDados.STATUS}',
                '{vDados.NAME}',
                '{vDados.DOCUMENT_ID}',
                '{vDados.IS_LEGAL_ENTITY}',
                '{vDados.MSISDN}',
                '{vDados.REQUESTED_DATE}',
                '{vDados.SCHEDULED_DATE}',
                '{vDados.OPERATION_DATE}',
                '{vDados.MESSAGE}'
              );              
        """
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    b.commit()
    cursor.close()
    return True
  except Exception as e:
    logging.error('setWhookTelecall() ' + str(e))
    logging.error(sql)
    return False

def getWebHookIDUsuaio(user: str):
  sql = f"""select 
            	wu.id 
            from wh_users wu 
            where wu.user = '{user}'
              and wu.active"""        
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchone()
    b.commit()
    cursor.close()
    if rs:
        return rs['id']
    else: 
        return 0
  except Exception as e:
    logging.error('StayBox_funcoes.py getWebHookIDUsuaio' + str(e))
    logging.error(sql)
    return {"status_code": 402, "Mensagem": "Valor informado inválido."}
