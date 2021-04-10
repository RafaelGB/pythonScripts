#!/usr/bin/env python
# Typing
from typing import List
import os
import time

from flask import make_response, jsonify
# Own
from arq_decorators.arq_decorator import ArqToolsTemplate

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

    def __init_app_test(self):
        for attr in dir(self):
            test = getattr(self, attr)
            if attr.startswith("_{}__{}".format(
                    self.__class__.__name__, "test")) and callable(test):
                self.add_test(test)

class SQLPrueba(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
    def prueba(self):
        self.sqlTools.open_session()
        adminUser = User("RafaelGB","password")
        self.sqlTools.add_item(adminUser)
        self.sqlTools.commit_current_session()

if __name__ == "__main__":
    prueba = SQLPrueba()
    #prueba.prueba()
