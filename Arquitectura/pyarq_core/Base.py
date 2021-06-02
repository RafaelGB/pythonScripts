import requests
# Basic
import logging
import threading
#own
from .ArqErrors import ArqError

# Switch selección de parseo
parserDict={
    'int':int,
    'eval':eval,
    'str': str
}

class ContextFilter(logging.Filter):
    """
    Filtro que aplica los filtros deseados al log
    """
    def filter(self, record):
        if 'context' in threading.currentThread().__dict__:
            context = threading.currentThread().__dict__['context']
            if 'uuid' in context:
                record.UUID=context['uuid']
            return True
        else:
            return False

class Base:
    """
    BASE
    ------
    Funciones cross a todos los servicios. 
    NO DEBE TENER SERVICIOS DEL CONTENEDOR 
    """

    def read_input_instruccions(self,instructions:dict,**kwargs)->dict:
        try:
            result = getattr(
                self,
                instructions.pop("action")
            )(
                *instructions.pop("args"), # *args
                **self.__parse_kwargs_instructions(instructions.pop('kwargs'),**kwargs) # **kwargs
            )
        except AttributeError as attError:
            raise ArqError("La acción "+instructions["action"]+" no está contemplada")
        except TypeError as tpError:
            raise ArqError("Los argumentos de entrada no son correctos (sobran o faltan)")
        instructions["output_instructions"]=result
        return instructions

    def __parse_kwargs_instructions(self,kwargs_instructions:list,**kwargs):
        parsed_kwargs={}
        for hit in kwargs_instructions:
            parsed_kwargs[hit['key']]=parserDict[hit['type']](hit['value'])
        parsed_kwargs.update(kwargs)
        return parsed_kwargs

def request(url: str, params:dict = {},headers:dict = {}):
    return requests.get(url,params=params, headers=headers)