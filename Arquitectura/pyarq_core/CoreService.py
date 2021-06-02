# IoC
from dependency_injector import containers, providers
#own
from .Logger import Logger
from .Config import Configuration
from .Constants import Const

"""
Inversion of control section
""" 
class CoreService(containers.DeclarativeContainer):
    """Application IoC container."""
    # Configuration
    config = providers.Configuration()
    # Services
    logger_service = providers.Singleton(Logger,logger_config=config.logger)
    constants = providers.Singleton(Const)
    
    config_service = providers.Singleton(
        Configuration,
        const=constants,
        logger=logger_service,
        configuration_config=config.configuration
    )


