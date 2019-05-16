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

def main():
    """
    Función de arranque del script
    """
    # Inicializacion de configuracion
    configMap = read_conf("configuration.cfg")
    directory = configMap['PATHS']['directoryLogs']
    res = requests.get(configMap['URLS']['request_endpoint'])
    es = Elasticsearch([{'host': configMap['URLS']['request_endpoint.host'], 'port': configMap['URLS']['request_endpoint.port']}])
    i = 0
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            with open(directory+"\\"+filename) as myFile:
                key = "event"+str(i)
                dictToEncode = {}
                text = myFile.read()
                delimiter = "}"
                eventList =  [event+delimiter for event in text.split(delimiter) if event]

                for event in eventList:
                    dictEvent = json.loads(event)
                    if "id" in dictEvent:
                        key_id = dictEvent["id"]
                        del dictEvent["id"]
                        es.index(index='kafka_event', ignore=400, doc_type='kafka_log', 
                        id=key_id, body=json.dumps(dictEvent))
if __name__ == '__main__':
  main()