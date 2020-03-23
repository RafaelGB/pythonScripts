import redis
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
        self.redis_conf_alias = self.config.getProperty("groups","redis")
        self.redis_conf=self.config.getGroupOfProperties(self.redis_conf_alias)
        self.redis = redis.Redis(self, self.host, self.port,
                 self.db, self.password, self.socket_timeout,
                 self.socket_connect_timeout,
                 self.socket_keepalive, self.socket_keepalive_options,
                 self.connection_pool, self.unix_socket_path,
                 self.encoding, self.encoding_errors,
                 self.charset, self.errors,
                 self.decode_responses, self.retry_on_timeout,
                 self.ssl, self.ssl_keyfile, self.ssl_certfile,
                 self.ssl_cert_reqs, self.ssl_ca_certs,
                 self.sl_check_hostname,
                 self.max_connections, self.single_connection_client,
                 self.health_check_interval, self.client_name, self.username)
    
    def setVal(self, key:str, value:str)-> None:
        self.redis.set(key,value)

    def getVal(self, key:str) -> any:
        return self.redis.get(key)
    
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()
    
if __name__ == "__main__":
    prueba = RedisTools()
    prueba.setVal("clave","valor")
    print(prueba.getVal("clave"))