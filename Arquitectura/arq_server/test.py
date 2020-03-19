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
        className = self.__class__.__name__
        super().__init__(className, *args, **kwargs)

    def showOwnDirTree(self):
        dirTree = self.getDirectoryTree(
            os.path.dirname(os.path.abspath(__file__)))
        self.logger.info(json.dumps(dirTree,  sort_keys=True, indent=4))
        
    def prueba(self):
        self.logger.info("utilizando log de la arquitectura en una clase. Propiedad '%s'",
                         self.getProperty("mi.propiedad"))


if __name__ == "__main__":

    prueba = MiApp("app_pruebas")
    prueba.prueba()

    # ArqContainer.protocols_service().rest_service().start_server()

    # app.run(debug=True)
