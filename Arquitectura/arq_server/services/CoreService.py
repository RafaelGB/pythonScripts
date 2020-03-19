# Basic
import configparser
import logging
from logging.config import fileConfig, dictConfig
#Testing
import unittest
# Filesystem
from os import path, getenv
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
    def __init__(self):
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        logger_path = path.join(self.parent_path, "resources/logger_conf.json")
        self.__setup_logging(default_path=logger_path)
        self.logger = logging.getLogger("arquitecture")
        self.logger.info("conf de logger obtenida de '%s'",logger_path)
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
        else:
            print("Se inicializa el logger por defecto")
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

        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))

        conf_path = path.join(self.parent_path, "resources/arq_conf.cfg")
        self.logger.info("conf general obtenida de '%s'",conf_path)
        self.confMap = configparser.ConfigParser()
        self.confMap.read(conf_path)
        self.logger.debug("-"*20)
        {section: self.logger.debug("Sección: %s",json.dumps(dict(self.confMap[section]))) for section in self.confMap.sections()}
        self.logger.debug("-"*20)
        self.logger.info("FIN - servicio de Configuración")
    
    def getProperty(self, group, key):
        """
        Obtener propiedad en función del grupo y la clave
        """
        if group in self.confMap:
            if key in self.confMap[group]:
                return self.confMap[group][key]
            else:
                self.logger.error("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.logger.error("El grupo '%s' no está definido en configuración", group)
            return None
    
    def getPropertyDefault(self, group, key, defaultValue):
        """
        Obtener propiedad en función del grupo y la clave.
        En caso de no existir, define un valor por defecto
        """
        propertyValue = self.getProperty(group,key)
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
    
    def __filterTheDict(self, dictObj, callback):
        newDict = dict()
        # Itera sobnrte todos los elementos del diccionario
        for (key, value) in dictObj.items():
            # Comprueba si satisface la condición del parámetro para añadir al diccionario
            if callback(key):
                newDict[key] = value
        return newDict

class LogThisTestCase(type):

    def __new__(cls, name, bases, dct):
        # if the TestCase already provides setUp, wrap it
        if 'setUp' in dct:
            setUp = dct['setUp']
        else:
            setUp = lambda self: None
            print ("creating setUp...")

        def wrappedSetUp(self):
            # for hdlr in self.logger.handlers:
            #    self.logger.removeHandler(hdlr)
            self.hdlr = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(self.hdlr)
            setUp(self)
        dct['setUp'] = wrappedSetUp

        # same for tearDown
        if 'tearDown' in dct:
            tearDown = dct['tearDown']
        else:
            tearDown = lambda self: None

        def wrappedTearDown(self):
            tearDown(self)
            self.logger.removeHandler(self.hdlr)
        dct['tearDown'] = wrappedTearDown

        # return the class instance with the replaced setUp/tearDown
        return type.__new__(cls, name, bases, dct)

class LoggedTestCase(unittest.TestCase):
    __metaclass__ = LogThisTestCase
    logger = Logger().testingLogger()

    def test_list_int(self):
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

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

