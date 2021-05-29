# system
import sys, os
import pathlib
import logging
# IoC
from arq_server.services.CoreService import Configuration

class FileSystemTools(object):
    __logger: logging.Logger
    __config: Configuration

    def __init__(self,core, *args, **kwargs):
        self.__init_services(core)
        self.__logger.info("Herramientas sistema de fichero arrancado correctamente")

    def getDirectoryTree(self,dirPath) -> dict:
        """
        Dada una ruta a un directorio del fileSystem, devuelve un diccionario con la información de su contenido,
        incluyendo los directorios anidados
        """
        dirTree =  {}
        self.__logger.debug("Ruta a recorrer para obtener su información: %s",dirPath)
        for (path, dirs, files) in os.walk(dirPath):
            dirTree[path] = {}
            dirTree[path]["dirs"] = dirs
            dirTree[path]["files"] = files
        return dirTree

    def modifyValuesOnDict(self, a_dict:dict, k:str, subst_dict:dict) -> None:
        """
        dado un diccionario 'referencia', una clave y un diccionario 'variables' (clave-valor), modifica, en todos los niveles
        del diccionario base donde se encuentre la clave, su valor asociado en caso de que dicho valor contenga alguna de las
        variables especificadas en el diccionario 'variables' con el formato {{variable}},siendo sustituída por el valor referenciado.

        i.e.: {
            "clave1":"valor1",
            "clave2":
                {
                    "clave_buscada":"esta clave contiene {{variable}}"
                }
            }
        """
        for key in a_dict.keys():
            if key == k:
                for s_k, s_v in subst_dict.items():
                    a_dict[key] = a_dict[key].replace("{{"+s_k+"}}",s_v)
            elif type(a_dict[key]) is dict:
                self.modifyValuesOnDict(a_dict[key], k, subst_dict)
    
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()