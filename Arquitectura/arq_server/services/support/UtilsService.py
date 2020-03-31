# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.support.DockerTools import DockerTools
    
class UtilsService(containers.DeclarativeContainer):
    """Application IoC container."""
    # Dependencies
    core = providers.Dependency()
    # Services
    file_system_tools = providers.Singleton(
        FileSystemTools,
        core=core
    )

    docker_tools  = providers.Singleton(
        DockerTools,
        core=core
    )