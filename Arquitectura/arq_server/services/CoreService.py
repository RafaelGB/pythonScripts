# Basic
import configparser
import logging
from logging.config import fileConfig, dictConfig
from cachetools import cached, TTLCache
#Testing
import unittest
# Filesystem
from os import path, getenv,mkdir
from pathlib import Path
import sys
import json
# IoC
from dependency_injector import containers, providers

class Logger:
    """
    LOGGER
    ------
    Servicio para ofrecer logging centralizado al resto de servicios y aplicaciones
    """
    isCustomCOnf: bool
    def __init__(self):
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        logger_path = path.join(self.parent_path, "resources/logger_conf.json")
        self.__setup_logging(default_path=logger_path)
        self.logger = logging.getLogger("arquitecture")
        if self.isCustomCOnf:
            self.logger.info("conf de logger obtenida de '%s'",logger_path)
        else:
            self.logger.warn("ruta '%s' para configuración de logging no existente. Cargada configuración básica por defecto")
        self.logger.info("¡servicio de logging levantado!")

    def arqLogger(self):
        return logging.getLogger("arquitecture")

    def appLogger(self):
        return logging.getLogger("app")

    def testingLogger(self):
        return logging.getLogger("testing")

    def __fixup(self, a_dict:dict, k:str, subst_dict:dict) -> dict:
        for key in a_dict.keys():
            if key == k:
                for s_k, s_v in subst_dict.items():
                    a_dict[key] = a_dict[key].replace("{{"+s_k+"}}",s_v)
            elif type(a_dict[key]) is dict:
                self.__fixup(a_dict[key], k, subst_dict)

    def __setup_logging(self,
    default_path='logging.json',
    default_level=logging.INFO):
        """
        Setup logging configuration
        """
        file_path = default_path
        if path.exists(file_path):
            with open(file_path, 'rt') as f:
                config = json.load(f)
                self.__fixup(config["logging_conf"],"filename",config["properties"])
                logging.config.dictConfig(config["logging_conf"])
                self.isCustomCOnf = True
        else:
            self.isCustomCOnf = False
            logging.basicConfig(level=default_level)

class Configuration:
    """
    CONFIGURACION
    -------------
    Servicio para ofrecer configuración centralizada al resto de servicios y aplicaciones
    """
    def __init__(self,logger):
        self.__init_services(logger)
        self.logger.info("INI - servicio de Configuración")

        parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        self.__init_conf(parent_path,"arq_conf.cfg")
        self.logger.debug("-"*20)
        {section: self.logger.debug("Sección: %s",json.dumps(dict(self.confMap[section]))) for section in self.confMap.sections()}
        self.logger.debug("-"*20)
        self.logger.info("FIN - servicio de Configuración")
    
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
                    self.logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.logger.warn("El grupo '%s' no está definido en configuración", group)
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
                    self.logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.logger.warn("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyDefault(self, group, key, defaultValue,parseType=str):
        """
        Obtener propiedad en función del grupo y la clave.
        En caso de no existir, define un valor por defecto
        """
        propertyValue = self.getProperty(group,key,parseType)
        return (propertyValue, defaultValue)[propertyValue == None]
    
    def getGroupOfProperties(self,group_name):
        """
        Devuelve un grupo de propiedades.
        En caso de no existir devuelve 'None'
        """
        if group_name in self.confMap:
            return self.confMap[group_name]
        else:
            self.logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def getFilteredGroupOfProperties(self, group_name, callback):
        """
        Devuelve un grupo de propiedades filtradas en función de la condición impuesta por parámetro
        """
        if group_name in self.confMap:
            return self.__filterTheDict(self.confMap[group_name], callback)
        else:
            self.logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def __init_services(self,logger):
        # Servicio de logging
        self.logger = logger.arqLogger()
    
    def __init_conf(self,basepath,filename):
        self.confMap = configparser.ConfigParser()
        resources_path = path.join(basepath, "resources/")
        conf_path = path.join(resources_path, filename)
        self.logger.info("conf general obtenida de '%s'",conf_path)
        
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

    config_service = providers.Singleton(
        Configuration,
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
                         'init.test': True,
                         'enable.redis': False
                        }
                        
    if not path.exists(conf_path):
        mkdir(base_path)
    conf_path = path.join(base_path, filename)
    with open(conf_path, 'w') as configfile:
        config.write(configfile)
