# Data
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
            raise ArqError(redis_e,201)
        except Exception as e:
            raise e
        return result
    return wrapper

class RedisTools(object):
    # DefaultValues
    host='localhost'
    port=6379
    db=0
    password=None
    socket_timeout=None
    socket_connect_timeout=None
    socket_keepalive=None
    socket_keepalive_options=None
    connection_pool=None
    unix_socket_path=None
    encoding='utf-8'
    encoding_errors='strict'
    charset=None
    errors=None
    decode_responses=False
    retry_on_timeout=False
    ssl=False
    ssl_keyfile=None
    ssl_certfile=None
    ssl_cert_reqs='required'
    ssl_ca_certs=None
    ssl_check_hostname=False
    max_connections=None
    single_connection_client=False
    health_check_interval=0
    client_name=None
    username=None

    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration
    
    __redis_client : StrictRedis

    def __init__(self, core):
        self.__init_services(core)
        # Local configuration
        self.__redis_conf_alias = self.__config.getProperty("groups","redis")
        self.__redis_conf=self.__config.getGroupOfProperties(self.__redis_conf_alias)
        # Server configuration
        self.__conf_redis_client()

        self.__redis_client = redis.StrictRedis(self.host, self.port,
                 self.db, self.password, self.socket_timeout,
                 self.socket_connect_timeout,
                 self.socket_keepalive, self.socket_keepalive_options,
                 self.connection_pool, self.unix_socket_path,
                 self.encoding, self.encoding_errors, self.charset, self.errors,
                 self.decode_responses, self.retry_on_timeout,
                 self.ssl, self.ssl_keyfile, self.ssl_certfile,
                 self.ssl_cert_reqs, self.ssl_ca_certs,
                 self.ssl_check_hostname,self.max_connections, self.single_connection_client,
                 self.health_check_interval, self.client_name, self.username)
    
    def setVal(self, key:str, value:str,volatile=False,timeToExpire=60)-> None:
        self.__redis_client.set(key,value)
        if volatile:
            self.__redis_client.expire(key,timeToExpire)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getValFast(self, key:str) -> any:
        """
        obtiene de cache el valor asociado a la clave usada como parámetro.
        En caso de que se haya realizado la misma petición recientemente,ahorrará una 
        consulta y devolverá el valor cacheado
        """
        return self.__redis_client.get(key)
    
    def getVal(self, key:str) -> any:
        """obtiene de cache el valor asociado a la clave usada como parámetro"""
        return self.__redis_client.get(key)

    def setDict(self,key:str ,myDict:dict,volatile=False,timeToExpire=60) -> None:
        """Añade a la cache un objeto dict propio de python dado como parámetro de entrada"""
        marshallDict = json.dumps(myDict)
        self.setVal(key,marshallDict,volatile=volatile,timeToExpire=timeToExpire)

    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def getDict(self,key:str ) -> dict:
        """Recupera de cache un objeto dict propio de python referenciando su Key por parámetro"""
        myDict = json.loads(self.__redis_client.get(key))
        return myDict

    def existKey(self,key:str) -> bool:
        """Comprueba si existe la clave dada como parámetro"""
        return self.__redis_client.exists(key)

    def deleteKeyList(self,keyList:[]) -> None:
        """Borra una lista de claves de cache dada como parámetro"""
        self.__logger.debug("Borrando las siguientes claves de cache:%s",keyList)
        self.__redis_client.delete(keyList)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__const = core.constants()
    
    def __conf_redis_client(self):
        self.host = self.__config.getPropertyDefault(self.__redis_conf_alias,"host",self.host)
        self.port = self.__config.getPropertyDefault(self.__redis_conf_alias,"port",self.port,parseType=int)
        self.db = self.__config.getPropertyDefault(self.__redis_conf_alias,"db",self.db,parseType=int)
        self.password = self.__config.getPropertyDefault(self.__redis_conf_alias,"password",self.password)
        self.socket_timeout = self.__config.getPropertyDefault(self.__redis_conf_alias,"socket_timeout",self.socket_timeout,parseType=int)
        self.socket_connect_timeout = self.__config.getPropertyDefault(self.__redis_conf_alias,"socket_connect_timeout",self.socket_connect_timeout,parseType=int)
        self.socket_keepalive = self.__config.getPropertyDefault(self.__redis_conf_alias,"socket_keepalive",self.socket_keepalive,parseType=int)
        self.socket_keepalive_options = self.__config.getPropertyDefault(self.__redis_conf_alias,"socket_keepalive_options",self.socket_keepalive_options,parseType=dict)
        self.connection_pool = self.__config.getPropertyDefault(self.__redis_conf_alias,"connection_pool",self.connection_pool,parseType=dict)
        self.unix_socket_path = self.__config.getPropertyDefault(self.__redis_conf_alias,"unix_socket_path",self.unix_socket_path)
        self.encoding_errors = self.__config.getPropertyDefault(self.__redis_conf_alias,"encoding_errors",self.encoding_errors)
        self.charset = self.__config.getPropertyDefault(self.__redis_conf_alias,"charset",self.charset)
        self.errors = self.__config.getPropertyDefault(self.__redis_conf_alias,"errors",self.errors)
        self.decode_responses = self.__config.getPropertyDefault(self.__redis_conf_alias,"decode_responses",self.decode_responses,parseType=eval)
        self.retry_on_timeout = self.__config.getPropertyDefault(self.__redis_conf_alias,"retry_on_timeout",self.retry_on_timeout,parseType=eval)
        self.ssl = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl",self.ssl,parseType=eval)
        self.ssl_keyfile = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl_keyfile",self.ssl_keyfile)
        self.ssl_certfile = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl_certfile",self.ssl_certfile)
        self.ssl_cert_reqs = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl_cert_reqs",self.ssl_cert_reqs)
        self.ssl_ca_certs = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl_ca_certs",self.ssl_ca_certs)
        self.ssl_check_hostname = self.__config.getPropertyDefault(self.__redis_conf_alias,"ssl_check_hostname",self.ssl_check_hostname,parseType=eval)
        self.max_connections = self.__config.getPropertyDefault(self.__redis_conf_alias,"max_connections",self.max_connections,parseType=int)
        self.single_connection_client = self.__config.getPropertyDefault(self.__redis_conf_alias,"single_connection_client",self.single_connection_client,parseType=eval)
        self.health_check_interval = self.__config.getPropertyDefault(self.__redis_conf_alias,"health_check_interval",self.health_check_interval,parseType=int)
        self.client_name = self.__config.getPropertyDefault(self.__redis_conf_alias,"client_name",self.client_name)
        self.username = self.__config.getPropertyDefault(self.__redis_conf_alias,"username",self.username)
    
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
