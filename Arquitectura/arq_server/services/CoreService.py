# Basic
import configparser
import logging
import traceback
from logging.config import fileConfig, dictConfig
from cachetools import cached, TTLCache
from typing import Any
#Testing
import unittest
# Filesystem
from os import path, getenv,mkdir
from pathlib import Path
import sys
import json
# IoC
from dependency_injector import containers, providers
#own
from arq_server.base.Constants import Const


class Logger:
    """
    LOGGER
    ------
    Servicio para ofrecer logging centralizado al resto de servicios y aplicaciones
    """
    isCustomCOnf: bool
    def __init__(self):
        main_path = path.realpath(sys.argv[0]) if sys.argv[0] else '.'
        parent_path = Path(main_path).parent
        logger_path = (parent_path / "resources/logger_conf.json").resolve()
        print("\n\nruta padre de la configuracion:\n" + str(parent_path)+"\n"+str(main_path)+"\n"+str(logger_path))
        self.__setup_logging(default_path=logger_path)
        self.__logger = logging.getLogger("arquitecture")
        if(self.isCustomCOnf):
            self.__logger.debug("Se detectó configuración de logging custom - Configuración utilizada:%s",self.file_path)
        else:
            self.__logger.debug("Cargada configuración de logging por defecto")
        self.__logger.info("¡servicio de logging levantado!")

    def arqLogger(self):
        return logging.getLogger("arquitecture")

    def appLogger(self):
        return logging.getLogger("app")

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
        custom_path = path.join(custom_path, "resources/").join("logger_conf.json")
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

class Configuration:
    """
    CONFIGURACION
    -------------
    Servicio para ofrecer configuración centralizada al resto de servicios y aplicaciones
    """
    __const:Const
    __logger:logging.Logger

    def __init__(self,logger,const):
        self.__init_services(logger,const)
        self.__logger.info("INI - servicio de Configuración")

        parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        self.__init_conf(parent_path,self.__const.RESOURCE_ARQ_CONF_FILENAME)
        self.__logger.debug("-"*20)
        {section: self.__logger.debug("Sección %s: %s",section,json.dumps(dict(self.confMap[section]))) for section in self.confMap.sections()}
        self.__logger.debug("-"*20)
        self.__logger.info("FIN - servicio de Configuración")
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getProperty(self, group, key, parseType=str):
        """
        Obtener propiedad en función del grupo y la clave ( usando cache )
        """
        if group in self.confMap:
            if key in self.confMap[group]:
                try:
                    return parseType(self.confMap[group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warn("El grupo '%s' no está definido en configuración", group)
            return None
    
    def getPropertyVerbose(self, group, key, parseType=str):
        """
        Obtener propiedad en función del grupo y la clave ( sin usar cache )
        """
        if group in self.confMap:
            if key in self.confMap[group]:
                try:
                    return parseType(self.confMap[group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warn("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyDefault(self, group, key, defaultValue:Any,parseType=str) -> Any:
        """
        Obtener propiedad en función del grupo y la clave.
        En caso de no existir, define un valor por defecto
        """
        propertyValue = self.getProperty(group,key,parseType=parseType)
        return (propertyValue, defaultValue)[propertyValue == None]
    
    def getGroupOfProperties(self,group_name):
        """
        Devuelve un grupo de propiedades.
        En caso de no existir devuelve 'None'
        """
        if group_name in self.confMap:
            return self.confMap[group_name]
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def getFilteredGroupOfProperties(self, group_name, callback):
        """
        Devuelve un grupo de propiedades filtradas en función de la condición impuesta por parámetro
        """
        if group_name in self.confMap:
            return self.__filterTheDict(self.confMap[group_name], callback)
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def __init_services(self,logger,const):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__const = const

    def __init_conf(self,basepath,filename):
        self.confMap = configparser.ConfigParser()
        resources_path = path.join(basepath, "resources/")
        conf_path = path.join(resources_path, filename)
        self.__logger.info("conf general obtenida de '%s'",conf_path)
        
        if not path.exists(conf_path):
            generate_default_conf(resources_path,filename)
        self.confMap.read(conf_path)

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

    # Gateways

    #database_client = providers.Singleton(sqlite3.connect, config.database.dsn)

    # Services
    logger_service = providers.Singleton(Logger)
    constants = providers.Singleton(Const)
    config_service = providers.Singleton(
        Configuration,
        const=constants,
        logger=logger_service
    )

def generate_default_conf(base_path:str, filename:str):
    config = configparser.ConfigParser()
    config['groups'] = {
                         'environment': 'environment',
                         'applications': 'applications',
                         'flask': 'flask',
                         'flags': 'flags',
                         'redis': 'redis'
                        }
    config['base'] = {
                         'path.resources': 'resources/'
                        }    

    config['applications'] = {
                         'filename.method_views': 'methodViews.json',
                         'path.app.repository': 'apps/'
                        }

    config['flask'] = {
                         'shutdown': 'werkzeug.server.shutdown',
                         'url.rule.applications': '/api/applications/<app_name>;applications_api'
                        }
    
    config['flags'] = {
                         'init.test': 'True',
                         'enable.redis': 'False'
                        }
                        
    if not path.exists(base_path):
        mkdir(base_path)
    conf_path = path.join(base_path, filename)
    with open(conf_path, 'w') as configfile:
        config.write(configfile)
