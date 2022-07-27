import logging
from pprint import pp
from fastapi import FastAPI, status, Body, Depends, Response
from SynSuite_funcoes import getDadosPPOE
from models.model import WhTelecallSchema, UserLoginSchema
from auth.auth_bearer_wh import JWTBearer
from datetime import datetime
from fastapi.responses import JSONResponse
from pathlib import Path
import uvicorn


app = FastAPI()

@app.get("/get_dados/{ppoe}", tags=["UFSM"])
async def get_dados(ppoe: str):
    try:
        print(ppoe)
        logging.debug(ppoe)
        rs = getDadosPPOE(ppoe)
        return rs
    except Exception as e: 
        logging.error('API UFSM - Código de Status: 404. ' + str(e))
        print(str(e))
        return JSONResponse(status_code = status.HTTP_404_NOT_FOUND, content={'status':'false','message':'Ver LOG.'})
        #return {"status_code": 404, "Exception:": str(e)}

if __name__ == "__main__":
    cwd = Path(__file__).parent.resolve()
    uvicorn.run("api_ufsm:app", host="0.0.0.0", port=18084, reload=True, log_config=f"{cwd}/log.ini")    
