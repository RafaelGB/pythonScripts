# Filesystem
import logging

# Database
from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

# Own
from arq_server.services.CoreService import Configuration

Base = declarative_base()

class DbSQL:
    # Services TIPS
    __logger: logging.Logger
    __config: Configuration

    def __init__(self,core):
        self.__init_services(core)
        self.__engine = self.__db_config()
        self.__init_schema()

    def __db_config(self) -> str:
        sqlConfig = self.__config.getGroupOfProperties("sql",confKey="relational")
        db_type = sqlConfig['db_type']
        driver = sqlConfig['driver']
        db_user = sqlConfig['db_user']
        db_password = sqlConfig['db_password']
        host = sqlConfig['host']
        connection = sqlConfig['connection']
        config =db_type + \
                ("+"+driver,"")[driver == None] + \
                "://"+db_user + \
                ":"+db_password + \
                "@"+host + \
                "/"+connection
        return create_engine(config, echo=True)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__const = core.constants()

    def __init_schema(self):
        self.__logger.info("Inicializando los esquemas de la arquitectura en bbdd")
        from arq_server.services.data_access.relational.models.User import User
        Base.metadata.create_all(bind=self.__engine)
        self.__logger.info("Esquemas inicializados")
