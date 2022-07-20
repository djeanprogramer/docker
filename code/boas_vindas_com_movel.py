import sys
import logging
import random
from time import sleep
#from pydantic import validate_arguments
import SZChat_funcoes
import SynSuite_funcoes
import bd_conecta
import json
#import pyparsing
#import time
from hora import getIsTimeSend
from StayBox_funcoes import setFilaEnvio

def setAtivacoesDoDia(vContratoID, vClienteID, vNome, vCelular, vStatus, vIDMensagem: str, vBD):
  sql = f"""INSERT INTO public.szchat_log_envio(
                contract_id, 
                client_id, 
                mensagem_id, 
                status,
                data_envio,
                nome,
                celular)
              VALUES ({vContratoID},
                      {vClienteID},
                      '{vIDMensagem}', 
                      {vStatus},
                      now(),
                      '{vNome}',
                      '{vCelular}');              
        """
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    #rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    logging.debug('BOAS_VINDAS -  INSERIU REGISTROS. Contrato/Cliente:' + str(vContratoID) + '/' + str(vClienteID) )
    return True
  except Exception as e:
    logging.error('BOAS_VINDAS - setAtivacoesDoDia() ' + str(e))
    logging.error(sql)
    return False

def getJaEnviou(vCelular, vCliente, vMensagemID: str, vBD):
  
  if vCelular != '':
    sql = f"""select l.id
            from szchat_log_envio l
            where l.mensagem_id = {vMensagemID}
              and (l.status = '200' or l.status = '-1')
              and date(l.data_envio) = date(current_date)
              and l.celular = '{vCelular}'; """
  else:
    sql = f"""select l.id
            from szchat_log_envio l
            where l.mensagem_id = {vMensagemID}
              and (l.status = '200' or l.status = '-1')
              and date(l.data_envio) = date(current_date)
              and l.client_id = {vCliente};"""
        
  try:
    cursor = vBD.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    vBD.commit()
    cursor.close()
    if len(rs) > 0:
      logging.debug('BOAS VINDAS - getJaEnviou - JÁ ENVIADO - Cliente/Celular/ID Mensagem Retorno: ' + str(vCliente) + '/' + str(vCelular) + '/' + str(rs[0]['id']))
      return rs[0]['id']
    else:    
      logging.debug('BOAS VINDAS - getJaEnviou - NÃO ENCONTROU - Cliente/Celular: ' + str(vCliente) + '/' + str(vCelular))
      return 0
    
  except Exception as e:
    logging.error('BOAS_VINDAS - getJaEnviou() ' + str(e))
    logging.error(sql)
    return -1

