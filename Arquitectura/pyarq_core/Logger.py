# Basic
import logging
import traceback
import threading
import uuid
from logging.config import dictConfig

# logging
from logging.handlers import QueueListener
from multiprocessing import Queue

# Filesystem
from os import path
from pathlib import Path
import sys
import json

# Own
from .Base import ContextFilter
class Logger:
    """
    LOGGER
    ------
    Servicio para ofrecer logging centralizado al resto de servicios y aplicaciones
    """
    isCustomCOnf: bool
    def __init__(self,logger_config):
        log_conf_path='' # Ruta absoluta hacia el fichero de configuración
        if 'log_conf_path' not in logger_config:
            # Por defecto se busca la config en la __main__/resources/logger_conf.json
            main_path = path.realpath(sys.argv[0]) if sys.argv[0] else '.'
            parent_path = Path(main_path).parent
            log_conf_path = (parent_path / "resources/logger_conf.json").resolve()
        else:
            log_conf_path=logger_config['log_conf_path']
        self.__setup_logging(default_path=log_conf_path)
        self.generate_context()
        self.__logger = self.arqLogger()
        if(self.isCustomCOnf):
            self.__logger.debug("Se detectó configuración de logging custom - Configuración utilizada:%s",self.file_path)
        else:
            self.__logger.debug("Cargada configuración de logging por defecto")
        self.__logger.info("¡servicio de logging levantado!")

    def generate_context(self,my_uuid=None,extra_info:dict=None):
        """
        Añade información ligada al hilo actual de ejecución
        """
        if my_uuid is None:
            my_uuid:str=str(uuid.uuid4())

        context = {
            'uuid':my_uuid
            }

        if extra_info is not None:
            context.update(extra_info)

        threading.currentThread().__dict__['context'] = context

    def arqLogger(self):
        arqLogger = logging.getLogger("arquitecture")
        arqLogger.addFilter(ContextFilter())
        return arqLogger

    def appLogger(self):
        appLogger = logging.getLogger("app")
        appLogger.addFilter(ContextFilter())
        return appLogger

    def testingLogger(self):
        testingLogger = logging.getLogger("testing")
        testingLogger.addFilter(ContextFilter())
        return testingLogger
    
    def __handlerExceptions(self,Etype, value, tb):
        self.__logger.error("Excepción capturada:%s - %s",Etype,value)
        strTb = ''.join(traceback.format_tb(tb))
        self.__logger.exception("Traceback: %s",strTb)

    def __fixup(self, a_dict:dict, k:str, subst_dict:dict):
        for key in a_dict.keys():
            if key == k:
                for s_k, s_v in subst_dict.items():
                    a_dict[key] = a_dict[key].replace("{{"+s_k+"}}",s_v)
            elif type(a_dict[key]) is dict:
                self.__fixup(a_dict[key], k, subst_dict)

    def __setup_logging(self,
    default_path='logging.json'):
        """
        Setup logging configuration
        """
        custom_path = Path((sys.modules['__main__'].__file__)).parent
        custom_path = path.join(custom_path, "resources/")
        custom_path = path.join(custom_path, "logger_conf.json")
        if path.exists(custom_path):
            self.file_path = custom_path
            self.isCustomCOnf = True
        else:
            self.file_path = default_path
            self.isCustomCOnf = False

        with open(self.file_path, 'rt') as f:
            config = json.load(f)
            logger_properties=config["properties"]
            self.__fixup(config["logging_conf"],"filename",logger_properties)
            dictConfig(config["logging_conf"])
        # Sección no configurable desde fichero
        # Configuración de logging asíncrono
        self.arq_queue=Queue(maxsize=10000)
        self.__listener = QueueListener(self.arq_queue, *logging.getLogger("arquitecture").handlers)
        self.__listener.start()
        
        # Las excepciones son capturadas por el logger
        sys.excepthook = self.__handlerExceptions