# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path

import configparser
import logging
from logging.config import fileConfig

# Librerias de terceros
import shutil

class architecture_Decorator():
    def __init__(self, *a, **kw):
        self.dec_args = a
        self.dec_kw = kw
        self.cache = {}

        self.__logger_init()
        self.__conf_init()
       
    def __call__(self, class_or_fun):
        # self.func = func
        if isclass(class_or_fun):
            self.logger.info('Arranque de la clase "%s"',class_or_fun.__name__)
    
            setattr(class_or_fun, "logger", self.logger)
            setattr(class_or_fun, "confMap", self.confMap)

            for attr in class_or_fun.__dict__.keys():
                
                test = getattr(class_or_fun, attr)
                if attr.startswith('test_') and callable(test):
                    self.logger.info('Lanzando test de arranque "%s"',attr)  
                    isCorrect = self.run_test(test)
                    if not isCorrect:
                        raise Exception("Error ejecutanto el test {}".format(attr))
            return class_or_fun
        else:
            print("decorando una funcion")
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

    def __logger_init(self):
        # Create a custom logger
        parent_path = Path(path.dirname(path.abspath(__file__))).parent.parent
        print(parent_path)
        log_file_path = path.join(parent_path,'resources\\logging_conf.ini')
        print(log_file_path)
        fileConfig(fname=log_file_path, disable_existing_loggers=False)
        self.logger = logging.getLogger("access")

    def __conf_init(self):
        self.logger.info('preprocesando configuración: %s - %s', self.dec_args, self.dec_kw)
        
        if "conf_filename" in self.dec_kw:
            self.confMap = configparser.ConfigParser()
            self.confMap.read(self.dec_kw["conf_filename"])
            return True
        else:
            self.logger.error("No se ha determinado ningún fichero de configuración")
            return False
        