# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.support.DockerTools import DockerTools
from arq_server.services.support.ConcurrentTools import ConcurrentTools
from arq_server.services.support.SecurityTools import Security
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