# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.support.ParseArgsTools import ParseArgsTools
from arq_server.services.CoreService import CoreService
from arq_server.services.CoreService import Configuration


    
class UtilsService(containers.DeclarativeContainer):
    """Application IoC container."""

    # Services
    file_system_tools = providers.Singleton(
        FileSystemTools,
        core=providers.Singleton(CoreService)
    )
    parse_args_tools = providers.Singleton(
        ParseArgsTools,
        core=providers.Singleton(CoreService)
    )