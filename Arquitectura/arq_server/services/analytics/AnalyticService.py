# system
import sys, os
import pathlib
import logging

# IoC
from dependency_injector import containers, providers
# Own
from arq_server.services.analytics.DashTools import DashTools
from arq_server.services.analytics.StadisticTools import StatisticsTools

class AnalyticService(containers.DeclarativeContainer):
    """Application IoC container."""
    core = providers.Dependency()
    # Services
    dash_tools = providers.Singleton(
        DashTools,
        core=core
    )
    stadistics_tools = providers.Singleton(
        StatisticsTools,
        core=core,
        dash=dash_tools
    )