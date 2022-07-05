import logging
from pydoc import doc
import SZChat_funcoes
import StayBox_funcoes 
import SynSuite_funcoes
import bd_conecta
from hora import getIsTimeSend
import sys
import random
from time import sleep
from datetime import datetime

def sendWhatsappWebhook():
    #1 - CONECTA NO BD AUX E BUSCA MENSAGENS DA FILA PARA ENVIO
    b = bd_conecta.conecta_db_aux()
    mensagens = StayBox_funcoes.getFilaEnvio('4', b) #1 = cobrança
    b.close()

    if mensagens != None: #TEM MENSAGENS PARA ENVIAR
      #2 - CONECTA NO BD POSTGRESS E BUSCA CREDENCIAIS PARA API
      result = SZChat_funcoes.getLogin(3) #API NEGATIVADOS
      if result == None:
        logging.error('AVISO NEGATIVAÇAO - main() - getLogin=NONE')
        sys.exit('AVISO NEGATIVAÇAO - main() - getLogin=NONE')
        exit
      else:
        #ogging.debug('CREDENCIAIS SZCHAT OK')
        vApi = result[0]['api']
        vUsr = result[0]['usr']
        vUsr_Token = result[0]['usr_token']
        vPsw = result[0]['psw']
        vApiSend   = result[0]['api_send']
        vApiLogout = result[0]['api_logout']

        #3 - CONECTA NO BD AUX E BUSCA AS CONFIGURAÇÕES DE MENSAGEM
        result = SZChat_funcoes.getMensagemConfig(4)
        if result == None:
          logging.error('AVISO NEGATIVAÇAO - main() - getMensagem=NONE')
          sys.exit('AVISO NEGATIVAÇAO - main() - getMensagem=NONE')
        else:
          logging.debug('MENSAGENS SZCHAT OK')
          vId_equipe = result[0]['id_equipe']
          vChanel_id = result[0]['chanel_id']
          vClosed_session = result[0]['closed_session']
          vIntervalo_segundos = result[0]['intervalo_segundos']
          vDescricao = result[0]['descricao']
          print(vDescricao, vId_equipe, vChanel_id, vClosed_session, vIntervalo_segundos)

        #4 - CONECTA NA API E BUSCA TOKEN
        print('API: %s', vApi)
        print('USR: %s', vUsr)
        auth = SZChat_funcoes.fAutenticar(vApi, vUsr, vPsw)
        if auth.status_code != 200:
          logging.error('AVISO NEGATIVAÇAO - Não foi possível autenticar na API.')     
          sys.exit('AVISO NEGATIVAÇAO - Não foi possível autenticar na API.')
        else:
            jauth = auth.json()
            vTOKEN_APP = jauth['token']
            vATENDDANCE_ID = SZChat_funcoes.getAtenddanceID(5) #COBRANÇA
            logging.debug('COBRANÇA - ATENDDANCE_ID: ' + vATENDDANCE_ID)
            logging.debug('COBRANÇA - TOKEN_APP: ' + vTOKEN_APP)

        for m in  mensagens:
          if getIsTimeSend: #se está em horário comercial
            b = bd_conecta.conecta_db_aux()
            vCelular = m['celular']
            vMsgm = m['msgm']

            vAss = 'Negativação - ' +  m['nome']
            credenciais = {
                'platform_id': vCelular,
                'channel_id': '615c4aa0a0d3c7001208e518',
                'type': 'text',
                'message': vMsgm,
                'subject': vAss,
                'token': vUsr_Token,
                'agent' : vUsr,
                'attendance_id': vATENDDANCE_ID,
                'close_session': str(vClosed_session)
            }

            send = SZChat_funcoes.fEnviaWhatsapp(credenciais, vTOKEN_APP, vApiSend)
            if send == 200:
              logging.info('Código de Status: 200. '+ str(vCelular) )
            else:
              logging.info('Código de Status: ' + str(send) + '. ' + str(vCelular) )
            
            #depois de disparar no szchat, grava o registro no bdaux
            StayBox_funcoes.setLogEnvio('4', m['contract_id'], m['client_id'], m['nome'], vCelular, str(send), 0, b)

            #apaga da FILA
            StayBox_funcoes.dropFilaEnvioItem(m['id'], b)

            #atrasa o envio para não bloquear o número
            if vIntervalo_segundos > 0:
              b.close()
              rand = random.randint(vIntervalo_segundos, vIntervalo_segundos + 5)
              logging.debug('COBRANÇA - SLEEP - ' + str(rand))
              print(rand)
              sleep(rand)
            else:
              logging.info('COBRANÇA - Por favor, defina o campo de intervalo de mensagens na tabela de configuração')
              b.close()
              sys.exit('DEFINA O SLEEP NA CONFIGURAÇÃO DA MENSAGEM');                  
        
        SZChat_funcoes.fLogoutToken(vTOKEN_APP, vApiLogout)
