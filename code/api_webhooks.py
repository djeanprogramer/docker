import logging
#import uvicorn
from fastapi import FastAPI, status, Body, Depends, Response
import StayBox_funcoes
from models.model import WhTelecallSchema, UserLoginSchema
from auth.auth_bearer_wh import JWTBearer
#from starlette.responses import FileResponse
from datetime import datetime
from fastapi.responses import JSONResponse

app_wh = FastAPI()

# CODIGO AUXILIAR - PRECISA BUSCAR DO BANCO DE DADOS
#def check_user(data: UserLoginSchema):
#    if data.email == 'djean@tcheturbo.com.br':
#        if  data.password=='testej' :
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
        logging.debug(dados)
        if StayBox_funcoes.setWebHookTelecall(dados):
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content={'status':'false','message':'Ver LOG.'})    
    except Exception as e: 
        logging.error('WH TELECALL - Código de Status: 404. ' + str(e))
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content={'status':'false','message':'Ver LOG.'})
        #return {"status_code": 404, "Exception:": str(e)}

#if __name__ == "__main__":
#   uvicorn.run("api_webhooks:app_wh", host="0.0.0.0", port=18082, reload=True)