from tkinter import Tk,Label
from tkinter.filedialog import askopenfilename

from functools import wraps
from inspect import isclass

import configparser
import logging
from logging.config import fileConfig

class PanelDecorator:
    def __init__(self, *a, **kw):
        self.dec_args = a
        self.dec_kw = kw
        self.__logger_init()
        self.__conf_init()
        self.cache = {}
        # self.func  = None
       
    def __call__(self, class_or_fun):
        # self.func = func
        if isclass(class_or_fun):
            class_or_fun.self = self
            self.logger.info('Decorando clase - (%s) para ejecutar test de prueba',class_or_fun.__name__)  
            for attr in class_or_fun.__dict__.keys():
                val = getattr(class_or_fun, attr)
                if attr.startswith('test_') and callable(val):
                    setattr(class_or_fun, attr, self.decorate(val))
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
        fileConfig(fname='../resources/logging_conf.ini', disable_existing_loggers=False)
        self.logger = logging.getLogger("access")

    def __conf_init(self):
        self.logger.info('preprocesando configuración: %s - %s', self.dec_args, self.dec_kw)
        
        if "conf_filename" in self.dec_kw:
            self.conf = configparser.ConfigParser()
            self.conf.read(self.dec_kw["conf_filename"])
            return "OK"
        else:
            self.logger.error("No se ha determinado ningún fichero de configuración")
            return "KO"
        # Preprocesado de argumentos diccionario