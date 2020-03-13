
"""Example of dependency injection in Python."""
import logging
import sqlite3
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.protocols.RestService import FlaskFunctions
from arq_server.main import main

class ArqContainer(containers.DeclarativeContainer):
    """Application IoC container."""
    #logger = providers.Singleton(logging.Logger, name='logger')

    # Gateways

    #database_client = providers.Singleton(sqlite3.connect, config.database.dsn)

    # Services

    core_service = providers.Singleton(CoreService)

    rest_service = providers.Singleton(
        FlaskFunctions,
        core=core_service
    )
