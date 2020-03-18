# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

# filesystem
import configparser
import logging
import sys

# metadata
from typing import TypeVar
import types
# metrics 
from datetime import datetime

# own
from arq_server.containers.ArqContainer import ArqContainer
from arq_server.services.CoreService import Configuration
from arq_server.services.OSService import FileSystemTools

def method_wrapper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger = ArqContainer.core_service().logger_service().arqLogger()
        logger.debug("INI - funcion '%s'",function.__name__)
        before = datetime.now()  
        result = function(*args, **kwargs)
        after = datetime.now()
        logger.debug("FIN - funcion '%s' - tiempo empleado: %s ms",function.__name__,(after-before).total_seconds() * 1000)
        return result
    return wrapper

def arq_decorator(Cls):
    class NewApp(object):
        
        def __init__(self,*args,**kwargs):
            self.__tools_init()
            self.__logger.info("INI - arranque decorador de la clase %a",Cls.__name__)
            args, kwargs = self.__set_arq_attributes(*args,**kwargs)
            self.wrapped = Cls(*args, **kwargs)
            self.__logger.info("FIN - arranque decorador de la clase %a",Cls.__name__)

        def __getattribute__(self,attr):
            """
            esta función es invocada cada vez que se accede a cualquier atributo de la clase decoradora. 
            En primer lugar intenta obtener el atributo de NewCls. Si falla, intenta obtener el 
            atributo de self.oInstance (un instancia de la clase decorada).
            """
            try:
                x = super(NewApp,self).__getattribute__(attr)
            except (AttributeError, TypeError) as e:      
                pass
            else:
                return x
            
            x = self.wrapped.__getattribute__(attr)
            if type(x) == types.MethodType:
                x = method_wrapper(x)
            return x

        def __run_test(self, test):
            self.__before_call(test)
            try:
                return test(self)
            finally:
                self.__after_call(test)

        def __before_call(self, func):
            """
            Pre-acciones para una función
            """
            self.__logger.info('INI - %s', func.__name__)

        def __after_call(self, func):
            """
            Post-acciones para una función
            """
            self.__logger.info('FIN - %s', func.__name__)

        def __tools_init(self):
            try:
                # CORE
                self.__logger = ArqContainer.core_service().logger_service().arqLogger()
                self.__config = ArqContainer.core_service().config_service()
                # SERVICES
                self.__protocols = ArqContainer.protocols_service()
            except Exception as err:
                self.logger.error(err)
            

        def __set_arq_attributes(self,*args, **kwargs):
            if "logger" not in kwargs:
                    kwargs['logger'] = self.__logger
            if "config" not in kwargs:
                kwargs['config'] = self.__config
            if "os_tools" not in kwargs:
                kwargs['os_tools'] = ArqContainer.os_service().file_system_tools()
            return args, kwargs
    return NewApp


@arq_decorator
class ArqToolsTemplate:
    # TYPE HINTS TEMPLATE
    __logger: logging.getLogger()
    __config: Configuration
    __protocols: ArqContainer.protocols_service()
    __os_tools: FileSystemTools
    # TYPE HINTS APP
    logger: logging.getLogger()

    def __init__(self, app_name, *args,**kwargs):
        self.app_name: str = app_name
        self.__init_kwargs_attrs(*args,**kwargs)
        
    """
    --------------
    CORE Functions
    --------------
    """
    def getProperty(self, property_key) -> str:
        return self.__config.getProperty(self.app_name, property_key)

    def getPropertyDefault(self, property_key: str, default: str) -> str:
        return self.__config.getPropertyDefault(self.app_name, property_key, default)

    def getDirectoryTree(self,dirPath):
        return self.__os_tools.getDirectoryTree(dirPath)

    """
    ------------------
    Internal Functions
    ------------------
    """
    def __init_kwargs_attrs(self,*args,**kwargs):
        for key, value in kwargs.items():
            # Valores privados propios de la clase plantilla
            self.__dict__["_{}__{}".format(self.__class__.__name__, key)] = value
        # Valores privados añadidos a la aplicación
        self.__dict__["{}".format("logger")] = ArqContainer.core_service().logger_service().appLogger()
        self.__logger.debug("Atributos disponibles en la clase: %s",self.__dict__)
