"""Example of dependency injection in Python."""
# Base
import os
import sys
# Dependecies
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
# Support
from arq_server.services.support.UtilsService import UtilsService
# data access
from arq_server.services.data_access.DataService import DataService
# Analytics
from arq_server.services.analytics.AnalyticService import AnalyticService,AnalyticServerFactory
# Protocols
from arq_server.services.protocols.ProtocolsService import ProtocolsService

class ArqContainer(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    # Base
    core_service = providers.Singleton(CoreService,config=config.core)
    # Factories
    #analytic_factories = AnalyticServerFactory(core=core_service)
    # Info
    data_service = providers.Singleton(DataService,core=core_service,config=config.data)
    # Cross
    utils_service = providers.Singleton(UtilsService,core=core_service,data=data_service)
    # Services
    #analytic_service = AnalyticService(core=core_service,factories=analytic_factories)
    # Protocols
    protocols_service = providers.Singleton(ProtocolsService,core=core_service,cross=utils_service)
    

class BaseContainerDecorator(object):
    _container:ArqContainer

    def __init__(self,**kwargs):
        config_path = os.environ['config_path_file']
        self._container:ArqContainer = ArqContainer()
        self._container.init_resources()
        self._container.config.from_yaml(config_path,required=True)
        self._container.wire(modules=[sys.modules[__name__]])


