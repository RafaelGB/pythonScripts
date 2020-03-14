# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

import configparser
import logging
import sys

class arq_decorator():
    def __init__(self, *a, **kw):
        self.dec_args = a
        self.dec_kw = kw
        self.cache = {}
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__))).parent

        if not self.__conf_init():
            raise Exception("Inicialización de configuración fallida, revisar logs y/o consola")
        if not self.__logger_init():
            raise Exception("Inicialización de loggers fallida, revisar logs y/o consola")

    def __call__(self, class_or_fun):
        # self.func = func
        if isclass(class_or_fun):
            self.logger.info('Arranque de la clase "%s"',class_or_fun.__name__)
    
            setattr(class_or_fun, "logger", self.logger_func)
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

    def __conf_init(self):
        print('preprocesando configuración:', self.dec_args, self.dec_kw)
        
        if "conf_filename" in self.dec_kw:
            conf_path = path.join(self.parent_path, self.dec_kw["conf_filename"])
            print("Ruta de configuración general: ",conf_path)
            self.confMap = configparser.ConfigParser()
            self.confMap.read(conf_path)
            {section: print("Seccion:"+section,dict(self.confMap[section])) for section in self.confMap.sections()}
            return True
        else:
            print("No se ha determinado ningún fichero de configuración")
            return False

    def __logger_init(self):
        # Create a custom logger 
        if self.confMap.has_option("logger","filename") \
        and self.confMap.has_option("logger","main") \
        and self.confMap.has_option("logger","decorator"):
            log_file_path = path.join(self.parent_path,self.confMap["paths"]["resources"],self.confMap["logger"]["filename"])
            print("Ruta de configuración logging: ",log_file_path)
            fileConfig(fname=log_file_path, disable_existing_loggers=False)
            self.logger = logging.getLogger(self.confMap["logger"]["decorator"])
            self.logger_func = logging.getLogger(self.confMap["logger"]["main"])
            return True
        else:
            print("No se ha configurado correctamente el logger. Añadir filename, decorator y main en el apartado de logger en el fichero de configuración")
            return False
        
        