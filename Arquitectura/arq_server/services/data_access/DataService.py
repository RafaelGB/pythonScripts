# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.CoreService import CoreService
from arq_server.services.data_access.CacheTools  import RedisTools


    
class DataService(containers.DeclarativeContainer):
    """Application IoC container."""

    # Services
    cache_tools = providers.Singleton(
        RedisTools,
        core=providers.Singleton(CoreService)
    )