"""Example of dependency injection in Python."""
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.data_access.DataService import DataService
from arq_server.services.support.UtilsService import UtilsService
from arq_server.services.protocols.ProtocolsService import ProtocolsService

class TestingContainer(containers.DeclarativeContainer):
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
    
    

