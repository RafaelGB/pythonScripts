# Dependency
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration as di_Configuration
# System
import sys
import os
# Own
from arq_server.services.CoreService import Configuration, Logger, Const
from arq_server.services.data_access.relational.DatabaseSQL import DbSQL
from tdd.containers.TestingContainer import TestingContainer

"""
# TYPE HINTS public Tools
        dockerTools: DockerTools
        osTools: FileSystemTools
        cacheTools: RedisTools
        concurrentTools : ConcurrentTools
        stadisticsTools : StatisticsTools
        dashTools : DashTools
        restTools : APIRestTools
        sqlTools : DbSQL
"""
class TestingArq(object):
    __container:DeclarativeContainer

    def __init__(self,**kwargs):
        confif_path = os.environ['config_path_file']
        self.__container = TestingContainer()
        self.__container.init_resources()
        self.__container.config.from_yaml(confif_path,required=True)
        self.__container.wire(modules=[sys.modules[__name__]])

    def config_container(self) -> di_Configuration:
        return self.__container.config

    def get_logger_service(self) -> Logger:
        return self.__container.core_service().logger_service()
    
    def get_config_service(self) -> Configuration:
        return self.__container.core_service().config_service()
    
    def get_sql_service(self) -> DbSQL:
        return self.__container.data_service().relational_tools().db_sql()