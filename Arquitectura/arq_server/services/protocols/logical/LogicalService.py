# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.protocols.logical.NormalizeSelector import NormalizeSelector

class LogicalService(containers.DeclarativeContainer):
  core = providers.Dependency()

  normalize_selector_service = providers.Singleton(
        NormalizeSelector,
        core=core
    )
