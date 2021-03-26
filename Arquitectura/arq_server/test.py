#!/usr/bin/env python

import os
import time

from flask import make_response, jsonify
# Own
from arq_decorators.arq_decorator import ArqToolsTemplate


class MiApp(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.__init_app_test()
        
    def dashPrueba(self):
        """
        components = []
        alert = self.dashTools.alert("alerta desde megocio","nuevo-id",color="primary", is_open=True, dismissable=True)
        components.append(alert)
        figure = self.stadisticsTools.generate_figure()
        dashFigure = self.dashTools.plotly_graph(figure)
        components.append(dashFigure)
        """
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

class AWSPrueba(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)

if __name__ == "__main__":
    prueba = AWSPrueba()