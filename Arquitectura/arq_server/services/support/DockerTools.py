import docker

# system
import sys, os
import pathlib
import logging
# IoC
from arq_server.services.CoreService import Configuration



class DockerTools(object):
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, *args, **kwargs):
        self.__init_client()
        #self.__init_services(core)
        #self.__logger.info("API herramientas Docker cargada correctamente")
    
    def runContainer(
        self, image, name:str, auto_remove:bool=False, detach:bool=False, 
        command:str=None, port:dict=None, volumes:dict=None
        ):
        """
        Arranca un contenedor a partir de la imagen dada como argumento.
        El nombre es obligatorio para gestionar internamente los contenedores activos
        """
        conf = {
            "name":name,
            "auto_remove":auto_remove,
            "detach":detach
            }

        if command:
            conf['command'] = command
        if port:
            conf['port'] = port
        if port:
            conf['volumes'] = volumes

        self.__client.containers.run(
            image,
            **conf
            )
        
        container = self.__client.containers.get("my-redis")
        print(container.logs())
        container.stop()


    def __init_client(self):
        self.__client = client = docker.from_env()
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()


if __name__ == "__main__":
    docker_api = DockerTools()
    docker_api.runContainer("custom/redis:1.0.0")