# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.protocols.rest.RestService import FlaskFunctions

class ProtocolsService(containers.DeclarativeContainer):
      core = providers.Dependency()
      rest_service = providers.Singleton(
        FlaskFunctions,
        core=core
    )