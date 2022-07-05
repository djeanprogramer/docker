import logging
import psycopg2 as postresdb
from psycopg2.extras import RealDictCursor
import yaml

def conecta_db_aux():
  try:
    config_data = yaml.load(open("secrets.yml"), Loader=yaml.FullLoader)
    logging.debug('Leu o arquivo YML')
  except Exception as e:
    logging.error('BD AUX: NÃO FOI POSSÍVEL LER O ARQUIVO YAML: '+ str(e))  
    return 

  try:
    con = postresdb.connect(host=config_data["dbaux_host"], 
                         database=config_data["dbaux_database"],
                         user=config_data["dbaux_username"], 
                         password=config_data["dbaux_password"],
                         port=config_data["dbaux_port"],
                         cursor_factory=RealDictCursor)
    logging.debug('BD AUX: CONECTOU')
  except Exception as e:
    logging.error('BD AUX: NÃO FOI POSSÍVEL CONECTAR: '+ str(e))  
    return 
  return con

def conecta_db_tche():
  try:
    config_data = yaml.load(open("secrets.yml"), Loader=yaml.FullLoader)
    logging.debug('Leu o arquivo YML')
  except Exception as e:
    logging.error('BD TCHE: NÃO FOI POSSÍVEL LER O ARQUIVO YAML: '+ str(e))  
    return 

  try:
    conn = postresdb.connect(host=config_data["dbtche_Host"], 
                         database=config_data["dbtche_Database"],
                         user=config_data["dbtche_User"], 
                         password=config_data["dbtche_Password"],
                         port=config_data["dbtche_Port"],
                         cursor_factory=RealDictCursor)

    logging.debug('BD TCHE: CONECTOU')
  except Exception as e:
    logging.error('2BD TCHE: NÃO FOI POSSÍVEL CONECTAR: '+ str(e))  
    return 

  return conn