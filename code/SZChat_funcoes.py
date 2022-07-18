import logging
#from site import venv
import bd_conecta
import requests
import phonenumbers

def getLogin(vID_USUARIO: str):
  sql = f""" SELECT 
                a.id,
                a.versao,
                a.api,
                a.api_send,
                a.api_logout,
                a.usr,
                a.usr_token,
                PGP_SYM_DECRYPT(psw::bytea, '2cb7feda13b9692affad130d4d6b4b93') as psw
            FROM szchat_autenticacao a
            WHERE a.id = {vID_USUARIO};       
        """
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    logging.debug('BD AUX: DESCONECTOU')
    return rs
  except Exception as e:
    logging.error('SZCHAT_FUNCOES - getLogin() ' + str(e))
    return 

def getAtenddanceID(vID_EQUIPE: str):
  sql = f""" select
                e.atenddance_id
              from szchat_equipes e
              where e.id = {vID_EQUIPE};  """
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()

    if rs != None:
      return  rs[0]['atenddance_id']
    else:
      return None
  except Exception as e:
    logging.error('SZCHAT_FUNCOES - getAtenddanceID() ' + str(e))
    return 

def getMensagemConfig(vID_MENSAGEM: str):
  sql = f""" SELECT 
               id, 
               id_equipe, 
               chanel_id, 
               closed_session, 
               intervalo_segundos, 
               msgm, 
               descricao, 
               horario_envio               
             FROM szchat_mensagens
             WHERE id = {vID_MENSAGEM};       
        """
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    logging.debug('BD AUX: DESCONECTOU')
    return rs
  except Exception as e:
    logging.error('SZCHAT_FUNCOES - getMensagemConfig() ' + str(e))
    return 

def fAutenticar(vApi: str, vEmail, vSenha):
    try:
        parametros = {
                     'email': str(vEmail),
                     'password': str(vSenha)
        }        
        
        #print(parametros)

        autenticacao = requests.post(vApi, params=parametros)
        return autenticacao
    except:
        logging.error('SZChat_funcoes - fAutenticar - except')
        return -1

def fEnviaWhatsapp(vCredenciais, vToken, vApi):
    try:
        my_headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + vToken,
        }
        print(vCredenciais)
        whatsapp = requests.post(vApi, headers=my_headers, data=vCredenciais)
        print(whatsapp.json())
        return whatsapp.status_code
    except:
        logging.error('SZChat_funcoes - fEnviaWhatsapp - except')
        return 0

def fNumeroCelularValido(pCelular: str):
    try:
        if int(pCelular[4]) >= 6 and int(pCelular[2]) <= 9:
            return pCelular
        else:
            return ''
    except:
        return ''


def fgetCelular(pCelular, pTelefone: str):
    try:
        vPhone = phonenumbers.parse(str(pTelefone), 'BR')
    except:
        vPhone = ''

    try:
        vCell_Phone = phonenumbers.parse(str(pCelular), 'BR')
    except:
        vCell_Phone = ''

    if vPhone != '':
        vPhone = phonenumbers.format_number(vPhone,
                                            phonenumbers.PhoneNumberFormat.E164)
        vPhone = vPhone.replace('+', '')
        vPhone = fNumeroCelularValido(vPhone)

    if vCell_Phone != '':
        vCell_Phone = phonenumbers.format_number(vCell_Phone,
                                                    phonenumbers.PhoneNumberFormat.E164)
        vCell_Phone = vCell_Phone.replace('+', '')
        vCell_Phone = fNumeroCelularValido(vCell_Phone)

    #Sempre prioriza enviar para o celular, e caso não seja válido, tenta o telefone
    if vCell_Phone  != '':
        return  vCell_Phone 
    elif vPhone != '':
        return vPhone
    else:
        return ''  

def fLogoutToken(vToken, vApi):
    try:
        my_headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + vToken,
        }
        #logout = requests.get('https://tcheturbo.sz.chat/api/v4/auth/logout',  headers=my_headers )
        logout = requests.get(vApi,  headers=my_headers )
        if logout.status_code == 200:
            logging.debug('SZCHAT_Funcoes - fLogoutToken - código de Status: ' + str(logout.status_code))
            result = True
        else:
            logging.debug('SZCHAT_Funcoes - fLogoutToken - Código de Status: ' + str(logout.status_code))
            result = False
    except:
        logging.error('SZCHAT_funcoes - fLogoutToken - EXCEPT')
        result = False

    return result

def getContratosNaoEnviar(vMsgID: str):
  sql = f""" SELECT 
                n.contract_id
            FROM szchat_nao_enviar n
            WHERE n.mensagens_id = {vMsgID}
            ORDER BY n.contract_id
        """
  try:
    b = bd_conecta.conecta_db_aux()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()

    vContratos = ''
    for n in rs:
        if vContratos == '':
            vContratos = str(n['contract_id'] )
        else:
            vContratos = vContratos + ',' + str(n['contract_id'])
    
    cursor.close()
    b.close()
    logging.debug('BD AUX: DESCONECTOU')
    return vContratos
  except Exception as e:
    logging.error('SZCHAT_FUNCOES - getLogin() ' + str(e))
    return 
