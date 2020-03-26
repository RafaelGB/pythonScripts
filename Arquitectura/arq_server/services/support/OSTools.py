# system
import sys, os
import pathlib
import logging
# IoC
from arq_server.services.CoreService import Configuration

class FileSystemTools(object):
    logger: logging.getLogger()
    config: Configuration

    def __init__(self,core, *args, **kwargs):
        self.__init_services(core)
        self.logger.info("Herramientas sistema de fichero arrancado correctamente")

    def getDirectoryTree(self,dirPath) -> dict:
        """
        Dada una ruta, devuelve un diccionario con el arbol de archivos de dicha ruta
        """
        dirTree =  {}
        self.logger.debug("Ruta a recorrer para obtener su información: %s",dirPath)
        for (path, dirs, files) in os.walk(dirPath):
            dirTree[path] = {}
            dirTree[path]["dirs"] = dirs
            dirTree[path]["files"] = files
        return dirTree

    def modifyValuesOnDict(self, a_dict:dict, k:str, subst_dict:dict) -> None:
        # -*- coding: utf-8 -*-
        """Modifica de un diccionario (por referencia) valores de una clave en concreto en todos los niveles

        Dado un diccionario a recorrer, la clave a buscar y una serie de clave-valor. Modifica
        posibles variables en los valores de la clave.

        Las variables deben estar entree llaves del modo '{{variable}}'
        """
        for key in a_dict.keys():
            if key == k:
                for s_k, s_v in subst_dict.items():
                    a_dict[key] = a_dict[key].replace("{{"+s_k+"}}",s_v)
            elif type(a_dict[key]) is dict:
                self.modifyValuesOnDict(a_dict[key], k, subst_dict)
    
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()