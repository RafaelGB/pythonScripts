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
from arq_server.containers.ArqContainer import ArqContainer
from arq_server.services.CoreService import Configuration


def method_wrapper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger: logging.getLogger() = ArqContainer.core_service().logger_service().arqLogger()
        logger.debug("INI - funcion '%s'", function.__name__)
        before = datetime.now()
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            logger.error(
                "Error no controlado por la arquitectura - funcion %s \n%s", function.__name__, e)
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
                "INI - arranque decorador de la clase %a", Cls.__name__)
            args, kwargs = self.__set_arq_attributes(*args, **kwargs)
            self.wrapped = Cls(*args, **kwargs)
            self.__logger.info(
                "FIN - arranque decorador de la clase %a", Cls.__name__)

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
                return x

            x = self.wrapped.__getattribute__(attr)
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
                # SERVICES
                self.__protocols = ArqContainer.protocols_service()
            except Exception as err:
                self.__logger.error(
                    "Ha ocurrido un problema inicializando las funcionalidades de la arquitectura: %s", err)
                raise err

        def __set_arq_attributes(self, *args, **kwargs):
            if "logger" not in kwargs:
                kwargs['logger'] = self.__logger
            if "logger_test" not in kwargs:
                kwargs['logger_test'] = self.__logger_test
            if "config" not in kwargs:
                kwargs['config'] = self.__config
            if "os_tools" not in kwargs:
                kwargs['utils'] = ArqContainer.utils_service()
            return args, kwargs
    return NewApp


@arq_decorator
class ArqToolsTemplate:
    # TEMPLATE FLAGS
    __flags = {
        "skip_add_arq_test":False
        }
    # TEMPLATE VARS
    __suite = unittest.TestSuite()

    # TYPE HINTS TEMPLATE
    __logger: logging.getLogger()
    __config: Configuration
    __protocols: ArqContainer.protocols_service()
    __utils: ArqContainer.utils_service()
    # TYPE HINTS APP
    logger: logging.getLogger()

    def __init__(self, app_name, *args, **kwargs):
        self.app_name: str = app_name
        self.__init_kwargs_attrs(*args, **kwargs)
        self.__init_arq_test()

    """
    --------------
    CORE Functions
    --------------
    """

    def getProperty(self, property_key) -> str:
        return self.__config.getProperty(self.app_name, property_key)

    def getPropertyDefault(self, property_key: str, default: str) -> str:
        return self.__config.getPropertyDefault(self.app_name, property_key, default)

    def getDirectoryTree(self, dirPath) -> dict:
        return self.__utils.file_system_tools().getDirectoryTree(dirPath)

    """
    --------------
    OS Tools
    --------------
    """

    def modifyValuesOnDict(self, a_dict, key, key_value) -> dict:
        return self.__utils().file_system_tools().modifyValuesOnDict(a_dict, key, key_value)

    """
    --------------
    TESTING
    --------------
    """

    def run_tests(self):

        self.__logger_test.info("INI - test asignados a la aplicación %s\nNúmero de tests a ejecutar: '%d",
                                self.app_name,
                                self.__suite.countTestCases()
                                )
        unittest.TextTestRunner().run(self.__suite)
        self.__logger_test.info(
            "FIN - test asignados a la aplicación '%s'", self.app_name)

    def add_test(self, newTest: unittest.TestCase):
        try:
            self.__suite.addTest(
                unittest.FunctionTestCase(newTest)
            )
        except Exception as err:
            self.__logger.error(
                "Ha habido un problema añadiendo el test '%s' - %s",
                newTest.__name__,
                err
            )

    """
    ------------------
    Arquitecture FLAG Actions
    ------------------
    """
    def actions_on_init(self):
        if bool(self.__config.getProperty("flags", "init.test")):
            self.run_tests()
    """
    ------------------
    Test asociados a la arquitectura
    respuesta esperada: "resultado obntenido","resultado esperado"
    ------------------
    """

    def __test_logging(self):
        result = ""
        expected = "OK"
        try:
            self.__logger_test.info("Log nivel info")
            self.__logger_test.warn("Log nivel warn")
            self.__logger_test.error("Log nivel err")
            self.__logger_test.debug("Log nivel debug")
            result = "OK"
        except:
            result = "KO"

        assert result == expected
    
    def __test_cacheTools(self):
        jumps = 2000
        before = datetime.now()
        for i in range(jumps):
            self.__config.getPropertyVerbose("base","path.resources")
        after = datetime.now()
        usedTimeNoCache = (after-before).total_seconds() * 1000

        before = datetime.now()
        for i in range(jumps):
            self.__config.getProperty("base","path.resources")
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
        # Valores privados añadidos a la aplicación
        self.__dict__["{}".format("logger")] = ArqContainer.core_service(
        ).logger_service().appLogger()
    # TESTING

    def __init_arq_test(self):
        if self.__flags["skip_add_arq_test"]:
            for attr in dir(self):
                test = getattr(self, attr)
                if attr.startswith("_{}__{}".format(
                        self.__class__.__name__, "test")) and callable(test):
                    self.__suite.addTest(
                        unittest.FunctionTestCase(
                            test
                        )
                    )
            self.__flags["skip_add_arq_test"] = True
