#!/usr/bin/env python

import os
import time

from flask import make_response, jsonify
# Own
from arq_decorators.arq_decorator import ArqToolsTemplate, arq_decorator
from arq_server.containers.ArqContainer import ArqContainer


class MiApp(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.__init_app_test()

    def getOwnDirTree(self):
        dirTree = self.getDirectoryTree(
            os.path.dirname(os.path.abspath(__file__)))

        self.setDictOnCache("myTree", dirTree, volatile=True, timeToExpire=10)


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
    """
    APARTADO DE TESTING
    """
    def __test_cacheArq(self):
        """TEST orientado a cache"""
        self.dockerTools.runContainer(
                "custom/redis:1.0.0",
                "my-redis",
                auto_remove=True,
                detach=True,
                command="redis-server --appendonly yes",
                ports={"6379/tcp": "6379"},
                volumes={'redis-persist': {'bind': '/data', 'mode': 'rw'}})
        key = "testKey"
        value = "testValue"
        try:
            self.cacheTools.setVal(key, value, volatile=True, timeToExpire=5)
            exist = self.cacheTools.existKey(key)
            self.logger.debug("Comprobación sobre clave guardada:%s",exist)
            assert exist
        except Exception as e:
            self.logger.error("error en test de Cache: %s", e)
            assert False
        finally:
            self.dockerTools.removeContainer("my-redis")

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


class MiApp2(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error

    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.__init_app_test()

    def __test_own(self):
        assert "a" == "a"

    def __init_app_test(self):
        for attr in dir(self):
            test = getattr(self, attr)
            if attr.startswith("_{}__{}".format(
                    self.__class__.__name__, "test")) and callable(test):
                self.add_test(test)

def responsePrueba():
    return make_response(jsonify("esto es una prueba"),200)

class RestApp(ArqToolsTemplate):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)

    def initRestAPI(self):
        self.restTools.addUrlRule("/ruta/programatica",customFunc=responsePrueba)
        self.restTools.start_server()

if __name__ == "__main__":
    prueba = RestApp()
    prueba.initRestAPI()