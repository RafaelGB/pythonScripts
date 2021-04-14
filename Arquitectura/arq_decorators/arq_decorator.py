# Librerias nativas
from os import path, environ
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

# Injection
from dependency_injector.wiring import inject, Provide

# Testing
import unittest

# filesystem
import configparser
import logging
import sys

# metadata
from typing import TypeVar,Any
import types

# metrics
from datetime import datetime

# own
from arq_server.base.ArqErrors import ArqError
from arq_server.base.Constants import Const
from arq_server.containers.ArqContainer import BaseContainerDecorator, ArqContainer
from arq_server.services.CoreService import Configuration, Base
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
from arq_server.services.protocols.logical.NormalizeSelector import NormalizeSelector

# def transactional(function):
#     """
#     La función decorada pasa a tener un comportamiento transaccional en bbdd
#     """
#     @wraps(function)
#     def wrapper(*args, **kwargs):
#         relational:DbSQL = ArqContainer.data_service.relational_tools().db_sql()
#         relational.open_session()
#         result = function(*args,**kwargs)
#         relational.commit_current_session()
#         return result
#     return wrapper

# def requires_authorization(function):
#     """
#     Se comprueba token de seguridad (requerido en los argumentos)
#     """
#     @wraps(function)
#     def wrapper(*args, **kwargs):
#         security:Security = ArqContainer.utils_service().security_tools()
#         if 'auth_token' not in kwargs:
#             raise ArqError("Función que requiere autorización no trae token")
#         security.validate_token(kwargs['auth_token'])
#         result = function(*args,**kwargs)
#         return result
#     return wrapper    

def method_wrapper(function,logger:logging.Logger):
    if function.__name__ in ['__tools_init']:
        return function
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger.debug("INI - funcion '%s'", function.__name__)
        before = datetime.now()
        result = None
        try:
            result = function(*args, **kwargs)
        except ArqError as arq_e:
            logger.exception("Error controlado - función %s",
                         function.__name__, arq_e.message())

        except Exception as e:
            logger.exception(
                    "Error no controlado por la arquitectura - función %s \n%s", function.__name__, e)
            raise e
        finally:
            after = datetime.now()
            logger.debug("FIN - funcion '%s' - tiempo empleado: %s ms",
                     function.__name__, (after-before).total_seconds() * 1000)
            return result
    return wrapper


def arq_decorator(Cls):
    class NewApp(BaseContainerDecorator):
        # Protected HINTS
        _const: Const
        # TYPE HINTS logger
        logger: logging.Logger

        # TYPE HINTS public Tools
        dockerTools: DockerTools
        osTools: FileSystemTools
        cacheTools: RedisTools
        concurrentTools : ConcurrentTools
        stadisticsTools : StatisticsTools
        dashTools : DashTools
        restTools : APIRestTools
        sqlTools : DbSQL

        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            self.__tools_init()
            args, kwargs = self.__set_arq_attributes(*args, **kwargs)
            self.wrapped = Cls(*args, **kwargs)
            
            self._logger.info(
                "Genenando nuevo aplicativo bajo la plantilla %s\n%s", Cls.__name__, "*"*30)
            
            self._logger.info(
                "%s\nPlantilla %s generada correctamente", "*"*30, Cls.__name__)

        def __getattribute__(self, attr):
            """
            esta función es invocada cada vez que se accede a cualquier atributo de la clase decoradora. 
            En primer lugar intenta obtener el atributo de NewCls. Si falla, intenta obtener el 
            atributo de self.oInstance (un instancia de la clase decorada).
            """
            try:
                x = super(NewApp, self).__getattribute__(attr)
            except (AttributeError, TypeError) as e:
                # Continua al siguiente bloque de try-except
                pass
            else:
                # Devuelve atributo del padre
                if type(x) == types.MethodType:
                    x = method_wrapper(x,self._logger)
                return x

            try:
                # Recupera atributos del decorador
                if attr == 'wrapped':
                    return object.__getattribute__(self, attr)
                x = self.wrapped.__getattribute__(attr)
            except:
                return None
            # Devuelve atributo del hijo
            if type(x) == types.MethodType:
                x = method_wrapper(x,self._logger)
            return x

        def __run_test(self, test):
            self.__before_call(test)
            try:
                return test(self)
            finally:
                self.__after_call(test)

        def __before_call(self, func):
            """
            Pre-acciones para una función
            """
            self._logger.info('INI - %s', func.__name__)

        def __after_call(self, func):
            """
            Post-acciones para una función
            """
            self._logger.info('FIN - %s', func.__name__)

        def __tools_init(self):
            try:
                # CORE
                # inicializo los servicios internos
                self._logger = self._container.core_service().logger_service().arqLogger()
                self._logger_test = self._container.core_service().logger_service().testingLogger()
                self._config = self._container.core_service().config_service()
                self._const = self._container.core_service().constants()

            except Exception as err:
                self._logger.error(
                    "Ha ocurrido un problema inicializando las funcionalidades de la arquitectura: %s", err)
                raise err

        def __set_arq_attributes(self, *args, **kwargs):
            """
            Objetos exportados a la clase decorada
            """
            if "logger_test" not in kwargs:
                kwargs['logger_test'] = self.__logger_test
            if "config" not in kwargs:
                kwargs['config'] = self._config
            if "arq_container" not in kwargs:
                kwargs['arq_container'] = self._container
            
            return args, kwargs
    return NewApp

