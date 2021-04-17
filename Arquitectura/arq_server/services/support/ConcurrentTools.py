# Threads
from threading import current_thread
# system
import logging
import traceback

# Concurrencia
import concurrent.futures
import multiprocessing
import rx
from rx.scheduler import ThreadPoolScheduler
from rx.core.typing import Disposable
from rx import Observable, operators as ops

# Own
from arq_server.services.CoreService import Configuration, ContextFilter

    
class ConcurrentTools(object):
    _logger: logging.Logger
    _config: Configuration

    def __init__(self, core, *args, **kwargs):
        self.__init_services(core)
        optimal_thread_count = multiprocessing.cpu_count()
        self.__pool_scheduler = ThreadPoolScheduler(optimal_thread_count)
        self._logger.info(
            "Herramientas RX de concurrencia cargadas correctamente. pool de %d hilos",
            optimal_thread_count
            )

    def createProcess(
        self,func,*args,
        on_next=None,
        on_error=None,
        on_completed=None):
        """
        Genera un proceso en un hilo a parte para la función pasada como parámetro. 
        Ejecutará secuencialmente los argumentos *args. Existe una lógica de logging
        por defecto para las acciones 'on_next', 'on_error' y 'on_complete', permitiendo
        ser modificada si se desea
        """
        self._logger.info("Generando nuevo proceso")
        sequence: Observable = rx.of(*args)

        # TODO potencialmente se podrían añadir por parámetro más operaciones
        operators = [
            ops.map(lambda s: func(s)),
            ops.subscribe_on(self.__pool_scheduler)
            ]

        stream: Observable = sequence.pipe(
            *operators
        )
         
        def on_next_default(nextArg):
            self._logger.debug("Resultado obtenido:'%s'",str(nextArg))
        
        def on_error_default(error):
            strTb = ''.join(traceback.format_tb(error))
            print(strTb)
            self._logger.exception("Traceback: %s",strTb)
        
        def on_complete_default():
            self._logger.debug("¡Proceso completado!")

        disposableStream: Disposable = stream.subscribe(
            on_next=(on_next, on_next_default)[on_next==None],
            on_error=(on_error, on_error_default)[on_error==None],
            on_completed=(on_completed, on_complete_default)[on_completed==None]
        )
        
        self._logger.info("Proceso %s creado",func.__name__)

    
    """
    Información relevante
    """
    def current_thread_name(self) -> str:
        """Devuelve el nombre del hilo de la ejecución que convoque esta función"""
        return current_thread().name

    """
    Funciones de inicialización
    """
    def __init_services(self, core) -> None:
        # Servicio de logging
        self._logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
    
