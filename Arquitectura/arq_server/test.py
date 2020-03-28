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

        self.setDictOnCache("myTree", dirTree,volatile=True,timeToExpire=10)

    def __test_cacheArq(self):
        """TEST orientado a cache"""
        key = "testKey"
        value = "testValue"
        try:
            self.cacheTools.setVal(key, value, volatile=True, timeToExpire=5)
            exist = self.cacheTools.existKey(key)
            assert exist
        except Exception as e:
            self.__logger_test.error("error en test de Cache: ",e)
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
    prueba.dockerTools.runContainer(
        "custom/redis:1.0.0",
        "my-redis",
        auto_remove=True,
        detach=True,
        command="redis-server --appendonly yes",
        ports={"6379/tcp":"6379"},
        volumes={'redis-persist': {'bind': '/data', 'mode': 'rw'}})

    prueba.run_own_test()
    prueba.dockerTools.removeContainer("my-redis")
    prueba2 = MiApp2()
    prueba2.run_own_test()
