# system
import sys, os
import pathlib
# IoC
from dependency_injector import containers, providers
from arq_server.services.CoreService import CoreService

class FileSystemTools(object):
    def __init__(self,core, *args, **kwargs):
        self.__init_services(core)

    def __init_services(self, core):
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()

    def getDirectoryTree(self,dirPath):
        dirTree =  {}
        self.logger.debug("Ruta a recorrer para obtener su información: %s",dirPath)
        for (path, dirs, files) in os.walk(dirPath):
            dirTree[path] = {}
            dirTree[path]["dirs"] = dirs
            dirTree[path]["files"] = files
        return dirTree

class OSService(containers.DeclarativeContainer):
    """Application IoC container."""

    # Services
    file_system_tools = providers.Singleton(
        FileSystemTools,
        core=providers.Singleton(CoreService)
    )