import random
import time
# Threads
from threading import current_thread

# system
import logging

# Concurrencia
import multiprocessing
import rx
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops

# Own
from arq_server.services.CoreService import Configuration

def intense_calculation(value):
    # sleep for a random short duration between 0.5 to 2.0 seconds to simulate a long-running calculation
    time.sleep(random.randint(5, 20) * 0.1)
    return value

class ConcurrentTools(object):
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core, *args, **kwargs):
        self.__init_services(core)
        self.__init_default_actions()
        self.__optimal_thread_count = multiprocessing.cpu_count()
        self.__pool_scheduler = ThreadPoolScheduler(self.__optimal_thread_count)
        self.__logger.info("Herramientas RX de concurrencia cargadas correctamente")

    def createProcess(
        self,func,*args: any,
        on_next=None,
        on_error=None,
        on_completed=None):
        """
        Genera un proceso en un hilo a parte para la función pasada como parámetro. 
        Ejecutará secuencialmente los argumentos *args. Existe una lógica de logging
        por defecto para las acciones 'on_next', 'on_error' y 'on_complete', permitiendo
        ser modificada si se desea
        """
        rx.of(*args).pipe(
            ops.map(lambda s: func(s)), ops.subscribe_on(self.__pool_scheduler)
        ).subscribe(
            on_next=(on_next, self.__on_next_default)[on_next==None],
            on_error=(on_error, self.__on_error_default)[on_error==None],
            on_completed=(on_completed, self.__on_completed_default)[on_completed==None],
        )
    
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
    
    def __init_default_actions(self):
        self.__on_next_default = lambda nextArg: self.__logger.debug(
            "Proceso en hilo %s - siguiente argumento:'%s'",
            current_thread().name,
            nextArg
            )
        
        self.__on_error_default = lambda e: self.__logger.error(
            "Error durante la ejecución del hilo %s : %s",
            current_thread().name,
            e
            )
        
        self.__on_completed_default = lambda: self.__logger.debug(
            "¡Proceso en el hilo %s completado!",
            current_thread().name
            )
"""        
# calculate number of CPUs, then create a ThreadPoolScheduler with that number of threads
optimal_thread_count = multiprocessing.cpu_count()
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)

# Create Process 1
rx.of("Alpha", "Beta", "Gamma", "Delta", "Epsilon").pipe(
    ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
).subscribe(
    on_next=lambda s: print("PROCESS 1: {0} {1}".format(current_thread().name, s)),
    on_error=lambda e: print(e),
    on_completed=lambda: print("PROCESS 1 done!"),
)

# Create Process 2
rx.range(1, 10).pipe(
    ops.map(lambda s: intense_calculation(s)), ops.subscribe_on(pool_scheduler)
).subscribe(
    on_next=lambda i: print("PROCESS 2: {0} {1}".format(current_thread().name, i)),
    on_error=lambda e: print(e),
    on_completed=lambda: print("PROCESS 2 done!"),
)

# Create Process 3, which is infinite
rx.interval(1).pipe(
    ops.map(lambda i: i * 100),
    ops.observe_on(pool_scheduler),
    ops.map(lambda s: intense_calculation(s)),
).subscribe(
    on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
    on_error=lambda e: print(e),
)

input("Press any key to exit\n")
"""
if __name__ == "__main__":
    if None:
        print("hola")