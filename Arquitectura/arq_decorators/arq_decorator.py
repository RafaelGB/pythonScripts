# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

import configparser
import logging
import sys
# own
from arq_server.containers.ArqContainer import ArqContainer
class arq_decorator():
    def __init__(self, *a, **kw):
        self.dec_args = a
        self.dec_kw = kw
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__))).parent

        if not self.__core_init():
            raise Exception("Error durante la inicialización de funcionalidades básicas, revisar logs y/o consola")
        if not self.__services_init():
            raise Exception("Error durante la inicialización de los servicios de arquitectura, revisar logs y/o consola")

    def __call__(self, class_or_fun):
        # self.func = func
        if isclass(class_or_fun):
            self.logger.info('Arranque de la clase "%s"',class_or_fun.__name__)
    
            setattr(class_or_fun, "logger", self.logger)
            setattr(class_or_fun, "config", self.config)

            for attr in class_or_fun.__dict__.keys():
                
                test = getattr(class_or_fun, attr)
                if attr.startswith('test_') and callable(test):
                    self.logger.info('Lanzando test de arranque "%s"',attr)  
                    isCorrect = self.run_test(test)
                    if not isCorrect:
                        raise Exception("Error ejecutanto el test {}".format(attr))
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

    def __before_call(self,func):
        """
        Pre-acciones para una función
        """
        self.logger.info('INI - %s',func.__name__)

    def __after_call(self,func):
        """
        Post-acciones para una función
        """
        self.logger.info('FIN - %s',func.__name__)  

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
        
        