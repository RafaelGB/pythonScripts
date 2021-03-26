# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.protocols.physical.PhysicalService import PhysicalService

class ProtocolsService(containers.DeclarativeContainer):
  core = providers.Dependency()
  physical_protocol_services = providers.Singleton(
    PhysicalService,
    core=core
  )