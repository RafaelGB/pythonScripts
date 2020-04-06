
"""Example of dependency injection in Python."""
import logging
import sqlite3
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.support.UtilsService import UtilsService
# from arq_server.services.protocols.ProtocolsService import ProtocolsService
from arq_server.services.data_access.DataService import DataService
from arq_server.services.analytics.AnalyticService import AnalyticService

class ArqContainer(object):
    # Services
    core_service = providers.Singleton(CoreService)
    analytic_service = AnalyticService(core=core_service)
    data_service = DataService(core=core_service)
    # protocols_service = ProtocolsService(core=core_service)
    utils_service = UtilsService(core=core_service)
    
    

