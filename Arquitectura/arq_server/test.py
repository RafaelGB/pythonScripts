#!/usr/bin/env python
# Typing
from typing import List
import os
import time

from flask import make_response, jsonify
# Own
from arq_decorators.arq_decorator import ArqToolsTemplate

from arq_server.services.CoreService import Base
from arq_server.services.data_access.relational.models.Client import Client
from arq_server.services.data_access.relational.models.User import User

class MiApp(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.__init_app_test()
        
    def dashPrueba(self):
        self.stadisticsTools.createDashServer(None,None)
    
    def __test_lanzaProcesoPesado(self):
        try:
            iter = 24
            self.centinel = 0
            self.test_isOK = False
            args = 3,6

            def __on_next(result):
                self.logger.debug("Resultado: %s",result)
                

            def __on_complete(iter):
                self.centinel = self.centinel+1
                self.logger.debug("procesos acabados %d de %d", self.centinel,iter)
                if self.centinel >= iter:
                    self.test_isOK = True

            def __procesoPesado(arg):
                time.sleep(1)
                arg = arg*2
                return arg

            for i in range(iter):
                
                self.concurrentTools.createProcess(
                    __procesoPesado,
                    *args,
                    on_next=lambda next: __on_next(next),
                    on_completed=lambda: __on_complete(iter)
                )

            self.logger.info("Lanzando los procesos en paralelo")
            # Check sobre funcionamiento correcto
            timeout = 0
            while not self.test_isOK and timeout<10:
                time.sleep(1)
                timeout= timeout+1
            assert self.test_isOK
        except:
            assert False
        finally:
            del self.test_isOK
            del self.centinel

class SQLPrueba(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        
    def prueba(self):
        self.logger.info("primera clase!")

    def proceso(self):
        try:
            iter = 24
            self.centinel = 0
            self.test_isOK = False
            args = 3,6

            def __procesoPesado(arg):
                time.sleep(1)
                arg = arg*2
                return arg

            for i in range(iter):
                
                self.concurrentTools.createProcess(
                    __procesoPesado,
                    *args
                )

            self.logger.info("Lanzando los procesos en paralelo")
            # Check sobre funcionamiento correcto
            timeout = 0
            while not self.test_isOK and timeout<10:
                time.sleep(1)
                timeout= timeout+1
        except:
            assert False
        finally:
            del self.test_isOK
            del self.centinel

class Calculadora(ArqToolsTemplate,Base):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.expose_app(self)
        
    def sum(self,a,b,**kwargs):
        return a+b
        

if __name__ == "__main__":
    prueba = SQLPrueba()
    prueba.proceso()
    prueba2 = Calculadora()