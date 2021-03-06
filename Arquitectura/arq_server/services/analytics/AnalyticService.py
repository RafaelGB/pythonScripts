# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.analytics.DashTools import DashServer, DashTools
from arq_server.services.analytics.StadisticTools import StatisticsTools

class AnalyticServerFactory(containers.DeclarativeContainer):
    """Application IoC container."""
    core = providers.Dependency()

    # Services
    dash_tools = providers.Singleton(
        DashTools,
        core=core
    )
    # Factories
    dash_factory = providers.Factory(
        DashServer,
        core=core,
        tools=dash_tools
    )

class AnalyticService(containers.DeclarativeContainer):
    """Application IoC container."""
    core = providers.Dependency()
    # Factories
    factories = providers.Dependency()

    # Services    
    stadistics_tools = providers.Singleton(
        StatisticsTools,
        core=core,
        factories=factories
    )