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
    __isEnabled:bool = eval(Metadata.getInfo()['enabled.modules']['docker'])
    __logger: logging.Logger
    __config: Configuration

    def __init__(self, core, *args, **kwargs):
        self.__init_services(core)
        self.__logger.debug("Módulo DockerTools isEnabled:%s",str(self.__isEnabled))
        self.__init_client()
        self.__docker_conf_alias = self.__config.getProperty("groups", "docker")
        self.__dockerLogsPath = self.__config.getProperty("docker","path.docker.logs",confKey=self.__docker_conf_alias)

    
    @enableFunction(__isEnabled,className='DockerTools')
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
        
    @enableFunction(__isEnabled,className='DockerTools')
    def stopContainer(self,name) -> bool:
        isStoped:bool=False
        try:
            container = self.__client.containers.get(name)
            container.stop()
            self.__logger.debug("el contenedor %s fué detenido",name)
            isStoped=True
        except NotFound as not_found_e:
            raise ArqError(not_found_e.response)
        finally:
            return isStoped

    @enableFunction(__isEnabled,className='DockerTools')
    def removeContainer(self, name) -> bool:
        isRemoved:bool = False
        try:
            container = self.__client.containers.get(name)
            if container.status == "running":
                self.stopContainer(name)
                container = self.__client.containers.get(name)
            container.remove()
            isRemoved=True
            self.__logger.debug("el contenedor %s fué eliminado", name)
        except NotFound as not_found_e:
            self.__logger.error("El contenedor %s no se encuentra o ya ha sido eliminado", name)
        finally:
            return isRemoved

    def __streamContainerLogs(self, name, container):
        dateInfo = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        logPath = "{}\\{}__{}.log".format(self.__dockerLogsPath,name,dateInfo)
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

    @enableFunction(__isEnabled,className='DockerTools')
    def __init_client(self):
        self.__client = docker.from_env()
        self.__logger.info("API herramientas Docker cargada correctamente")
        
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()      