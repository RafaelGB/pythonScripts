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
        self.actions_on_init()

    def test__showOwnDirTree(self):
        dirTree = self.getDirectoryTree(
            os.path.dirname(os.path.abspath(__file__)))
        self.__init_app_test()
        
    def __test__propioMiApp(self):
        assert "aa" == "aa"

    def __init_app_test(self):
        for attr in dir(self):
            test = getattr(self, attr)
            if attr.startswith("_{}__{}".format(
                    self.__class__.__name__, "test")) and callable(test):
                self.add_test(test)

if __name__ == "__main__":

    prueba = MiApp()
    
    
    # ArqContainer.protocols_service().rest_service().start_server()

    # app.run(debug=True)
