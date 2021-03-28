# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.protocols.physical.PhysicalService import PhysicalService
from arq_server.services.protocols.logical.LogicalService import LogicalService

class ProtocolsService(containers.DeclarativeContainer):
  core = providers.Dependency()
  
  logical_protocol_services = providers.Singleton(
    LogicalService,
    core=core
  )

  physical_protocol_services = providers.Singleton(
    PhysicalService,
    core=core,
    logical=logical_protocol_services
  )

  