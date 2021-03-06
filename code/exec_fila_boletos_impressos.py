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

def main():
    print('START OK!')
    #1 - CONECTA NO BD AUX E BUSCA MENSAGENS DA FILA PARA ENVIO
    b = bd_conecta.conecta_db_aux()
    mensagens = StayBox_funcoes.getFilaEnvio('5', b) #5 = aviso fim de impressão de boleto
    b.close()

    if mensagens != None: #TEM MENSAGENS PARA ENVIAR
      #2 - CONECTA NO BD POSTGRESS E BUSCA CREDENCIAIS PARA API
      result = SZChat_funcoes.getLogin(3)
      if result == None:
        logging.error('BOLETOS IMPRESSOS - main() - getLogin=NONE')
        sys.exit('BOLETOS IMPRESSOS- main() - getLogin=NONE')
        exit
      else:
        logging.debug('CREDENCIAIS SZCHAT OK')
        vApi = result[0]['api']
        vUsr = result[0]['usr']
        vUsr_Token = result[0]['usr_token']
        vPsw = result[0]['psw']
        vApiSend   = result[0]['api_send']
        vApiLogout = result[0]['api_logout']

        #3 - CONECTA NO BD AUX E BUSCA AS CONFIGURAÇÕES DE MENSAGEM
        result = SZChat_funcoes.getMensagemConfig(5) # CONFIGURACOES DE MENSAGEM DE AVISO DE FIM DE IMPRESSAO DE BOLETO
        if result == None:
          logging.error('FIM IMPRESSAO BOLETO - main() - getMensagem=NONE')
          sys.exit('FIM IMPRESSAO BOLETO - main() - getMensagem=NONE')
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
          logging.error('FIM IMPRESSAO BOLETO  - Não foi possível autenticar na API.')     
          sys.exit('FIM IMPRESSAO BOLETO  - Não foi possível autenticar na API.')
        else:
            jauth = auth.json()
            vTOKEN_APP = jauth['token']
            vATENDDANCE_ID = SZChat_funcoes.getAtenddanceID(5) #USA A EQUIPE DA NEGATIVAÇÃO
            logging.debug('FIM IMPRESSAO BOLETO  - ATENDDANCE_ID: ' + vATENDDANCE_ID)
            logging.debug('FIM IMPRESSAO BOLETO  - TOKEN_APP: ' + vTOKEN_APP)

        for m in  mensagens:
          if getIsTimeSend: #se está em horário comercial
            b = bd_conecta.conecta_db_aux()
            vCelular = m['celular']
            vMsgm = m['msgm']
            vContrato = m['contract_id']
            vCliente = m['client_id']
            vNome = m['nome']

            vAssunto = 'Aviso: Final Imp. Boletos - (' + str(vContrato) + ') ' + vNome 
            print(vAssunto)
            credenciais = {
                'platform_id': vCelular,
                'channel_id': '615c4aa0a0d3c7001208e518',
                'type': 'text',
                'message': vMsgm,
                'subject': vAssunto,
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
            StayBox_funcoes.setLogEnvio('5', m['contract_id'], m['client_id'], m['nome'], vCelular, str(send), m['frt_id'], b)

            #apaga da FILA
            StayBox_funcoes.dropFilaEnvioItem(m['id'], b)

            #atrasa o envio para não bloquear o número
            if vIntervalo_segundos > 0:
              b.close()
              rand = random.randint(vIntervalo_segundos, vIntervalo_segundos + 5)
              logging.debug('FIM IMPRESSAO BOLETO - SLEEP - ' + str(rand))
              print(rand)
              sleep(rand)
            else:
              logging.info('FIM IMPRESSAO BOLETO - Por favor, defina o campo de intervalo de mensagens na tabela de configuração')
              b.close()
              sys.exit('DEFINA O SLEEP NA CONFIGURAÇÃO DA MENSAGEM');                  
        
        SZChat_funcoes.fLogoutToken(vTOKEN_APP, vApiLogout)

if __name__ == '__main__':
  Log_Format = "%(levelname)s %(asctime)s - %(message)s"
  #Log_Level = logging.debug #logging.ERROR

  logging.basicConfig(filename = "logTT.log",
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.DEBUG,
                    encoding='utf-8')
  logging.info('START')
  main()