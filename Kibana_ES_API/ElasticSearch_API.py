import requests, json, os
import configparser
from elasticsearch import Elasticsearch
def read_conf(configFilename):
    """
    Dado un nombre de fichero (tipo incluido), carga la configuración y se devuelve mapeada
    """
    config = configparser.ConfigParser()
    config.read(configFilename)
    return config

def parseLogFileToJson(logFileText):
    """
    Serializa un fichero log con trazas agrupadas
    """
    jsonText = ""
    return jsonText

def main():
    """
    Función de arranque del script
    """
    # Inicializacion de configuracion
    configMap = read_conf("configuration.cfg")
    directory = configMap['PATHS']['directoryLogs']
    res = requests.get(configMap['URLS']['request_endpoint'])
    es = Elasticsearch([
      {
        'host': configMap['URLS']['request_endpoint.host'],
        'port': configMap['URLS']['request_endpoint.port'],
        'http_auth': (configMap['SECURITY']['user'], configMap['SECURITY']['password'])
      }
      ])
    i = 0
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            with open(directory+"/"+filename) as myFile:
                dictToEncode = {}
                text = myFile.read()
                text = text.replace("}{","}\n{")
                jsonList = text.split('\n')
                for index,jsonFile in enumerate(jsonList,start=1):
                  datastore = json.loads(jsonFile)
                  if datastore['headers']['MensajeSalida'] is not None:
                    datastore['headers']['MensajeSalida']=json.loads(datastore['headers']['MensajeSalida'])
                  if datastore['headers']['MensajeEntrada'] is not None:
                    datastore['headers']['MensajeEntrada']=json.loads(datastore['headers']['MensajeEntrada'])
                  es.index(index=configMap['INDEX']['index.id'], ignore=400,
                  body=json.dumps(datastore))
                  print("se ha insertado el json formateado numero "+str(index))
                
if __name__ == '__main__':
  main()