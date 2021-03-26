# Data
from typing import Any, Literal, Text
import redis
from redis import StrictRedis

# Base
from cachetools import cached, TTLCache
from functools import wraps
# filesystem
import logging
import json
import types
# Own
from arq_server.services.CoreService import Configuration
from arq_server.base.ArqErrors import ArqError


def method_wrapper(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except redis.RedisError as redis_e:
            raise ArqError(redis_e, 201)
        except Exception as e:
            raise e
        return result
    return wrapper


class RedisTools(object):
    # DefaultValues
    __host: str = 'localhost'
    __port: int = 6379
    __db: int = 0
    __password: Any = None
    __socket_timeout = None
    __socket_connect_timeout = None
    __socket_keepalive = None
    __socket_keepalive_options = None
    __connection_pool = None
    __unix_socket_path = None
    __encoding = 'utf-8'
    __encoding_errors: Text= 'strict'
    __charset = None
    __errors = None
    __decode_responses:bool = False
    __retry_on_timeout:bool = False
    __ssl:bool = False
    __ssl_keyfile = None
    __ssl_certfile = None
    __ssl_cert_reqs = 'required'
    __ssl_ca_certs = None
    __ssl_check_hostname = False
    __max_connections = None
    __single_connection_client = False
    __health_check_interval = 0
    __client_name = None
    __username = None

    # Services TIPS
    __logger: logging.Logger
    __config: Configuration

    __redis_client: StrictRedis

    def __init__(self, core):
        self.__init_services(core)
        # Local configuration
        self.__redis_conf_alias = self.__config.getProperty("groups", "redis")
        self.__redis_conf = self.__config.getGroupOfProperties(
            self.__redis_conf_alias,confKey=self.__redis_conf_alias)
        # Server configuration
        self.__conf_redis_client()
        redis.StrictRedis()
        self.__redis_client = redis.StrictRedis(
            host=self.__host, port=self.__port,
            db=self.__db, password=self.__password,
            socket_timeout=self.__socket_timeout, socket_connect_timeout=self.__socket_connect_timeout,
            socket_keepalive=self.__socket_keepalive, socket_keepalive_options=self.__socket_keepalive_options,
            connection_pool=self.__connection_pool, unix_socket_path=self.__unix_socket_path,
            encoding=self.__encoding, encoding_errors=self.__encoding_errors,
            charset=self.__charset, errors=self.__errors,
            decode_responses=Literal[self.__decode_responses],retry_on_timeout=self.__retry_on_timeout,
            ssl=self.__ssl,ssl_keyfile=self.__ssl_keyfile,
            ssl_certfile=self.__ssl_certfile,ssl_cert_reqs=self.__ssl_cert_reqs,
            ssl_ca_certs=self.__ssl_ca_certs,ssl_check_hostname=self.__ssl_check_hostname,
            max_connections=self.__max_connections,single_connection_client=self.__single_connection_client,
            health_check_interval=self.__health_check_interval,client_name=self.__client_name,
            username=self.__username
            )

    def setVal(self, key: str, value: str, volatile=False, timeToExpire=60) -> None:
        self.__redis_client.set(key, value)
        if volatile:
            self.__redis_client.expire(key, timeToExpire)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getValFast(self, key: str) -> Any:
        """
        obtiene de cache el valor asociado a la clave usada como parámetro.
        En caso de que se haya realizado la misma petición recientemente,ahorrará una 
        consulta y devolverá el valor cacheado
        """
        return self.__redis_client.get(key)

    def getVal(self, key: str) -> Any:
        """obtiene de cache el valor asociado a la clave usada como parámetro"""
        return self.__redis_client.get(key)

    def setDict(self, key: str, myDict: dict, volatile=False, timeToExpire=60) -> None:
        """Añade a la cache un objeto dict propio de python dado como parámetro de entrada"""
        marshallDict = json.dumps(myDict)
        self.setVal(key, marshallDict, volatile=volatile,
                    timeToExpire=timeToExpire)

    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def getDict(self, key: str) -> dict:
        """Recupera de cache un objeto dict propio de python referenciando su Key por parámetro"""
        aux = self.__redis_client.get(key)
        myDict = {}
        if isinstance(aux,str):
            myDict = json.loads(aux)
        return myDict

    def existKey(self, key: str) -> bool:
        """Comprueba si existe la clave dada como parámetro"""
        return bool(self.__redis_client.exists(key))

    def deleteKeyList(self, keyList) -> None:
        """Borra una lista de claves de cache dada como parámetro"""
        self.__logger.debug(
            "Borrando las siguientes claves de cache:%s", keyList)
        self.__redis_client.delete(keyList)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__const = core.constants()

    def __conf_redis_client(self):
        self.__host = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "host", self.__host,confKey=self.__redis_conf_alias)
        self.__port = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "port", self.__port, parseType=int,confKey=self.__redis_conf_alias)
        self.__db = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "db", self.__db, parseType=int,confKey=self.__redis_conf_alias)
        self.__password = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "password", self.__password,confKey=self.__redis_conf_alias)
        self.__socket_timeout = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "socket_timeout", self.__socket_timeout, parseType=int,confKey=self.__redis_conf_alias)
        self.__socket_connect_timeout = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "socket_connect_timeout", self.__socket_connect_timeout, parseType=int,confKey=self.__redis_conf_alias)
        self.__socket_keepalive = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "socket_keepalive", self.__socket_keepalive, parseType=int,confKey=self.__redis_conf_alias)
        self.__socket_keepalive_options = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "socket_keepalive_options", self.__socket_keepalive_options, parseType=dict,confKey=self.__redis_conf_alias)
        self.__connection_pool = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "connection_pool", self.__connection_pool, parseType=dict,confKey=self.__redis_conf_alias)
        self.__unix_socket_path = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "unix_socket_path", self.__unix_socket_path,confKey=self.__redis_conf_alias)
        self.__encoding_errors = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "encoding_errors", self.__encoding_errors,confKey=self.__redis_conf_alias)
        self.__charset = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "charset", self.__charset,confKey=self.__redis_conf_alias)
        self.__errors = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "errors", self.__errors,confKey=self.__redis_conf_alias)
        self.__decode_responses = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "decode_responses", self.__decode_responses, parseType=eval,confKey=self.__redis_conf_alias)
        self.__retry_on_timeout = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "retry_on_timeout", self.__retry_on_timeout, parseType=eval,confKey=self.__redis_conf_alias)
        self.__ssl = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl", self.__ssl, parseType=eval,confKey=self.__redis_conf_alias)
        self.__ssl_keyfile = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl_keyfile", self.__ssl_keyfile,confKey=self.__redis_conf_alias)
        self.__ssl_certfile = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl_certfile", self.__ssl_certfile,confKey=self.__redis_conf_alias)
        self.__ssl_cert_reqs = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl_cert_reqs", self.__ssl_cert_reqs,confKey=self.__redis_conf_alias)
        self.__ssl_ca_certs = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl_ca_certs", self.__ssl_ca_certs,confKey=self.__redis_conf_alias)
        self.__ssl_check_hostname = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "ssl_check_hostname", self.__ssl_check_hostname, parseType=eval,confKey=self.__redis_conf_alias)
        self.__max_connections = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "max_connections", self.__max_connections, parseType=int,confKey=self.__redis_conf_alias)
        self.__single_connection_client = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "single_connection_client", self.__single_connection_client, parseType=eval,confKey=self.__redis_conf_alias)
        self.__health_check_interval = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "health_check_interval", self.__health_check_interval, parseType=int,confKey=self.__redis_conf_alias)
        self.__client_name = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "client_name", self.__client_name,confKey=self.__redis_conf_alias)
        self.__username = self.__config.getPropertyDefault(
            self.__redis_conf_alias, "username", self.__username,confKey=self.__redis_conf_alias)

    def __getattribute__(self, attr):
        try:
            attr_val = super().__getattribute__(attr)
            if type(attr_val) == types.MethodType:
                w_attr = method_wrapper(attr_val)
                return w_attr
            else:
                return attr_val
        except:
            raise AttributeError(attr)
