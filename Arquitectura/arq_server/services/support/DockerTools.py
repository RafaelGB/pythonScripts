import docker
from docker .errors import NotFound, APIError
# system
import sys, os
import pathlib
import logging
from datetime import datetime
# MultiThreading
from threading import Thread
# Own
from arq_decorators.service_decorator import enableFunction
from arq_server.services.CoreService import Configuration
from arq_server.base.ArqErrors import ArqError
from arq_server.base.Metadata import Metadata

class DockerTools(object):
    __isEnabled:bool = bool(Metadata.info()['enabled.modules']['docker'])
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core, *args, **kwargs):
        self.__init_services(core)
        self.__init_client()
        self.__dockerLogsPath = self.__config.getProperty("docker","path.docker.logs")

    
    @enableFunction(__isEnabled)
    def runContainer(
        self, image, name:str, auto_remove:bool=False, detach:bool=False, 
        command:str=None, ports:dict=None, volumes:dict=None
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
        if ports:
            conf['ports'] = ports
        if ports:
            conf['volumes'] = volumes

        self.__logger.debug("generando contenedor '%s' a partir de la imagen '%s'",name,image)
        self.__logger.debug("configuración recogida para generar el contenedor: %s",conf)

        self.__client.containers.run(
            image,
            **conf
            )

        self.__logger.debug("Contenedor '%s' generado",name)
        c = self.__client.containers.get(name)
        streamLogsThread = Thread(target = self.__streamContainerLogs, args = (name,c, ))
        streamLogsThread.start()
        
    @enableFunction(__isEnabled)
    def stopContainer(self,name) -> bool:
        try:
            container = self.__client.containers.get(name)
            container.stop()
            self.__logger.debug("el contenedor %s fué detenido",name)
        except NotFound as not_found_e:
            raise ArqError(101)

    @enableFunction(__isEnabled)
    def removeContainer(self, name) -> bool:
        try:
            container = self.__client.containers.get(name)
            if container.status == "running":
                self.stopContainer(name)
                container = self.__client.containers.get(name)
            container.remove()
            self.__logger.debug("el contenedor %s fué eliminado", name)
        except NotFound as not_found_e:
            self.__logger.error("El contenedor %s no se encuentra o ya ha sido eliminado", name)

    def __streamContainerLogs(self, name, container):
        dateInfo = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        logPath = "{}\{}__{}.log".format(self.__dockerLogsPath,name,dateInfo)
        f=open(logPath,"wb")
        self.__logger.debug("Generando un stream de logs para el contenedor %s en la ruta %s",name,logPath)
        try:
            for l in container.logs(stream=True):
                f.write(l)
        except Exception as e:
            self.__logger.error("Error durante el stream a fichero de los logs del contenedor %s",name)
            print(e)
            
        finally:
            f.close()

    @enableFunction(__isEnabled)
    def __init_client(self):
        self.__client = docker.from_env()
        self.__logger.info("API herramientas Docker cargada correctamente")
        
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()


if __name__ == "__main__":
    docker_api = DockerTools()
    docker_api.runContainer(
        "custom/redis:1.0.0",
        "my-redis",
        auto_remove=True,
        detach=True,
        command="redis-server --appendonly yes",
        ports={"6379/tcp":"6379"},
        volumes={'redis-persist': {'bind': '/data', 'mode': 'rw'}})
    docker_api.removeContainer("my-redis")        