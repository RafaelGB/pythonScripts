# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

import configparser
import logging
import sys
# metadata
from typing import TypeVar
# own
from arq_server.containers.ArqContainer import ArqContainer
from arq_server.services.CoreService import Configuration

def time_this(original_function):
    print ("decorating")
    def new_function(*args,**kwargs):
        print ("starting timer")
        import datetime
        before = datetime.datetime.now()                     
        x = original_function(*args,**kwargs)         
        after = datetime.datetime.now()                      
        print ("Elapsed Time = {0}".format(after-before))
        return x
    return new_function

def time_all_class_methods(Cls):
    class NewCls(object):
        def __init__(self,*args,**kwargs):
            self.oInstance = Cls(*args,**kwargs)
        def __getattribute__(self,s):
            """
            this is called whenever any attribute of a NewCls object is accessed. This function first tries to 
            get the attribute off NewCls. If it fails then it tries to fetch the attribute from self.oInstance (an
            instance of the decorated class). If it manages to fetch the attribute from self.oInstance, and 
            the attribute is an instance method then `time_this` is applied.
            """
            try:    
                x = super(NewCls,self).__getattribute__(s)
            except AttributeError:      
                pass
            else:
                return x
            x = self.oInstance.__getattribute__(s)
            if type(x) == type(self.__init__): # it is an instance method
                return time_this(x)                 # this is equivalent of just decorating the method with time_this
            else:
                return x
    return NewCls

class arq_decorator():
    def __init__(self, *a, **kw):
        self.dec_args = a
        self.dec_kw = kw
        self.parent_path = Path(path.dirname(
            path.abspath(sys.modules['__main__'].__file__))).parent

        if not self.__core_init():
            raise Exception(
                "Error durante la inicialización de funcionalidades básicas, revisar logs y/o consola")
        if not self.__services_init():
            raise Exception(
                "Error durante la inicialización de los servicios de arquitectura, revisar logs y/o consola")

    def __call__(self, class_or_fun:object):
        # self.func = func
        if isclass(class_or_fun):
            self.logger.info('Arranque de la clase "%s"',
                             class_or_fun.__name__)

            self.__set_arq_attributes(class_or_fun)

            for attr in class_or_fun.__dict__.keys():

                test = getattr(class_or_fun, attr)
                if attr.startswith('test_') and callable(test):
                    self.logger.info('Lanzando test de arranque "%s"', attr)
                    isCorrect = self.run_test(test)
                    if not isCorrect:
                        raise Exception(
                            "Error ejecutanto el test {}".format(attr))
            return class_or_fun
        else:
            return self.decorate(class_or_fun)

    def decorate(self, func):
        @wraps(func)
        def _inner(*args, **kwargs):
            self.__before_call(func)
            try:
                return func(*args, **kwargs)
            finally:
                self.__after_call(func)
        return _inner

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

    def __core_init(self):
        try:
            self.logger = ArqContainer.core_service().logger_service().appLogger()
            self.config = ArqContainer.core_service().config_service()
            return True
        except Exception as err:
            self.logger.error(err)
            return False

    def __services_init(self):
        try:
            self.protocols = ArqContainer.protocols_service()
            return True
        except Exception as err:
            self.logger.error(err)
            return False

    def __set_arq_attributes(self,class_or_fun):
        setattr(class_or_fun, "logger", self.logger)
        setattr(class_or_fun, "config", self.config)

@arq_decorator()
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
