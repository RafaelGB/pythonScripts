#!/usr/bin/env python
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import json
"""
import json
import os
import pathlib
import sys

import random
import time

from arq_decorators.arq_decorator import ArqToolsTemplate, arq_decorator
# own
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

    def lanzaProcesoPesado(self,iter):
        self.centinel = 0
        args = 1, 2, 3
        self.dockerTools.runContainer(
            "custom/redis:1.0.0",
            "my-redis",
            auto_remove=True,
            detach=True,
            command="redis-server --appendonly yes",
            ports={"6379/tcp": "6379"},
            volumes={'redis-persist': {'bind': '/data', 'mode': 'rw'}})

        def __on_next(key, result):
            self.cacheTools.setVal(key, result, volatile=True, timeToExpire=30)

        def __on_complete(iter):
            self.centinel = self.centinel+1
            self.logger.info("procesos acabados %d de %d", self.centinel,iter)
            if self.centinel >= iter:
                self.logger.info("ejemplo en cache: %s",
                                 self.cacheTools.getVal("9"))
                self.dockerTools.removeContainer("my-redis")
                del self.centinel

        def __procesoPesado(arg):
            time.sleep(2)
            arg = arg*2
            return arg

        for i in range(iter):
            self.concurrentTools.createProcess(
                __procesoPesado,
                *args,
                on_next=lambda next: __on_next(str(i), next),
                on_completed=lambda: __on_complete(iter)
            )

        self.logger.info("Lanzando los procesos en paralelo")

    def dashPrueba(self):
        self.stadisticsTools.pruebas()
    """
    APARTADO DE TESTING
    """
    def __test_cacheArq(self):
        """TEST orientado a cache"""
        key = "testKey"
        value = "testValue"
        try:
            self.cacheTools.setVal(key, value, volatile=True, timeToExpire=5)
            exist = self.cacheTools.existKey(key)
            assert exist
        except Exception as e:
            self.logger.error("error en test de Cache: %s", e)
            assert False

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


if __name__ == "__main__":
    prueba = MiApp()
    #prueba.lanzaProcesoPesado(12)
    prueba.dashPrueba()
    prueba2 = MiApp2()
    prueba2.run_own_test()
