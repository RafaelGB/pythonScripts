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
        a = self.getDictFromCache("myTree")
        print(a)

    def __test_own(self):
        assert "a" == "a"

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
    prueba.run_own_test()

    prueba.add_new_argument()
    prueba.show_help()
    prueba2 = MiApp2()
    prueba2.run_own_test()
