import requests, json, os
from elasticsearch import Elasticsearch
def main():
    # Inicializacion de server y directorio
    directory = 'C:\\Users\\r.gomez.bermejo\\Desktop\\pruebaDir'
    res = requests.get('http://localhost:9200')
    print (res.content)
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
    i = 0
    for filename in os.listdir(directory):
        if filename.endswith(".log"):
            with open(directory+"\\"+filename) as myFile:
                key = "event"+str(i)
                dictToEncode = {}
                text = myFile.read()
                delimiter = "}"
                comma = ","
                eventList =  [event+delimiter for event in text.split(delimiter) if event]

                for event in eventList:
                    dictEvent = json.loads(event)
                    if "id" in dictEvent:
                        key_id = dictEvent["id"]
                        del dictEvent["id"]
                        es.index(index='event', ignore=400, doc_type='docket', 
                        id=key_id, body=json.dumps(dictEvent))
                i = i + 1
if __name__ == '__main__':
  main()