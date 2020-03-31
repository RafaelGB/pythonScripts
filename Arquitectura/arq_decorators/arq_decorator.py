# Librerias nativas
from os import path
from functools import wraps
from inspect import isclass
from pathlib import Path
from logging.config import fileConfig

# Testing
import unittest

# filesystem
import configparser
import logging
import sys

# metadata
from typing import TypeVar
import types

# metrics
from datetime import datetime

# own
from arq_server.base.ArqErrors import ArqError
from arq_server.base.Constants import Const
from arq_server.containers.ArqContainer import ArqContainer
from arq_server.services.CoreService import Configuration
# own tools
from arq_server.services.data_access.CacheTools import RedisTools
from arq_server.services.support.OSTools import FileSystemTools
from arq_server.services.support.DockerTools import DockerTools
from arq_server.services.support.ConcurrentTools import ConcurrentTools

def method_wrapper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger: logging.getLogger() = ArqContainer.core_service().logger_service().arqLogger()
        logger.debug("INI - funcion '%s'", function.__name__)
        before = datetime.now()
        try:
            result = function(*args, **kwargs)
        except ArqError as arq_e:
            logger.error("Error controlado - función %s",
                         function.__name__, arq_e.code_message())

        except Exception as e:
            logger.error(
                "Error no controlado por la arquitectura - función %s \n%s", function.__name__, e)
            raise e
        after = datetime.now()
        logger.debug("FIN - funcion '%s' - tiempo empleado: %s ms",
                     function.__name__, (after-before).total_seconds() * 1000)
        return result
    return wrapper


