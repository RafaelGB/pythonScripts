# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.protocols.physical.rest.RestService import APIRestTools

class PhysicalService(containers.DeclarativeContainer):
  core = providers.Dependency()
  rest_protocol_tools = providers.Singleton(
    APIRestTools,
    core=core
  )