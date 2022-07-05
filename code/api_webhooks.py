import logging
import uvicorn
from fastapi import FastAPI, status, Body, Depends, Response
import StayBox_funcoes
from models.model import WhTelecallSchema
from auth.auth_bearer_wh import JWTBearer
from starlette.responses import FileResponse
from datetime import datetime
import SZChat_funcoes
import bd_conecta

app_wh = FastAPI()

# CODIGO AUXILIAR - PRECISA BUSCAR DO BANCO DE DADOS
#def check_user(data: UserLoginSchema):
#    if data.email == 'leandromaia@telecall.com.br':
#        if  data.password=='@26ApiTche' :
#            #print('check_user: ok!')
#            return True
#        else: return False
#    return False

# ROTAS
#@app_wh.post("/login", tags=["AUTH"])
#async def user_login(user: UserLoginSchema = Body(...)):
#    if check_user(user):
#        return signJWTDontExpires(user.email)
#    return {"status_code": 404, "Mensagem": "Usuário não encontrado."}

@app_wh.post("/Telecall", status_code=status.HTTP_204_NO_CONTENT, tags=["WEBHOOKS"], dependencies=[Depends(JWTBearer())])
async def post_grava_dados(dados: WhTelecallSchema = Body(...)):
    try:
        print(datetime.now())
        print('')
        print(dados)
        print('')
        StayBox_funcoes.setWebHookTelecall(dados)

        try:
            result = SZChat_funcoes.getLogin(2) #API BOAS VINDAS
            if result != None:
                vApi = result[0]['api']
                vUsr = result[0]['usr']
                vUsr_Token = result[0]['usr_token']
                vPsw = result[0]['psw']
                vApiSend   = result[0]['api_send']
                vApiLogout = result[0]['api_logout']

                result = SZChat_funcoes.getMensagemConfig(4)
                if result != None:
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
                        print('Não foi possível autenticar na API.')     
                    else:
                        jauth = auth.json()
                        vTOKEN_APP = jauth['token']
                        vATENDDANCE_ID = SZChat_funcoes.getAtenddanceID(4) #boas vindas
            
                    vCelular = '5555996515339'
                    vMsgm = str(dados)

                    vAss = 'Alerta Telecall'
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
                        print('Código de Status: 200. '+ str(vCelular) )
                    else:
                        print('Código de Status: ' + str(send) + '. ' + str(vCelular) )
                    
                    #depois de disparar no szchat, grava o registro no bdaux
                    b = bd_conecta.conecta_db_aux()
                    StayBox_funcoes.setLogEnvio('4', 0, 0, 'ALERTA TELECALL', vCelular, str(send), 0, b)
                    
        except:
            print('Erro ao buscar login szchat ')

        return Response(status_code=status.HTTP_204_NO_CONTENT)
        #return {"status_code": 204, "Mensagem:": "Sucesso"}
        #return {"status_code": 204}
    except Exception as e: 
        logging.error('WH TELECALL - Código de Status: 404. ' + str(e))
        return {"status_code": 404, "Exception:": str(e)}



if __name__ == "__main__":
   uvicorn.run("api_webhooks:app_wh", host="0.0.0.0", port=18082, reload=True)