def arq_decorator(Cls):
    class NewApp(object):

        def __init__(self, *args, **kwargs):
            self.__tools_init()
            self.__logger.info(
                "Genenando nuevo aplicativo bajo la plantilla %s\n%s", Cls.__name__, "*"*30)
            args, kwargs = self.__set_arq_attributes(*args, **kwargs)
            self.wrapped = Cls(*args, **kwargs)
            self.__logger.info(
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
                pass
            else:
                if type(x) == types.MethodType:
                    x = method_wrapper(x)
                return x

            try:
                x = self.wrapped.__getattribute__(attr)
            except:
                return None

            if type(x) == types.MethodType:
                x = method_wrapper(x)
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
            self.__logger.info('INI - %s', func.__name__)

        def __after_call(self, func):
            """
            Post-acciones para una función
            """
            self.__logger.info('FIN - %s', func.__name__)

        def __tools_init(self):
            try:
                # CORE
                self.__logger = ArqContainer.core_service().logger_service().arqLogger()
                self.__logger_test = ArqContainer.core_service().logger_service().testingLogger()
                self.__config = ArqContainer.core_service().config_service()
                self.__const = ArqContainer.core_service().constants()
                # SERVICES
                self.__protocols = ArqContainer.protocols_service
            except Exception as err:
                self.__logger.error(
                    "Ha ocurrido un problema inicializando las funcionalidades de la arquitectura: %s", err)
                raise err

        def __set_arq_attributes(self, *args, **kwargs):
            if "logger_test" not in kwargs:
                kwargs['logger_test'] = self.__logger_test
            if "config" not in kwargs:
                kwargs['config'] = self.__config
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

    # TYPE HINTS TEMPLATE
    __logger_test: logging.getLogger()
    __config: Configuration
    __const: Const
    __protocols: ArqContainer.protocols_service

    # TYPE HINTS logger
    logger: logging.getLogger()
    # TYPE HINTS public Tools
    dockerTools: DockerTools
    osTools: FileSystemTools
    cacheTools: RedisTools
    concurrentTools : ConcurrentTools

    def __init__(self, app_name, *args, **kwargs):
        self.app_name: str = app_name
        self.__init_kwargs_attrs(*args, **kwargs)
        self.__init_public_tools()
        self.__init_arq_test()
        self.__actions_on_init()

    """
    --------------
    CORE Functions
    --------------
    """

    def getProperty(self, property_key, parseType=str) -> any:
        """
        Recupera de la configuración de aplicación la propiedad solicitada por parámetro.
        Por defecto se entenderá como String. Se facilita como parámetro opcional la posibilidad
        de interpretar el tipo
        """
        return self.__config.getProperty(self.app_name, property_key, parseType=parseType)

    def getPropertyDefault(self, property_key: str, default: str, parseType=str) -> any:
        """
        Recupera de la configuración de aplicación la propiedad solicitada por parámetro. Añade
        la posibilidad de incluir uin valor por defecto en caso de no existir la propiedad.
        Por defecto se entenderá como String. Se facilita como parámetro opcional la posibilidad
        de interpretar el tipo
        """
        return self.__config.getPropertyDefault(self.app_name, property_key, default, parseType=parseType)

    """
    --------------
    TESTING
    --------------
    """

    def add_test(self, newTest: unittest.TestCase):
        """ Añade un test para la aplicación invocadora """
        self.__add_test(self.app_name, newTest)

    def run_own_test(self):
        """ Ejecuta todos los test de la aplicación invocadora """
        if self.app_name in self.__saved_test:
            ownTest = self.__saved_test.pop(self.app_name)
            self.__logger_test.info("INI - test asignados a la aplicación %s. Número de tests a ejecutar: '%d",
                                    self.app_name,
                                    ownTest.countTestCases()
                                    )
            unittest.TextTestRunner().run(ownTest)
            self.__logger_test.info(
                "FIN - test asignados a la aplicación '%s'. Test limpiados de la memoria", self.app_name)
        else:
            self.__logger_test.warn(
                "No existen actualmente test para la aplicación %s. Para añadir uno utilice la función 'add_test'", self.app_name)

    def run_arq_test(self):
        """ Ejecuta todos los test asociados a la arquitectura """
        if '__arq__' in self.__saved_test:
            arqTestSuite = self.__saved_test.pop('__arq__')
            self.__logger_test.info("INI - test asignados a la arquitectura. Número de tests a ejecutar: '%d",
                                    arqTestSuite.countTestCases()
                                    )
            verbosityLvl = self.__config.getPropertyDefault(
                "testing", "verbosity", 1, parseType=int)
            runner = unittest.TextTestRunner(verbosity=verbosityLvl)
            runner.run(arqTestSuite)

            self.__logger_test.info(
                "FIN - test asignados a la arquitectura. Test limpiados de la memoria")
            self.__flags["skip_run_arq_test"] = True
        else:
            self.__logger_test.warn(
                "Los test de arquitectura ya se han ejecutado. Reinicie la ejecución en caso de querer ejecutarlos de nuevo")

    """
    ------------------
    Arquitecture FLAG Actions
    ------------------
    """

    def __actions_on_init(self):
        if bool(self.__config.getProperty("flags", "init.test")):
            self.run_arq_test()
    """
    ------------------
    Test asociados a la arquitectura
    respuesta esperada: "resultado obntenido","resultado esperado"
    ------------------
    """

    def __add_test(self, context: str, newTest):
        try:
            if not context in self.__saved_test:
                self.__saved_test[context] = unittest.TestSuite()
            self.__saved_test[context].addTest(
                unittest.FunctionTestCase(
                    newTest,
                    setUp=lambda: None,
                    tearDown=lambda: None)
            )
        except Exception as err:
            self.logger.error(
                "Ha habido un problema añadiendo el test '%s' - %s",
                newTest.__name__,
                err
            )

    def __test_logging(self):
        """TEST orientado a logging"""
        try:
            self.__logger_test.info("Log nivel info")
            self.__logger_test.warn("Log nivel warn")
            self.__logger_test.error("Log nivel err")
            self.__logger_test.debug("Log nivel debug")
        except:
            assert False
        assert True

    def __test_config(self):
        """TEST orientado a configuracion"""
        jumps = 2000
        before = datetime.now()
        for i in range(jumps):
            self.__config.getPropertyVerbose("base", "path.resources")
        after = datetime.now()
        usedTimeNoCache = (after-before).total_seconds() * 1000

        before = datetime.now()
        for i in range(jumps):
            self.__config.getProperty("base", "path.resources")
        after = datetime.now()
        usedTimeCache = (after-before).total_seconds() * 1000
        self.__logger_test.info(
            "%d accesos a misma configuración. %d ms usando cache vs %d ms sin usar cache",
            jumps,
            usedTimeCache,
            usedTimeNoCache
        )

        assert usedTimeCache < usedTimeNoCache

    """
    ------------------
    Internal Functions
    ------------------
    """

    def __init_kwargs_attrs(self, *args, **kwargs):
        for key, value in kwargs.items():
            # Valores privados propios de la clase plantilla
            self.__dict__["_{}__{}".format(
                self.__class__.__name__, key)] = value
        # Valores visibles para la aplicación

    def __init_public_tools(self):
        # Core
        self.logger = ArqContainer.core_service(
        ).logger_service().appLogger()
        # Data
        self.cacheTools = ArqContainer.data_service.cache_tools()
        # Utils
        self.dockerTools = ArqContainer.utils_service.docker_tools()
        self.osTools = ArqContainer.utils_service.file_system_tools()
        self.concurrentTools = ArqContainer.utils_service.concurrent_tools()
    # TESTING

    def __init_arq_test(self):
        if not self.__flags["skip_add_arq_test"]:
            for attr in dir(self):
                test = getattr(self, attr)
                if attr.startswith("_{}__{}".format(
                        self.__class__.__name__, "test")) and callable(test):
                    self.__add_test(
                        '__arq__',
                        test
                    )
            self.__flags["skip_add_arq_test"] = True
