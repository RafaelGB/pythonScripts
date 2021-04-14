# Dependency
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration as di_Configuration
# System
import sys
import os
# Own
from tdd.containers.TestingContainer import TestingContainer
# own
from arq_server.services.CoreService import Configuration, Logger, Const
# Analytics
from arq_server.services.analytics.StadisticTools import StatisticsTools
from arq_server.services.analytics.DashTools import DashTools
# Data
from arq_server.services.data_access.CacheTools import RedisTools
from arq_server.services.data_access.relational.DatabaseSQL import DbSQL
# Support
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.support.DockerTools import DockerTools
from arq_server.services.support.ConcurrentTools import ConcurrentTools
from arq_server.services.support.SecurityTools import Security
# Physical Protocols
from arq_server.services.protocols.physical.rest.RestService import APIRestTools
# Logical Protocols

class TestingArq(object):
    __container:DeclarativeContainer

    def __init__(self,**kwargs):
        config_path = os.environ['config_path_file']
        self.__container:TestingContainer = TestingContainer()
        self.__container.init_resources()
        self.__container.config.from_yaml(config_path,required=True)
        self.__container.wire(modules=[sys.modules[__name__]])

    def config_container(self) -> di_Configuration:
        return self.__container.config

    def get_logger_service(self) -> Logger:
        return self.__container.core_service().logger_service()
    
    def get_config_service(self) -> Configuration:
        return self.__container.core_service().config_service()
    
    def get_concurrent_tools(self) -> ConcurrentTools:
        return self.__container.utils_service().concurrent_tools()
        
    def get_sql_service(self) -> DbSQL:
        sqldb = None
        try:
            sqldb = self.__container.data_service().relational_tools().db_sql()
            return sqldb
        except Exception as e:
            raise e

if __name__ == "__main__":
    arq = TestingArq()
    sql_service = arq.get_sql_service()
