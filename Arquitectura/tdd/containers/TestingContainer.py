"""Example of dependency injection in Python."""
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.data_access.DataService import DataService

class TestingContainer(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()

    # Base
    core_service = providers.Singleton(CoreService,config=config.core)

    # Utils
    data_service = DataService(core=core_service,config=config.data)
    
    

