import os
import logging
from datetime import date, datetime
from http.client import HTTPException
#from urllib import response
from fastapi import FastAPI, status, Body, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import StayBox_funcoes
import SynSuite_funcoes
import bd_conecta
import SZChat_funcoes
import docker
from models.model import UserLoginSchema 
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT
from starlette.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

favicon_path = './images/favicon.png'

app = FastAPI()

origins = [
    "http://187.108.16.57:18082",
    "http://187.108.16.57:18081",
    "http://187.108.16.57:18085",    
    "http://187.108.16.57:8082",
    "http://187.108.16.57:8081",
    "http://187.108.16.57",
    "http://187.108.16.57:8080",
    "http://localhost:18080",
    "http://localhost:18081",
    "http://localhost:18082",
    "http://localhost:18085",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost"    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CODIGO AUXILIAR

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    #print(f"OPS Tchê! An HTTP error!: {repr(exc)}")
    logging.error(f"OPS Tchê! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    #print(f"OPS Tchê! The client sent invalid data!: {exc}")
    logging.error(f"OPS Tchê! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)

def check_user(data: UserLoginSchema):
    if data.email == 'djean@tcheturbo.com.br':
        if  data.password=='testej' :
            #print('check_user: ok!')
            return True
        else: return False
    return False

# ROTAS
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)

@app.get("/", tags=["ROOT"])
def raiz():
    return {"Start":"API - Tchê"}

#, dependencies=[Depends(JWTBearer())] --status_code=status.HTTP_200_OK,
@app.get("/dash/log_envios/{data_envio}", tags=["DASH"])
def log_envios(data_envio: str):
    try:
        #d1 = datetime.strptime(data_envio, '%d%m%Y')
        log = StayBox_funcoes.getLogEnvios(data_envio)
        headers = {"Content-Type": "application/json",
                   "Access-Control-Allow-Methods": "GET",
                   "Access-Control-Allow-Headers": "*",
                   "Access-Control-Allow-Origin": "*"}
        if len(log) > 0:
            return JSONResponse(headers=headers, content=log)
        else:
            return JSONResponse(status_code = 404, content={'status':'false','message':'Nenhum resultado encontrado.'})
    except Exception as e: 
        print(str(e))
        logging.error('Exception: ' +  str(e))
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content={'status':'false','message':str(e)})

@app.get("/dash/log_portabilidades/", status_code=status.HTTP_200_OK, tags=["DASH"])
def log_portabilidades():
    try:
        log = StayBox_funcoes.getLogPortabilidades()
        headers = {"Content-Type": "application/json",
                   "Access-Control-Allow-Methods": "GET",
                   "Access-Control-Allow-Headers": "*",
                   "Access-Control-Allow-Origin": "*"
        }
        return JSONResponse(content=log, headers=headers)

    except Exception as e: 
        return {"status_code" : status.HTTP_404_NOT_FOUND, "Exception:": str(e)}

@app.get("/dash/log_portabilidades_erros/", status_code=status.HTTP_200_OK, tags=["DASH"])
def log_erros_portabilidades():
    try:
        log = StayBox_funcoes.getLogPortabilidadesErros()
        headers = {"Content-Type": "application/json",
                   "Access-Control-Allow-Methods": "GET",
                   "Access-Control-Allow-Headers": "*",
                   "Access-Control-Allow-Origin": "*"
        }
        return JSONResponse(content=log, headers=headers)

    except Exception as e: 
        return {"status_code" : status.HTTP_404_NOT_FOUND, "Exception:": str(e)}

@app.post("/dash/cardcabecalho/", status_code=status.HTTP_200_OK, tags=["DASH"])
def cards_cabecalho():
    try:
        log = StayBox_funcoes.getCardCabecalho()
        headers = {"Content-Type": "application/json"}
        return JSONResponse(content=log, headers=headers)

    except Exception as e: 
        return {"status_code" : status.HTTP_404_NOT_FOUND, "Exception:": str(e)}

@app.post("/dash/cardcabecalhotelecall/", status_code=status.HTTP_200_OK, tags=["DASH"])
def cards_cabecalho_telecall():
    try:
        log = StayBox_funcoes.getCardCabecalhoTelecall()
        headers = {"Content-Type": "application/json",
                   "Access-Control-Allow-Methods": "GET",
                   "Access-Control-Allow-Headers": "*",
                   "Access-Control-Allow-Origin": "*"
        }

        
        return JSONResponse(content=log, headers=headers)

    except Exception as e: 
        return {"status_code" : status.HTTP_404_NOT_FOUND, "Exception:": str(e)}

@app.post("/fila/criar_fila_parcela_vencida/{DDMMYYY_DDMMYYY}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED, tags=["FILA"])
def post_criar_fila_parcela_vencida(DDMMYYY_DDMMYYY: str):
    try:
        intervalo = DDMMYYY_DDMMYYY.split('_') 
        d1 = datetime.strptime(intervalo[0], '%d%m%Y')
        d2 = datetime.strptime(intervalo[1], '%d%m%Y')
        
        dias = (d2 - d1).days
        if dias > 31:
            return {"status_code": 404, "Mensagem": "Utilize intervalo máximo de 1 mês."}
        elif dias < 0:
            return {"status_code": 404, "Mensagem": "Intervalo de datas incorreto."}
        else:
            rs = SynSuite_funcoes.getFilaParcelaVencida(d1,d2)  #função que pega parcelas da VOALLE
            if rs != None:
                vFila = []
                b = bd_conecta.conecta_db_aux()
                
                msgCfg = SZChat_funcoes.getMensagemConfig('1') #carrega a mensagem padrão configurada no BD Aux
                vMsgModelo = msgCfg[0]['msgm']

                #gravar no BD StayBox
                for i in rs:
                    vFila.append(i)

                    vCelular = vCelular = SZChat_funcoes.fgetCelular(i['cell_phone_1'], i['phone']) #Valida se é celular

                    if i['type_tx_id'] != 2: #JURÍDICA, não informa o nome na mensagem
                        vNome = ''
                    else: #FÍSICA, só envia primeiro nome
                        vNome = str(i['name'])
                        vNome = vNome.split()
                        vNome = ' ' + vNome[0]
                    
                    vMsgm = str(vMsgModelo).replace("{vNome}", vNome  )
                    vMsgm = str(vMsgm).replace("{vNumContrato}", str(i['contract_id']) )
                    v = i['expiration_date'] 
                    vDataStr = v.strftime('%d/%m/%Y')
                    vMsgm = str(vMsgm).replace("{Vencimento}", vDataStr ) 

                    #grava na fila, para que o outro processo realize o envio
                    if not StayBox_funcoes.setFilaEnvio(i['contract_id'],
                                                 i['client_id'],
                                                 i['name'],
                                                 vCelular,
                                                 '0',
                                                 vMsgm,
                                                 '1',
                                                 i['frt_id'],
                                                 b
                                                ):
                        b.close()
                        return {"status_code": 404, "Mensagem": "Erro ao incluir Fila."}

                b.close()
                #return rs
                return {"status_code": 202, "Mensagem:": "Parcelas registradas na fila!", "Resultado:": vFila}
            else:
                return {"status_code": 404, "Mensagem": "Nenhuma parcela foi encontrada."}
            
    except Exception as e: 
        return {"status_code": 402, "Mensagem": "Data informada inválida. Utilize DDMMYYYY_DDMMYYY. Intervalo máximo de 1 mês.", "Exception:": str(e)}
    
@app.post("/fila/criar_fila_aviso_bloqueio/{DDMMYYY}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED, tags=["FILA"])
def post_criar_fila_aviso_bloqueio(DDMMYYY: str):

    try:
        d1 = datetime.strptime(DDMMYYY, '%d%m%Y').date() 
        print(d1)

        d2 = date.today()
        print(d2)

        dias = (d2 - d1).days
        print(dias)
        if d1 >= d2:
            return {"status_code": 404, "Mensagem": "Data informada inválida. Ainda não venceu."}
        else:
            rs = SynSuite_funcoes.getFilaAvisoBloqueio(d1)  #função que pega parcelas da VOALLE
            if rs != None:
                vFila = []
                b = bd_conecta.conecta_db_aux()
                
                msgCfg = SZChat_funcoes.getMensagemConfig('3') #carrega a mensagem padrão configurada no BD Aux
                vMsgModelo = msgCfg[0]['msgm']

                #gravar no BD StayBox
                for i in rs:
                    vFila.append(i)

                    vCelular = vCelular = SZChat_funcoes.fgetCelular(i['cell_phone_1'], i['phone']) #Valida se é celular

                    if i['type_tx_id'] != 2: #JURÍDICA, não informa o nome na mensagem
                        vNome = ''
                    else: #FÍSICA, só envia primeiro nome
                        vNome = str(i['name'])
                        vNome = vNome.split()
                        vNome = ' ' + vNome[0]
                    
                    vMsgm = str(vMsgModelo).replace("{vNome}", vNome  )
                    vMsgm = str(vMsgm).replace("{vNumContrato}", str(i['contract_id']) )
                    v = i['expiration_date'] 
                    vDataStr = v.strftime('%d/%m/%Y')
                    vMsgm = str(vMsgm).replace("{Vencimento}", vDataStr ) 

                    #grava na fila, para que o outro processo realize o envio
                    StayBox_funcoes.setFilaEnvio(i['contract_id'],
                                                 i['client_id'],
                                                 i['name'],
                                                 vCelular,
                                                 '0',
                                                 vMsgm,
                                                 '3',
                                                 0,
                                                 b
                                                )

                b.close()
                #return rs
                return {"status_code": 202, "Mensagem:": "Avisos de boquios registradas na fila!", "Resultado:": vFila}
            else:
                return {"status_code": 404, "Mensagem": "Nenhuma parcela foi encontrada."}
            
    except Exception as e: 
        return {"status_code": 402, "Mensagem": "Data informada inválida. Utilize DDMMYYYY.", "Exception:": str(e)}    

@app.post("/fila/criar_fila_serasa_spc/{DDMMYYY_DDMMYYY}", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED, tags=["FILA"])
def post_criar_fila_serasa_spc(DDMMYYY_DDMMYYY: str):

    try:
        intervalo = DDMMYYY_DDMMYYY.split('_') 
        d1 = datetime.strptime(intervalo[0], '%d%m%Y')
        d2 = datetime.strptime(intervalo[1], '%d%m%Y')
        
        dias = (d2 - d1).days
        if dias < 0:
            return {"status_code": 404, "Mensagem": "Intervalo de datas incorreto."}
        else:
            rs = SynSuite_funcoes.getFilaSerasaSPC(d1,d2)  #função que pega parcelas da VOALLE
            if rs != None:
                vFila = []
                b = bd_conecta.conecta_db_aux()

                msgCfg = SZChat_funcoes.getMensagemConfig('4') #carrega a mensagem padrão configurada no BD Aux
                vMsgModelo = msgCfg[0]['msgm']

                #gravar no BD StayBox
                for i in rs:
                    vFila.append(i)

                    vCelular = vCelular = SZChat_funcoes.fgetCelular(i['cell_phone_1'], i['phone']) #Valida se é celular

                    #grava na fila, para que o outro processo realize o envio
                    if not StayBox_funcoes.setFilaEnvio(i['contract_id'],
                                                        i['client_id'],
                                                        i['name'],
                                                        vCelular,
                                                        '0',
                                                        vMsgModelo,
                                                        '4',
                                                        'Null',
                                                        b ):
                        b.close()
                        return {"status_code": 404, "Mensagem": "Erro ao incluir Fila."}

                b.close()
                #return rs
                return {"status_code": 202, "Mensagem:": "Parcelas registradas na fila!", "Resultado:": vFila}
            else:
                return {"status_code": 404, "Mensagem": "Nenhuma parcela foi encontrada."}
            
    except Exception as e: 
        return {"status_code": 402, "Mensagem": "Data informada inválida. Utilize DDMMYYYY_DDMMYYY. Intervalo máximo de 1 mês.", "Exception:": str(e)}

@app.post("/user/login", tags=["USER"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        headers = {"Content-Type": "application/json",
                   "charset":"utf-8"}
        conteudo = signJWT(user.email)
        return conteudo
        #return JSONResponse(content=conteudo, status_code=status.HTTP_200_OK, headers=headers)
    else:
        return {"status_code": 404, "Mensagem": "Usuário não encontrado."}
            
@app.post("/fila/criar_fila_aviso_fim_impressao_boletos/", dependencies=[Depends(JWTBearer())], status_code=status.HTTP_202_ACCEPTED, tags=["FILA"])
def criar_fila_aviso_fim_impressao_boletos():
    try:
        rs = SynSuite_funcoes.getFilaAvisoFimImpressaoBoletos()  #função que pega clientes que possuem boleto impresso
        if rs != None:
            vFila = []
            b = bd_conecta.conecta_db_aux()
            
            msgCfg = SZChat_funcoes.getMensagemConfig('5') #carrega a mensagem padrão configurada no BD Aux
            vMsgModelo = msgCfg[0]['msgm']

            #gravar no BD StayBox
            for i in rs:
                vFila.append(i)

                vCelular = vCelular = SZChat_funcoes.fgetCelular(i['cell_phone_1'], i['phone']) #Valida se é celular

                if i['type_tx_id'] != 2: #JURÍDICA, não informa o nome na mensagem
                    vNome = ''
                else: #FÍSICA, só envia primeiro nome
                    vNome = str(i['name'])
                    vNome = vNome.split()
                    vNome = ' ' + vNome[0]
                
                vMsgm = str(vMsgModelo).replace("{vNome}", vNome  )

                #grava na fila, para que o outro processo realize o envio
                StayBox_funcoes.setFilaEnvio(i['contract_id'],
                                                i['client_id'],
                                                i['name'],
                                                vCelular,
                                                '0',
                                                vMsgm,
                                                '5',
                                                0,
                                                b
                                            )

            b.close()
            #return rs
            return {"status_code": 202, "Mensagem:": "Avisos registradas na fila!", "Resultado:": vFila}
        else:
            return {"status_code": 404, "Mensagem": "Nenhum cliente foi encontrado."}
            
    except Exception as e: 
        return {"status_code": 402, "Mensagem": "Dados informados inválidos.", "Exception:": str(e)}    

@app.get("/exec/fila_cobranca/", tags=["EXEC"])
def exec_fila_cobranca():
    try:
        client = docker.from_env()
        client.containers.run('serviceszchat', environment=['script=exec_fila_cobranca.py'] , detach=True, remove=True, name='Exec_AvisoBloq')
    except Exception as e: 
        print(str(e))
        return {"status_code": 402, "Mensagem": "Erro ao executar script.", "Exception:": str(e)}    

@app.get("/exec/fila_aviso_bloqueio/", tags=["EXEC"])
def exec_fila_aviso_bloqueio():
    try:
        client = docker.from_env()
        client.containers.run('serviceszchat', environment=['script=exec_fila_aviso_bloqueio.py'] , detach=True, remove=True, name='Exec_AvisoBloq')
    except Exception as e: 
        print(str(e))
        return {"status_code": 402, "Mensagem": "Erro ao executar script.", "Exception:": str(e)}    

@app.get("/exec/fila_serasa_spc/", tags=["EXEC"])
def exec_fila_aviso_bloqueio():
    try:
        client = docker.from_env()
        client.containers.run('serviceszchat', environment=['script=exec_fila_serasa_spc.py'] , detach=True, remove=True, name='Exec_Serasa')
    except Exception as e: 
        print(str(e))
        return {"status_code": 402, "Mensagem": "Erro ao executar script.", "Exception:": str(e)}    