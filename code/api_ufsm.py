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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    
    "http://177.190.118.64:18081",
    "http://177.190.118.64:18083",
    "http://177.190.118.64:18084",
    "http://177.190.118.64:18085",
    "http://187.108.16.57:18082",
    "http://187.108.16.57:18081",
    "http://187.108.16.57:18085",    
    "http://187.108.16.57:18084"
    "http://187.108.16.57:8082",
    "http://187.108.16.57:8081",
    "http://187.108.16.57",
    "http://187.108.16.57:8080",
    "http://localhost:18080",
    "http://localhost:18081",
    "http://localhost:18084",
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