@arq_decorator
class ArqToolsTemplate:
    # TEMPLATE FLAGS
    __flags = {
        "skip_add_arq_test": False
    }
    # TEMPLATE VARS
    __saved_test = {}

    # TYPE HINTS private tools
    __logger_test: logging.Logger
    __config: Configuration
    __arq_container: ArqContainer

    def __init__(self, app_name, *args, **kwargs):
        self.app_name: str = app_name
        self.__init_kwargs_attrs(*args, **kwargs)
        self.__init_public_tools()
        self.__actions_on_init()

    """
    --------------
    CORE Functions
    --------------
    """

    def getProperty(self, group, property_key, parseType=str) -> Any:
        """
        Recupera de la configuración de aplicación la propiedad solicitada por parámetro.
        Por defecto se entenderá como String. Se facilita como parámetro opcional la posibilidad
        de interpretar el tipo
        """
        return self.__config.getProperty(group, property_key, parseType=parseType,confKey=self.app_name)

    def getPropertyDefault(self, group, property_key: str, default: str, parseType=str) -> Any:
        """
        Recupera de la configuración de aplicación la propiedad solicitada por parámetro. Añade
        la posibilidad de incluir uin valor por defecto en caso de no existir la propiedad.
        Por defecto se entenderá como String. Se facilita como parámetro opcional la posibilidad
        de interpretar el tipo
        """
        return self.__config.getPropertyDefault(group, property_key, default, parseType=parseType, confKey=self.app_name)

    """
    ------------------
    BEHAIVOR Functions
    ------------------
    """
    def expose_app(self,appToExpose:object):
        """
        Las funciones públicas de la clase pasada como parámetro
        quedan expuestas a llamadas por protocolos físicos
        """
        tmp_logical:NormalizeSelector=self.__arq_container.protocols_service().logical_protocol_services().normalize_selector_service()
        tmp_logical.addAvaliableService(appToExpose)

    """
    ------------------
    Arquitecture FLAG Actions
    ------------------
    """

    def __actions_on_init(self):
        """
        Acciones a realizar durante el arranque
        """
        pass

    """
    ------------------
    Internal Functions
    ------------------
    """

    def __init_kwargs_attrs(self, *args, **kwargs):
        """
        Los valores que recibo como argumentos del decorador los
        transformo en objetos privados de la clase
        """
        for key, value in kwargs.items():
            # Valores privados propios de la clase plantilla
            self.__dict__["_{}__{}".format(
                self.__class__.__name__, key)] = value
        # Valores visibles para la aplicación

    def __init_public_tools(self):
        # Core
        self.logger = self.__arq_container.core_service().logger_service().appLogger()
        # Analytics
        #self.stadisticsTools = self.__arq_container.analytic_service.stadistics_tools()
        #self.dashTools = self.__arq_container.analytic_factories.dash_tools()

        # Data
        self.cacheTools = self.__arq_container.data_service().cache_tools()
        self.sqlTools = self.__arq_container.data_service().relational_tools().db_sql()

        # Utils
        self.dockerTools = self.__arq_container.utils_service().docker_tools()
        self.osTools = self.__arq_container.utils_service().file_system_tools()
        self.concurrentTools = self.__arq_container.utils_service().concurrent_tools()

        # Physical Protocols
        self.restTools = self.__arq_container.protocols_service().physical_protocol_services().rest_protocol_tools()
