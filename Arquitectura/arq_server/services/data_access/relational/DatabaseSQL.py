# Filesystem
import logging
from typing import Any, List

# Database
from sqlalchemy import  create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker, Session

# Own
from arq_server.services.CoreService import Configuration

Base = declarative_base()

class DbSQL:
    """
    Servicio que ofrece acceso CRUD a base de datos relacional
    ---
    Por defecto la arquitectura trabaja con el driver de postgres
    """
    # Services TIPS
    __logger: logging.Logger
    __config: Configuration
    __current_session: sessionmaker

    def __init__(self,core):
        self.__init_services(core)
        self.__engine = self.__db_config()
        self.__engine.connect() # Abre conexión con bbdd
        self.__session_maker = sessionmaker(bind=self.__engine)
        self.__init_schema()
    
    def select_items_filtering_by(self,item_class,**kwargs) -> list:
        # select * from item_class where **kwargs
        with self.__session_maker() as session:
            result:List[item_class] = session.query(item_class).filter_by(**kwargs)
            return result.all()
    
    def select_unique_item_filtering_by(self,item_class,**kwargs) -> Any:
        # select * from item_class where **kwargs (resultado único obligado)
        with self.__session_maker() as session:
            result:List[item_class] = session.query(item_class).filter_by(**kwargs)
            if len(result) == 0:
                return result.pop(0)
            else:
                return None

    def add_item(self,item):
        """
        Escribe un item en BBDD
        """
        try:
            if self.__current_session is None:
                self.open_session()
            self.__current_session.add(item)
        except Exception as e:
            self.__logger.error("Tipo de error: %s",e.__class__.__name__)
            self.__current_session.rollback()
            self.__current_session = None

    def open_session(self):
        if self.__current_session is None:
            self.__logger.info("Se abre nueva sesión transaccional")
            self.__current_session = self.__session_maker()
        else:
            self.__logger.error("Existe ya una sesión abierta en este hilo")

    def commit_current_session(self):
        if self.__current_session is not None:
            self.__logger.info("Guardado cambios realizados durante la sesión")
            self.__current_session.commit()
            self.__current_session = None
            self.__logger.info("Datos guardados, se cierra sesión")
        else:
            self.__logger.error("No existe una sesión abierta actualmente en este hilo")

    def __db_config(self) -> Engine:
        """
        Dada una configuración, 
        """
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
        return create_engine(config, echo=self.__config.getProperty("sql","verbose",parseType=eval,confKey="relational"))

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__const = core.constants()

    def __init_schema(self):
        self.__logger.info("Inicializando los esquemas de la arquitectura en bbdd")
        # Importamos las tablas propias de la arquitectura
        from arq_server.services.data_access.relational.models.User import User
        Base.metadata.create_all(bind=self.__engine)
        self.__current_session = None
        self.__logger.info("Esquemas inicializados")
