# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.data_access.relational.DatabaseSQL import DbSQL

class RelationalService(containers.DeclarativeContainer):
    """Application IoC container."""
    core = providers.Dependency()
    # Services
    db_sql = providers.Singleton(
        DbSQL,
        core=core
    )