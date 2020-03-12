# Basic
import configparser
import logging
from logging.config import fileConfig, dictConfig
# Filesystem
from os import path, getenv
from pathlib import Path
import sys
import json
# IoC
from dependency_injector import containers, providers

class LoggerService:
    def __init__(self):
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        logger_path = path.join(self.parent_path, "resources\\logger_conf.json")
        self.__setup_logging(default_path=logger_path)
        self.logger = logging.getLogger("arquitecture")
        self.logger.info("¡servicio de logging levantado!")

    def arqLogger(self):
        """ TODO """
        return self.logger

    def __setup_logging(self,
    default_path='logging.json',
    default_level=logging.INFO):
        """
        Setup logging configuration
        """
        file_path = default_path
        print(file_path)
        if path.exists(file_path):
            with open(file_path, 'rt') as f:
                config = json.load(f)
                logging.config.dictConfig(config)
        else:
            print("Se inicializa el logger por defecto")
            logging.basicConfig(level=default_level)

class ConfigService:
    def __init__(self,logger):
        self.logger = logger.arqLogger()
        self.logger.info("INI - servicio de Configuración")

        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))

        conf_path = path.join(self.parent_path, "resources\\arq_conf.cfg")
        self.confMap = configparser.ConfigParser()
        self.confMap.read(conf_path)
        {section: print("Sección: "+section,dict(self.confMap[section])) for section in self.confMap.sections()}
        self.logger.info("FIN - servicio de Configuración")
    
    def getProperty(self, group, key):
         
        if group in self.confMap:
            if key in self.confMap[group]:
                return self.confMap[group][key]
            else:
                self.logger.error("La propiedad %s no está definida en el grupo %s en configuración",key, group)
                return None
        else:
            self.logger.error("El grupoo %s no está definido en configuración", group)
            return None
    
    def getPropertyDefault(self, group, key, defaultValue):
        propertyValue = self.getProperty(group,key)
        return (propertyValue, defaultValue)[propertyValue == None]
    
class CoreService(containers.DeclarativeContainer):
    """Application IoC container."""
    #logger = providers.Singleton(logging.Logger, name='logger')

    # Gateways

    #database_client = providers.Singleton(sqlite3.connect, config.database.dsn)

    # Services
    logger_service = providers.Factory(LoggerService)
    config_service = providers.Factory(
        ConfigService,
        logger=logger_service
    )