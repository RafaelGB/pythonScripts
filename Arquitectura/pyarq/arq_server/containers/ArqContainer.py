"""Example of dependency injection in Python."""
# Base
import os
import sys
# Dependecies
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide
# own
from pyarq_core.CoreService import CoreService
# Support
from pyarq_utils.UtilsService import UtilsService
# data access
from pyarq.arq_server.services.data_access.DataService import DataService
# Protocols
from pyarq.arq_server.services.protocols.ProtocolsService import ProtocolsService

ARQ_STARTED=False

class ArqContainer(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    # Base
    core_service = providers.Singleton(CoreService,config=config.core)
    # Factories

    # Info
    data_service = providers.Singleton(DataService,core=core_service,config=config.data)
    # Cross
    utils_service = providers.Singleton(UtilsService,core=core_service,data=data_service)
    # Services

    # Protocols
    protocols_service = providers.Singleton(ProtocolsService,core=core_service,cross=utils_service)
    
@inject
def load_started_arq(startedArq:ArqContainer = Provide[ArqContainer]):
    return startedArq

class BaseContainerDecorator(object):
    _container:ArqContainer

    def __init__(self,**kwargs):
        global ARQ_STARTED
        if not ARQ_STARTED:
            config_path = os.environ['config_path_file']
            self._container:ArqContainer = ArqContainer()
            self._container.init_resources()
            self._container.config.from_yaml(config_path,required=True)
            self._container.wire(modules=[sys.modules[__name__]])
            ARQ_STARTED=True
        else:
            self._container=load_started_arq()
        
    

