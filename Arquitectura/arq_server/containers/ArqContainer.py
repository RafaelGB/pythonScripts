
"""Example of dependency injection in Python."""
import logging
import sqlite3
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
# Support
from arq_server.services.support.UtilsService import UtilsService
# data access
from arq_server.services.data_access.DataService import DataService
# Analytics
from arq_server.services.analytics.AnalyticService import AnalyticService,AnalyticServerFactory

class ArqContainer(object):
    # Base
    core_service = providers.Singleton(CoreService)
    # Factories
    analytic_factories = AnalyticServerFactory(core=core_service)
    # Services
    analytic_service = AnalyticService(core=core_service,factories=analytic_factories)
    data_service = DataService(core=core_service)
    utils_service = UtilsService(core=core_service)
    
    

