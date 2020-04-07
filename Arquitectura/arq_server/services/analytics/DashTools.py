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
    __app = dash.Dash(__name__, external_stylesheets=[
                      'https://codepen.io/chriddyp/pen/bWLwgP.css'])
    __host = 'localhost'
    __port = 8050
    __debug = False
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core, *args, **kwargs):
        super(DashTools, self).__init__(*args, **kwargs)
        self.__init_services(core)
    """
    ----------
    Interacciones con el servidor
    ----------
    """

    def run(self):
        """
        Arranque del servidor junto con el arranque del hilo
        """
        try:
            self.__startServer()
        except self.ThreadStopped:
            pass
        finally:
            self.__logger.debug(
                "El servidor dash se ha detenido correctamente")

    def generateLayout(self, figure=None,components:list=None):
        
        layoutComponents = []
        if components != None:
            layoutComponents.extend(components)

        if figure != None:
            layoutComponents.append(dcc.Graph(id='plot', figure=figure))
            
        self.__app.layout = html.Div(children=layoutComponents)

        # Local configuration
        self.__dash_conf_alias = self.__config.getProperty("groups", "dash")
        self.__dash_conf = self.__config.getGroupOfProperties(
            self.__dash_conf_alias)
        # server configuration
        self.__config__dash_server()

        self.__logger.info(
            "Servicios asociados a servidor Dash declarados correctamente")

    def stop_server(self):
        """Detiene el servidor forzando una excepción"""
        self.__raise_exc()

    """
    ----------
    Generador de componentes
    ----------
    """

    def generate_table(self, dataframe, max_rows=10):
        return html.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ])
    """
    ----------
    Funciones privadas
    ----------
    """

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
        # processes=4,
        # threaded=False)

    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()

    class ThreadStopped(Exception):
        pass

    def __raise_exc(self):
        thread_id = self.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(self.ThreadStopped))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
