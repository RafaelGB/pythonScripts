# Data
import redis
# Base
from cachetools import cached, TTLCache
# filesystem
import logging
# IoC
from arq_server.services.CoreService import Configuration

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

    # Services
    logger: logging.getLogger()
    config: Configuration
    
    def __init__(self, core):
        self.__init_services(core)
        # Local configuration
        self.__redis_conf_alias = self.config.getProperty("groups","redis")
        self.__redis_conf=self.config.getGroupOfProperties(self.__redis_conf_alias)
        # Server configuration
        self.__conf_redis_client()
        self.redis = redis.Redis(self.host, self.port,
                 self.db, self.password, self.socket_timeout,
                 self.socket_connect_timeout,
                 self.socket_keepalive, self.socket_keepalive_options,
                 self.connection_pool, self.unix_socket_path,
                 self.encoding, self.encoding_errors,
                 self.charset, self.errors,
                 self.decode_responses, self.retry_on_timeout,
                 self.ssl, self.ssl_keyfile, self.ssl_certfile,
                 self.ssl_cert_reqs, self.ssl_ca_certs,
                 self.ssl_check_hostname,
                 self.max_connections, self.single_connection_client,
                 self.health_check_interval, self.client_name, self.username)
    
    def setVal(self, key:str, value:str)-> None:
        self.redis.set(key,value)

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getValFast(self, key:str) -> any:
        return self.redis.get(key)
    
    def getVal(self, key:str) -> any:
        return self.redis.get(key)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()
    
    def __conf_redis_client(self):
        self.host = self.config.getPropertyDefault(self.__redis_conf_alias,"host",self.host)
        self.port = self.config.getPropertyDefault(self.__redis_conf_alias,"port",self.port,parseType=int)
        self.db = self.config.getPropertyDefault(self.__redis_conf_alias,"db",self.db,parseType=int)
        self.password = self.config.getPropertyDefault(self.__redis_conf_alias,"password",self.password)
        self.socket_timeout = self.config.getPropertyDefault(self.__redis_conf_alias,"socket_timeout",self.socket_timeout,parseType=int)
        self.socket_connect_timeout = self.config.getPropertyDefault(self.__redis_conf_alias,"socket_connect_timeout",self.socket_connect_timeout,parseType=int)
        self.socket_keepalive = self.config.getPropertyDefault(self.__redis_conf_alias,"socket_keepalive",self.socket_keepalive,parseType=int)
        self.socket_keepalive_options = self.config.getPropertyDefault(self.__redis_conf_alias,"socket_keepalive_options",self.socket_keepalive_options,parseType=dict)
        self.connection_pool = self.config.getPropertyDefault(self.__redis_conf_alias,"connection_pool",self.connection_pool,parseType=dict)
        self.unix_socket_path = self.config.getPropertyDefault(self.__redis_conf_alias,"unix_socket_path",self.unix_socket_path)
        self.encoding_errors = self.config.getPropertyDefault(self.__redis_conf_alias,"encoding_errors",self.encoding_errors)
        self.charset = self.config.getPropertyDefault(self.__redis_conf_alias,"charset",self.charset)
        self.errors = self.config.getPropertyDefault(self.__redis_conf_alias,"errors",self.errors)
        self.decode_responses = self.config.getPropertyDefault(self.__redis_conf_alias,"decode_responses",self.decode_responses,parseType=eval)
        self.retry_on_timeout = self.config.getPropertyDefault(self.__redis_conf_alias,"retry_on_timeout",self.retry_on_timeout,parseType=eval)
        self.ssl = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl",self.ssl,parseType=eval)
        self.ssl_keyfile = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl_keyfile",self.ssl_keyfile)
        self.ssl_certfile = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl_certfile",self.ssl_certfile)
        self.ssl_cert_reqs = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl_cert_reqs",self.ssl_cert_reqs)
        self.ssl_ca_certs = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl_ca_certs",self.ssl_ca_certs)
        self.ssl_check_hostname = self.config.getPropertyDefault(self.__redis_conf_alias,"ssl_check_hostname",self.ssl_check_hostname,parseType=eval)
        self.max_connections = self.config.getPropertyDefault(self.__redis_conf_alias,"max_connections",self.max_connections,parseType=int)
        self.single_connection_client = self.config.getPropertyDefault(self.__redis_conf_alias,"single_connection_client",self.single_connection_client,parseType=eval)
        self.health_check_interval = self.config.getPropertyDefault(self.__redis_conf_alias,"health_check_interval",self.health_check_interval,parseType=int)
        self.client_name = self.config.getPropertyDefault(self.__redis_conf_alias,"client_name",self.client_name)
        self.username = self.config.getPropertyDefault(self.__redis_conf_alias,"username",self.username)
    
if __name__ == "__main__":
    prueba = RedisTools()
    prueba.setVal("clave","valor")
    print(prueba.getVal("clave"))