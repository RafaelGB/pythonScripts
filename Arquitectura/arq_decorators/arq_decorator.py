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

def decorating_meta(decorator):
    class DecoratingMetaclass(type):
        def __new__(self, class_name, bases, namespace):
            for key, value in list(namespace.items()):
                if callable(value):
                    namespace[key] = decorator(value)

            return type.__new__(self, class_name, bases, namespace)

    return DecoratingMetaclass

def own_wrapper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger = ArqContainer.core_service().logger_service().appLogger()
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
            self.logger.info("INI - decorador de la clase %a",Cls.__name__)
            self.dec_args = args
            self.dec_kwargs = kwargs
            self.parent_path = Path(path.dirname(
                path.abspath(sys.modules['__main__'].__file__))).parent

            self.__set_arq_attributes(Cls)
            self.oInstance = Cls(*args,**kwargs)
            self.logger.info("FIN - decorador de la clase %a",Cls.__name__)

        def __getattribute__(self,s):
            """
            esta función es invocada cada vez que se accede a cualquier atributo de la clase decoradora. 
            En primer lugar intenta obtener el atributo de NewCls. Si falla, intenta obtener el 
            atributo de self.oInstance (un instancia de la clase decorada).
            """
            try:    
                x = super(NewApp,self).__getattribute__(s)
            except AttributeError:      
                pass
            else:
                return x
            x = self.oInstance.__getattribute__(s)
            if type(x) == types.MethodType:
                x = own_wrapper(x)
            return x

        def run_test(self, test):
            self.__before_call(test)
            try:
                return test(self)
            finally:
                self.__after_call(test)

        def __before_call(self, func):
            """
            Pre-acciones para una función
            """
            self.logger.info('INI - %s', func.__name__)

        def __after_call(self, func):
            """
            Post-acciones para una función
            """
            self.logger.info('FIN - %s', func.__name__)

        def __tools_init(self):
            try:
                # CORE
                self.logger = ArqContainer.core_service().logger_service().appLogger()
                self.config = ArqContainer.core_service().config_service()
                # SERVICES
                self.protocols = ArqContainer.protocols_service()
                return True
            except Exception as err:
                self.logger.error(err)
                return False

        def __set_arq_attributes(self,Cls):
            """
            for attr in Cls.__dict__: # there's propably a better way to do this
                if callable(getattr(Cls, attr)):
                    setattr(Cls, attr, time_this(getattr(Cls, attr)))
            """
            setattr(Cls, "logger", self.logger)
            setattr(Cls, "config", self.config)
    return NewApp


@arq_decorator
class ArqToolsTemplate:
    logger: logging.getLogger()
    config: Configuration
    __protocols: ArqContainer.protocols_service()

    def __init__(self, app_name):
        self.app_name: str = app_name
        self.__config = self.config
        self.__remove_references()
    """
    --------------
    CORE Functions
    --------------
    """
    def getProperty(self, property_key) -> str:
        return self.__config.getProperty(self.app_name, property_key)

    def getPropertyDefault(self, property_key: str, default: str) -> str:
        return self.__config.getPropertyDefault(self.app_name, property_key, default)

    """
    ------------------
    Internal Functions
    ------------------
    """
    def __remove_references(self):
        self.config = None
        del self.config
