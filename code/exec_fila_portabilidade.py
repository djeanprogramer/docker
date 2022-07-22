#ESSA FILA É EXECUTADA ATRAVÉS DO CRONTAB, as 9hs, 14hs e 16hs
import logging
from pydoc import doc
import SZChat_funcoes
import StayBox_funcoes 
import bd_conecta
import sys
import random
from time import sleep
from datetime import datetime

def main():
    print('START OK!')
    #1 - CONECTA NO BD AUX E BUSCA MENSAGENS DA FILA PARA ENVIO
    b = bd_conecta.conecta_db_aux()
    mensagens = StayBox_funcoes.getFilaEnvioPortabilidade(b) 
    b.close()

    if mensagens != None: #TEM MENSAGENS PARA ENVIAR
      #2 - CONECTA NO BD POSTGRESS E BUSCA CREDENCIAIS PARA API
      result = SZChat_funcoes.getLogin(6) #API PORTABILIDADE
      if result == None:
        logging.error('AVISO PORTABILIDADE - main() - getLogin=NONE')
        sys.exit('AVISO PORTABILIDADE - main() - getLogin=NONE')
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
        result = SZChat_funcoes.getMensagemConfig(8)
        if result == None:
          logging.error('AVISO PORTABILIDADE  - main() - getMensagem=NONE')
          sys.exit('AVISO PORTABILIDADE - main() - getMensagem=NONE')
        else:
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
          logging.error('AVISO PORTABILIDADE - Não foi possível autenticar na API.')     
          sys.exit('AVISO PORTABILIDADE - Não foi possível autenticar na API.')
        else:
            jauth = auth.json()
            vTOKEN_APP = jauth['token']
            vATENDDANCE_ID = SZChat_funcoes.getAtenddanceID(4) #BOAS VINDAS

        for m in mensagens:
          if datetime.now().weekday() != 7:
            b = bd_conecta.conecta_db_aux()
            vCelular = m['celular']
            #vCelular = '5555996515339'
            vMsgm = m['msgm']

            vAss = 'PORTABILIDADE - ' +  m['nome']
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
              logging.debug('Código de Status: 200. '+ str(vCelular) )
            else:
              logging.debug('Código de Status: ' + str(send) + '. ' + str(vCelular) )
            
            #depois de disparar no szchat, grava o registro no bdaux
            StayBox_funcoes.setLogEnvio('8', m['contract_id'], m['client_id'], m['nome'], vCelular, str(send), 0, b)

            #apaga da FILA
            StayBox_funcoes.dropFilaEnvioItem(m['id'], b)

            #atrasa o envio para não bloquear o número
            if vIntervalo_segundos > 0:
              b.close()
              rand = random.randint(vIntervalo_segundos, vIntervalo_segundos + 5)
              logging.debug('PORTABILIDADE - SLEEP - ' + str(rand))
              print(rand)
              sleep(rand)
            else:
              logging.info('PORTABILIDADE - Por favor, defina o campo de intervalo de mensagens na tabela de configuração')
              b.close()
              sys.exit('DEFINA O SLEEP NA CONFIGURAÇÃO DA MENSAGEM');                  
        
        SZChat_funcoes.fLogoutToken(vTOKEN_APP, vApiLogout)
        print('LOGOUT OK')

if __name__ == '__main__':
  Log_Format = "%(levelname)s %(asctime)s - %(message)s"

  logging.basicConfig(filename = "logTT.log",
                    filemode = "w",
                    format = Log_Format, 
                    level = logging.INFO,
                    encoding='utf-8')
  logging.info('START')
  main()