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
from arq_server.services.data_access.CacheTools import RedisTools


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
                # SERVICES
                self.__protocols = ArqContainer.protocols_service
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
            if "utils" not in kwargs:
                kwargs['utils'] = ArqContainer.utils_service
            if "cache" not in kwargs:
                kwargs['cache'] = ArqContainer.data_service.cache_tools()
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
    __logger: logging.getLogger()
    __config: Configuration
    __protocols: ArqContainer.protocols_service
    __utils: ArqContainer.utils_service
    __cache: RedisTools
    # TYPE HINTS APP
    logger: logging.getLogger()

    def __init__(self, app_name, *args, **kwargs):
        self.app_name: str = app_name
        self.__init_kwargs_attrs(*args, **kwargs)
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

    def getDirectoryTree(self, dirPath) -> dict:
        """
        Dada una ruta a un directorio del fileSystem, devuelve un diccionario con la información de su contenido,
        incluyendo los directorios anidados
        """
        return self.__utils.file_system_tools().getDirectoryTree(dirPath)

    """
    --------------
    SUPPORT
    -------
    OS Tools
    --------------
    """

    def modifyValuesOnDict(self, a_dict:dict, key:str, key_value_subst:dict) -> dict:
        """
        dado un diccionario 'referencia', una clave y un diccionario 'variables' (clave-valor), modifica, en todos los niveles
        del diccionario base donde se encuentre la clave, su valor asociado en caso de que dicho valor contenga alguna de las
        variables especificadas en el diccionario 'variables' con el formato {{variable}},siendo sustituída por el valor referenciado.

        i.e.: {
            "clave1":"valor1",
            "clave2":
                {
                    "clave_buscada":"esta clave contiene {{variable}}"
                }
            }
        """
        return self.__utils().file_system_tools().modifyValuesOnDict(a_dict, key, key_value_subst)

    def add_new_argument(self) -> None:
        self.__utils.parse_args_tools().add_argument()

    def show_help(self) -> None:
        self.__utils.parse_args_tools().show_help()
    """
    --------------
    DATA
    ----
    Cache
    --------------
    """

    def getValFromCache(self, key: str, isFast: bool) -> any:
        """
        CACHE - obtiene de cache el valor asociado a la clave usada como parámetro.
        En caso de que el flag booleano 'isFast' sea 'True' y se haya realizado la misma
        petición recientemente. Se ahorrará una consulta y devolverá el valor cacheado
        """
        return (self.__cache.getVal(key), self.__cache.getValFast(key))[isFast]

    def setValOnCache(self, key: str, value: any, volatile=False, timeToExpire=60) -> None:
        """
        CACHE - Añade a la cache el par 'Clave-Valor' dada como parámetros de entrada
        """
        self.__cache.setVal(key, value, volatile=volatile,
                            timeToExpire=timeToExpire)

    def setDictOnCache(self, dictKey: str, myDict: dict, volatile=False, timeToExpire=60) -> None:
        """
        CACHE - Añade a la cache un objeto dict propio de python dado como parámetro de entrada
        """
        self.__cache.setDict(
            dictKey, myDict, volatile=volatile, timeToExpire=timeToExpire)

    def getDictFromCache(self, dictKey: str) -> dict:
        """
        CACHE - Recupera de cache un objeto dict propio de python referenciando su Key por parámetro
        """
        return self.__cache.getDict(dictKey)

    def existKeyFromCache(self, key: str) -> bool:
        """CACHE - Comprueba si existe la clave dada como parámetro"""
        return self.__cache.existKey(key)

    def deleteFromCache(self, keyList: []) -> None:
        """CACHE - Borra una lista de claves de cache dada como parámetro"""
        return self.__cache.deleteKeyList(keyList)

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
            arqTest = self.__saved_test.pop('__arq__')
            self.__logger_test.info("INI - test asignados a la arquitectura. Número de tests a ejecutar: '%d",
                                    arqTest.countTestCases()
                                    )
            unittest.TextTestRunner().run(arqTest)

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

    def __add_test(self, context: str, newTest: unittest.TestCase):
        try:
            if not context in self.__saved_test:
                testSuite = unittest.TestSuite()
                self.__saved_test[context] = unittest.TestSuite()
            self.__saved_test[context].addTest(
                unittest.FunctionTestCase(newTest)
            )
        except Exception as err:
            self.__logger.error(
                "Ha habido un problema añadiendo el test '%s' - %s",
                newTest.__name__,
                err
            )

    def __test_logging(self):
        """TEST orientado a logging"""
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

    def __test_cacheArq(self):
        """TEST orientado a cache"""
        if self.__config.getProperty("flags", "enable.redis", parseType=bool):
            key = "testKey"
            value = "testValue"
            self.setValOnCache(key, value, volatile=True, timeToExpire=5)
            exist = self.existKeyFromCache(key)
            assert exist

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
        if not self.__flags["skip_add_arq_test"]:
            for attr in dir(self):
                test = getattr(self, attr)
                if attr.startswith("_{}__{}".format(
                        self.__class__.__name__, "test")) and callable(test):
                    self.__add_test(
                        '__arq__',
                        unittest.FunctionTestCase(
                            test
                        )
                    )
            self.__flags["skip_add_arq_test"] = True
