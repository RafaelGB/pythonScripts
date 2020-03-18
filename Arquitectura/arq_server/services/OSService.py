# IoC
from dependency_injector import containers, providers

from arq_server.services.CoreService import CoreService

class FileSystemTools(object):
    def __init__(self,core, *args, **kwargs)
        self.__init_services(core)

    def __init_services(self, core):
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()

class OSService(containers.DeclarativeContainer):
    """Application IoC container."""

    # Services
    file_system_tools = providers.Singleton(
        FileSystemTools,
        core=providers.Singleton(CoreService)
    )