import logging
import yaml
from typing import Dict
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

try:
    config_data = yaml.load(open("./secrets.yml"), Loader=yaml.FullLoader)
    JWT_SECRET = config_data["auth_secret"]
    JWT_ALGORITHM = config_data["auth_algorithm"]
    JWT_ACCESS_TOKEN_EXPIRE = config_data["auth_access_token_expire_hours"]

    logging.debug('Leu o arquivo YML')
except Exception as e:
    logging.error('BD AUX: NÃO FOI POSSÍVEL LER O ARQUIVO YAML: '+ str(e))  

def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": (datetime.utcnow() + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE)).isoformat()
    }

    try:
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        print(token)
    except Exception as e:
      print('excessão : '+ str(e))  

    return token_response(token)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        vAgora = (datetime.now()).isoformat()
        return decoded_token if decoded_token["expires"] >= vAgora else None
    except:
        return {}