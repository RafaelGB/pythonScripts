# IoC
from dependency_injector import containers, providers
# Own
from .OSTools import FileSystemTools
from .DockerTools import DockerTools
from .ConcurrentTools import ConcurrentTools
from .SecurityTools import Security

class UtilsService(containers.DeclarativeContainer):
    """Application IoC container."""
    # Dependencies
    core = providers.Dependency()
    data = providers.Dependency()
    # Services
    file_system_tools = providers.Singleton(
        FileSystemTools,
        core=core
    )

    docker_tools  = providers.Singleton(
        DockerTools,
        core=core
    )

    concurrent_tools = providers.Singleton(
        ConcurrentTools,
        core=core
    )

    security_tools = providers.Singleton(
        Security,
        core=core,
        data=data
    )