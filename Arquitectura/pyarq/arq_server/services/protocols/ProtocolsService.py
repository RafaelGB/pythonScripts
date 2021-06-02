# IoC
from dependency_injector import containers, providers
# own
from pyarq.arq_server.services.protocols.physical.PhysicalService import PhysicalService
from pyarq.arq_server.services.protocols.logical.LogicalService import LogicalService

class ProtocolsService(containers.DeclarativeContainer):
  core = providers.Dependency()
  cross = providers.Dependency()
  
  logical_protocol_services = providers.Singleton(
    LogicalService,
    core=core,
    cross=cross
  )

  physical_protocol_services = providers.Singleton(
    PhysicalService,
    core=core,
    logical=logical_protocol_services
  )

  