def main():
    #1 - CONECTA NO BD POSTGRESS E BUSCA CREDENCIAIS PARA API
    result = SZChat_funcoes.getLogin(2) 
    if result == None:
      logging.error('BOAS_VINDAS - main() - getLogin=NONE')
    else:
      logging.debug('BOAS_VINDAS - GET CREDENCIAIS SZCHAT OK')
      #vVersao = result[0]['versao']
      vApi = result[0]['api']
      vUsr = result[0]['usr']
      vUsr_Token = result[0]['usr_token']
      vPsw = result[0]['psw']
      vApiSend   = result[0]['api_send']
      vApiLogout = result[0]['api_logout']

      #2 - CONECTA NA API E BUSCA TOKEN
      auth = SZChat_funcoes.fAutenticar(vApi, vUsr, vPsw)
      if auth.status_code != 200:
        logging.error('BOAS VINDAS - Não foi possível autenticar na API.')     
        sys.exit('BOAS VINDAS - Não foi possível autenticar na API.')
      else:
          jauth = auth.json()
          vTOKEN_APP = jauth['token']
          vATENDDANCE_ID = SZChat_funcoes.getAtenddanceID(4)
          logging.debug('BOAS VINDAS - ATENDDANCE_ID: ' + vATENDDANCE_ID)
          logging.debug('BOAS VINDAS - TOKEN_APP: ' + vTOKEN_APP)
          
      #3 - CONECTA NO BD POSTGRESS E BUSCA AS CONFIGURAÇÕES DE MENSAGEM
      result = SZChat_funcoes.getMensagemConfig(2)
      if result == None:
        logging.error('BOAS_VINDAS - main() - getMensagemConfig=NONE')
      else:
        logging.debug('BOAS_VINDAS - MENSAGENS SZCHAT OK')
        vClose_session = result[0]['closed_session']
        vIntervalo_segundos = result[0]['intervalo_segundos']
        vMsgm = result[0]['msgm']
        #print(vId_equipe, vChanel_id, vClose_session, vIntervalo_segundos, vDescricao, vUsr, vUsr_Token)
        
        #3 - BUSCA TODAS AS ATIVAÇÕES DO DIA E FAZ UM LAÇO PARA ENVIAR (exceto móvel)
        ativacoes = SynSuite_funcoes.getAtivacoesDoDia('3,5') #só pessoa física e jurídica
        if ativacoes != None:
          b = bd_conecta.conecta_db_aux()
          
          for a in ativacoes:
              lista_servicos = ''
              servicos = SynSuite_funcoes.getAtivacoesDoDiaPlano(a['contrato_id'])
              for p in servicos:
                if lista_servicos == '':
                  lista_servicos = p['description']
                else:
                  lista_servicos = lista_servicos + ', ' + p['description']
              
              #trata o número do celular para envio da mensagem
              vCelular = SZChat_funcoes.fgetCelular(a['celular'], a['telefone'])
              res = getJaEnviou(vCelular, a['cliente_id'], '2', b) #retorna se já enviou a mensagem para o cliente/contrato
              
              if res == -1: #deu erro e para o processamento
                  b.close()
                  break
              elif res > 0: #já enviou mensagem de boas vindas para este número no dia de hoje
                continue
              else:
                if vCelular != '':
                  #mandar mensagem no szchat... pegar o retorno 200 é sucesso no envio.

                  vValor = str(a['amount'])
                  vValor = 'R$ ' +  vValor.replace(".",",")

                  vMsgEnvio = vMsgm.replace("{vplano}", lista_servicos)
                  vMsgEnvio = vMsgEnvio.replace("{vvalor}", vValor)
                  vMsgEnvio = vMsgEnvio.replace("{vdia}", str(a['collection_day']))

                  vSubjec = f"""B. Vindas: {a['contrato_id']} - {a['nome']} """

                  credenciais = {
                     'platform_id': vCelular,
                     'channel_id': '615c4aa0a0d3c7001208e518',
                     'type': 'text',
                     'message': vMsgEnvio,
                     'subject': vSubjec,
                     'token': vUsr_Token,
                     'agent' : vUsr,
                     'attendance_id': vATENDDANCE_ID,
                     'close_session': str(vClose_session)
                  }
                 
                  m = SZChat_funcoes.fEnviaWhatsapp(credenciais, vTOKEN_APP, vApiSend)
                  if m == 200:
                    logging.info('Código de Status: 200. '+ str(vCelular) )
                  else:
                    logging.info('Código de Status: ' + str(m) + '. ' + str(vCelular) )

                  #depois de disparar no szchat, grava o registro no bdaux
                  setAtivacoesDoDia(a['contrato_id'], a['cliente_id'],a['nome'],vCelular, str(m), '2', b)
                  
                  #atrasa o envio para não bloquear o número
                  if vIntervalo_segundos > 0:
                    rand = random.randint(vIntervalo_segundos, vIntervalo_segundos + 5)
                    logging.debug('BOAS_VINDAS - SLEEP - ' + str(rand))
                    sleep(rand)
                  else:
                    logging.info('BOAS VINDAS - Por favor, defina o campo de intervalo de mensagens na tabela de configuração')
                    b.close()
                    break;                  
              
              if vCelular == '':
                #não possui um celular válido - grava log de erro
                logging.info('BOAS_VINDAS -  SEM CELULAR NO CADASTRO. Contrato/Cliente:' + str(a['contrato_id']) + '/' + str(a['cliente_id']) )
                setAtivacoesDoDia(a['contrato_id'], a['cliente_id'],a['nome'],'', '-1', '2' , b)                
          b.close()

      #INICIO ENVIO MENSAGEM PARA O MÓVEL
      # - CONECTA NO BD POSTGRESS E BUSCA AS CONFIGURAÇÕES DE MENSAGEM MÓVEL
      result = SZChat_funcoes.getMensagemConfig(7)
      if result == None:
        logging.error('BOAS_VINDAS MÓVEL- main() - getMensagemConfig=NONE')
      else:
        vClose_session = result[0]['closed_session']
        vIntervalo_segundos = result[0]['intervalo_segundos']
        vMsgm = result[0]['msgm']
        #print(vId_equipe, vChanel_id, vClose_session, vIntervalo_segundos, vDescricao, vUsr, vUsr_Token)
        
        #3 - BUSCA TODAS AS ATIVAÇÕES DO DIA E FAZ UM LAÇO PARA ENVIAR
        ativacoes_movel = SynSuite_funcoes.getAtivacoesDoDiaMovel() #só MÓVEL
        if ativacoes_movel != None:
          b = bd_conecta.conecta_db_aux()
          for a in ativacoes_movel:
              lista_servicos = ''
              servicos = SynSuite_funcoes.getAtivacoesDoDiaPlano(a['contrato_id'])
              for p in servicos:
                if lista_servicos == '':
                  lista_servicos = p['description']
                else:
                  lista_servicos = lista_servicos + ', ' + p['description']
                
                lista_servicos = f"""*{lista_servicos}*"""
              
              #trata o número do celular para envio da mensagem
              vCelular = SZChat_funcoes.fgetCelular(a['celular'], a['telefone'])
              res = getJaEnviou(vCelular, a['cliente_id'], '7', b) #retorna se já enviou a mensagem para o cliente/contrato
              
              if res == -1: #deu erro e para o processamento
                  b.close()
                  break
              elif res > 0: #já enviou mensagem de boas vindas para este número no dia de hoje
                continue
              else:
                if vCelular != '':
                  #mandar mensagem no szchat... pegar o retorno 200 é sucesso no envio.
                  vNome = ''

                  vValor = str(a['amount'])
                  vValor = 'R$ ' +  vValor.replace(".",",")

                  vMsgmEnvio = vMsgm.replace("{vplano}", lista_servicos)
                  vMsgmEnvio = vMsgmEnvio.replace("{vvalor}", vValor)
                  vMsgmEnvio = vMsgmEnvio.replace("{vdia}", str(a['collection_day']))

                  #CHECK LIST FINAL
                  checklist = json.loads(str(a['final_checklist']))
                  if checklist != None:
                    portabilidade = None
                    data_portabilidade = None
                    hora_portabilidade = None
                    celular_portabilidade = None
                    plano_familia = None

                    for campo in checklist:
                      if checklist[campo]['label'] == 'É PORTABILIDADE':
                          portabilidade = checklist[campo]['value']
                      elif checklist[campo]['label'] == 'PORTABILIDADE':
                          portabilidade = checklist[campo]['value']                          
                      elif checklist[campo]['label'] == 'DATA AGENDADA':
                          data_portabilidade = checklist[campo]['value']
                      elif checklist[campo]['label'] == 'HORA AGENDADA':
                          hora_portabilidade = checklist[campo]['value']
                      elif checklist[campo]['label'] == 'CELULAR':
                          celular_portabilidade = checklist[campo]['value']
                      elif checklist[campo]['label'] == 'PLANO FAMILIA':
                          plano_familia = checklist[campo]['value']

                  if portabilidade == '1': #faz este tratamento para evitar de ir a palavra "None" na mensagem do zap
                    if celular_portabilidade == None:
                      celular_portabilidade = ''
                    if hora_portabilidade == None:
                      hora_portabilidade = ''  
                    
                    if plano_familia == '1': 
                      vMsgmEnvio = vMsgmEnvio.replace("{vportabilidade}", f"""👉A portabilidade do(s) número(s) *{celular_portabilidade}* foram agendadas para: *{data_portabilidade}* - *{hora_portabilidade}.* """)
                    else:
                      vMsgmEnvio = vMsgmEnvio.replace("{vportabilidade}", f"""👉A portabilidade do número *{celular_portabilidade}* foi agendada para: *{data_portabilidade}* - *{hora_portabilidade}* """)
                  else:
                    vMsgmEnvio = vMsgmEnvio.replace("{vportabilidade}", "")

                  vNome = str(a['nome']).split()
                  vMsgmEnvio = vMsgmEnvio.replace("{nome}", vNome[0] )

                  vSubjec = f"""B Móvel: {a['contrato_id']} - {a['nome']} """

                  credenciais = {
                      'platform_id': vCelular,
                      'channel_id': '615c4aa0a0d3c7001208e518',
                      'type': 'text',
                      'message': vMsgmEnvio,
                      'subject': vSubjec,
                      'token': vUsr_Token,
                      'agent' : vUsr,
                      'attendance_id': vATENDDANCE_ID,
                      'close_session': str(vClose_session)
                  }
                  
                  m = SZChat_funcoes.fEnviaWhatsapp(credenciais, vTOKEN_APP, vApiSend)
                  if m == 200:
                    logging.info('Código de Status: 200. '+ str(vCelular) )
                  else:
                    logging.info('Código de Status: ' + str(m) + '. ' + str(vCelular) )

                  #depois de disparar no szchat, grava o registro no bdaux
                  setAtivacoesDoDia(a['contrato_id'], a['cliente_id'],a['nome'],vCelular, str(m), '7', b)
                  
                  #se for portabilidade, já cria o registro na fila para o envio da mensagem de informação de troca de chip
                  if portabilidade == '1': 
                    vConfigPortabilidade = SZChat_funcoes.getMensagemConfig(8) #configuração de msg de portabilidade
                    if vConfigPortabilidade != None:
                      vMsgm = vConfigPortabilidade[0]['msgm']
                      if a['vpjpf'] == 'PF':
                        vNome = a['nome']
                        vFirstName = vNome.split()
                        vMsgm = vMsgm.replace("{nome}", vFirstName[0])
                      else:
                        vMsgm = vMsgm.replace("{nome}", "")
                      
                      if hora_portabilidade == '':
                        vTextData = data_portabilidade
                      else:
                        vTextData = f"""{hora_portabilidade} - {hora_portabilidade}."""
                      
                      vMsgm = vMsgm.replace("{data_port}", vTextData)
                      
                      #grava na fila, para que o outro processo realize o envio
                      try:
                        setFilaEnvio(a['contrato_id'],
                                     a['cliente_id'],
                                     a['nome'],
                                     vCelular,
                                     '0',
                                     vMsgm,
                                     '8',
                                     0,
                                     b,
                                     data_portabilidade
                                     )
                      except Exception as e:
                        logging.error('SetFilaEnvio: ' + str(e))
                        print('SetFilaEnvio: ' + str(e))

                  #atrasa o envio para não bloquear o número
                  if vIntervalo_segundos > 0:
                    rand = random.randint(vIntervalo_segundos, vIntervalo_segundos + 5)
                    logging.debug('BOAS_VINDAS - SLEEP - ' + str(rand))
                    sleep(rand)
                  else:
                    logging.info('BOAS VINDAS - Por favor, defina o campo de intervalo de mensagens na tabela de configuração')
                    b.close()
                    break;                  
                
                if vCelular == '':
                  #não possui um celular válido - grava log de erro
                  logging.info('BOAS_VINDAS -  SEM CELULAR NO CADASTRO. Contrato/Cliente:' + str(a['contrato_id']) + '/' + str(a['cliente_id']) )
                  setAtivacoesDoDia(a['contrato_id'], a['cliente_id'],a['nome'],'','-1','7', b)                
        
          b.close()
          
          SZChat_funcoes.fLogoutToken(vTOKEN_APP, vApiLogout)  

        print('BOAS_VINDAS - START/FINISH OK!')

if __name__ == '__main__':
  Log_Format = "%(levelname)s %(asctime)s - %(message)s"
  #Log_Level = logging.debug #logging.ERROR

  logging.basicConfig(filename = "logTT.log",
                    format = Log_Format, 
                    level = logging.INFO,
                    encoding='utf-8')

  logging.info('BOAS_VINDAS - START')
  
  #executar = getIsTimeSend
  #print(executar)
  if 1 == 1:
    print('BOAS_VINDAS - EXECUTANDO AGORA...')
    logging.info('BOAS_VINDAS - EXECUTANDO AGORA...')
    main()
  else:
    print('FORA DO INTERVALO DE HORAS...')
