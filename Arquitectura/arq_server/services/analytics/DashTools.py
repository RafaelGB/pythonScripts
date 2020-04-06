import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Multiprocessing
import threading
from threading import Thread
import inspect
import ctypes

# filesystem
import logging

# Own
from arq_server.services.CoreService import Configuration
from arq_server.base.ArqErrors import ArqError


class DashTools(Thread):
    __app = dash.Dash()
    __host = 'localhost'
    __port = 8050
    __debug = False
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration
    
    # function using _stop function 
    def stop(self,force=False):
        self.__logger.debug("parando el servidor DASH")
        self._stop.set()

    def stopped(self): 
        return self._stop.isSet() 
  
    def __raise_exc(self, exctype):
        """raises the given exception type in the context of this thread"""
        _async_raise(self._get_my_tid(), exctype)
    
    def terminate(self):
        """raises SystemExit in the context of the given thread, which should 
        cause the thread to exit silently (unless caught)"""
        self.__raise_exc(SystemExit)

    def run(self): 
        self.__startServer()

    def modifyLayout(self, fig):
        self.__app.layout = html.Div([
            dcc.Graph(id='plot', figure=fig)
        ])

    def __init__(self, core, *args, **kwargs):
        super(DashTools, self).__init__(*args, **kwargs) 
        self.__init_services(core)

        # Local configuration
        self.__dash_conf_alias = self.__config.getProperty("groups", "dash")
        self.__dash_conf = self.__config.getGroupOfProperties(
            self.__dash_conf_alias)
        # server configuration
        self._stop = threading.Event() 
        self.__config__dash_server()
        
        self.__logger.info(
            "Servicios asociados a servidor Dash declarados correctamente")

    def __config__dash_server(self):
        self.__host = self.__config.getPropertyDefault(
            self.__dash_conf_alias, "host", self.__host)
        self.__port = self.__config.getPropertyDefault(
            self.__dash_conf_alias, "port", self.__port, parseType=int)
        self.__debug = self.__config.getPropertyDefault(
            self.__dash_conf_alias, "debug", self.__debug, parseType=eval)
        """
        dev_tools_ui = None,
        dev_tools_props_check = None,
        dev_tools_serve_dev_bundles = None,
        dev_tools_hot_reload = None,
        dev_tools_hot_reload_interval = None,
        dev_tools_hot_reload_watch_interval = None,
        dev_tools_hot_reload_max_retry = None,
        dev_tools_silence_routes_logging = None,
        dev_tools_prune_errors = None,
        **flask_run_options
        """

    def __startServer(self):
        #self.__app.scripts.config.serve_locally = True
        self.__app.run_server(
            host=self.__host,
            port=self.__port,
            debug=self.__debug)
            # Flask properties
            #processes=4,
            #threaded=False)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()

    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")