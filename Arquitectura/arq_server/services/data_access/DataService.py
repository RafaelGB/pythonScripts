# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.data_access.CacheTools  import RedisTools
from arq_server.services.data_access.relational.RelationalService import RelationalService

class DataService(containers.DeclarativeContainer):
    """Application IoC container."""
    # Configuration
    config = providers.Configuration()
    
    core = providers.Dependency()
    # Services
    cache_tools = providers.Singleton(
        RedisTools,
        core=core,
        config=config.redis
    )

    relational_tools = providers.Singleton(
        RelationalService,
        core=core
    )