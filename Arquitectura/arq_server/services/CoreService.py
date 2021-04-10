# Basic
import requests
import configparser
import logging
import traceback
import threading
import uuid
from logging.config import fileConfig, dictConfig
from cachetools import cached, TTLCache
from typing import Any, Dict

# Filesystem
from os import path, getenv,mkdir
from pathlib import Path
import sys
import json
# IoC
from dependency_injector import containers, providers
#own
from arq_server.base.ArqErrors import ArqError
from arq_server.base.Constants import Const

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
        return logging.getLogger("testing")
    
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
            self.__fixup(config["logging_conf"],"filename",config["properties"])
            dictConfig(config["logging_conf"])
        # Las excepciones son capturadas por el logger
        sys.excepthook = self.__handlerExceptions

class Base:
    """
    BASE
    ------
    Funciones cross a todos los servicios
    """
    __const:Const
    __logger:Logger
    def __init__(self,logger,const) -> None:
        self.__init_services(logger,const)
    
    def __init_services(self,logger,const):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__const = const

    def read_input_instruccions(self,instructions:dict,**kwargs)->dict:
        try:
            result = getattr(
                self,
                instructions.pop("action")
            )(
                *instructions.pop("args"),
                **self.__parse_kwargs_instructions(instructions.pop('kwargs'),**kwargs)
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

class Configuration(Base):
    """
    CONFIGURACION
    -------------
    Servicio para ofrecer configuración centralizada al resto de servicios y aplicaciones
    """
    __const:Const
    __logger:logging.Logger
    __allModulesConfDict : Dict
    def __init__(self,logger,const,configuration_config):
        self.__init_services(logger,const)
        self.__logger.info("INI - servicio de Configuración")
        try:
            self.__init_conf(configuration_config['github'])
        except Exception as ex:
            raise ArqError("Error: no se han definido las credenciales para recuperar la configuración")
        self.__logger.info("FIN - servicio de Configuración")
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getProperty(self, group, key, parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave ( usando cache )
        """
        if group in self.__allModulesConfDict[confKey]:
            if key in self.__allModulesConfDict[confKey][group]:
                try:
                    return parseType(self.__allModulesConfDict[confKey][group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warn("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyVerbose(self, group, key, parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave ( sin usar cache )
        """
        if group in self.__allModulesConfDict[confKey]:
            if key in self.__allModulesConfDict[confKey][group]:
                try:
                    return parseType(self.__allModulesConfDict[confKey][group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warn("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyDefault(self, group, key, defaultValue:Any,parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave.
        En caso de no existir, define un valor por defecto
        """
        propertyValue = self.getProperty(group,key,parseType=parseType,confKey=confKey)
        return (propertyValue, defaultValue)[propertyValue == None]
    
    def getGroupOfProperties(self,group_name,confKey="arq", **kwargs):
        """
        Devuelve un grupo de propiedades.
        En caso de no existir devuelve 'None'
        """
        if group_name in self.__allModulesConfDict[confKey]:
            return self.__allModulesConfDict[confKey][group_name]
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def getFilteredGroupOfProperties(self, group_name, callback,confKey="arq", **kwargs):
        """
        Devuelve un grupo de propiedades filtradas en función de la condición impuesta por parámetro
        """
        if group_name in self.__allModulesConfDict[confKey]:
            return self.__filterTheDict(self.__allModulesConfDict[confKey][group_name], callback)
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def __init_services(self,logger,const):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__const = const
    
    def __init_conf(self,credentialsPath):
        """
        Dado un fichero de credenciales, recupera configuración de un repositorio git
        """
        self.__allModulesConfDict = self.__getConfFromGit(credentialsPath)

    def __getConfFromGit(self,credentials) -> dict:
        """
        Recupera configuración de un repositorio git
        """ 
        self.__logger.info("Obteniendo configuracion con perfil %s en git",credentials['profile'])
        confDict={}
        content= credentials['content_url']+credentials['profile']
        filelist=request(content,headers={'Authorization':'Token '+credentials['config_token']})
        for hit in json.loads(filelist.text):
            self.__logger.info("Fichero '%s' obtenido",hit["name"])
            funcConf=configparser.ConfigParser()
            urlFile=self.__generate_git_file_url(
                credentials['user'],
                credentials['repo'],
                credentials['branch'],
                hit['path'])
            response=request(urlFile,headers={'Authorization':'Token '+credentials['config_token']})
            funcConf.read_string(response.text)
            confDict[hit["name"][:hit["name"].index(".")]]=funcConf
        return confDict
    
    def __generate_git_file_url(self,user,repo,branch,path):
        separator='/'
        url="https://raw.githubusercontent.com"
        url = url+separator+user
        url = url+separator+repo
        url = url+separator+branch
        url = url+separator+path
        return url
        
    def __filterTheDict(self, dictObj, callback):
        newDict = dict()
        # Itera sobnrte todos los elementos del diccionario
        for (key, value) in dictObj.items():
            # Comprueba si satisface la condición del parámetro para añadir al diccionario
            if callback(key):
                newDict[key] = value
        return newDict


"""
Inversion of control section
""" 
class CoreService(containers.DeclarativeContainer):
    """Application IoC container."""
    # Configuration
    config = providers.Configuration()
    # Services
    logger_service = providers.Singleton(Logger,logger_config=config.logger)
    constants = providers.Singleton(Const)

    base_service = providers.Singleton(
        Base,
        const=constants,
        logger=logger_service
    )
    
    config_service = providers.Singleton(
        Configuration,
        const=constants,
        logger=logger_service,
        configuration_config=config.configuration
    )

def request(url: str, params:dict = {},headers:dict = {}):
    return requests.get(url,params=params, headers=headers)
