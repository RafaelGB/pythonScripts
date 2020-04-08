import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

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


class DashServer(Thread):
    __app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    __host = 'localhost'
    __port = 8050
    __debug = False
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core, *args, **kwargs):
        super(DashServer, self).__init__(*args, **kwargs)
        self.__init_services(core)
        # Local configuration
        self.__dash_conf_alias = self.__config.getProperty("groups", "dash.server")
        self.__dash_conf = self.__config.getGroupOfProperties(
            self.__dash_conf_alias)
        # server configuration
        self.__config__dash_server()
        self.__logger.info(
            "Servicios asociados a servidor Dash declarados correctamente")
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

    def generateLayout(self, 
        components: list = None, 
        extra_callbacks = None):
        # Componentes insertados por la arquitectura
        layoutComponents = [
            arq_navbar,
            arq_alert_shutdown
        ]

        if components != None:
            layoutComponents.extend(components)
        else:
            self.__logger.warn("No se ha asignado ningún componente desde aplicación para el layout")
        self.__app.layout = html.Div(children=layoutComponents)
        self.__logger.debug("Nuevo layout inicializado para servidor Dash")
        self.__callbacks()
        self.__logger.debug("Inicializados callbacks propios de la arquitectura")
        if extra_callbacks != None and callable(extra_callbacks):
            extra_callbacks(self.__app)
            self.__logger.debug("Inicializados callbacks custom")

    def stop_server(self):
        """Detiene el servidor forzando una excepción"""
        self.__raise_exc()

    """
    ----------
    callbacks para servidor DASH
    ----------
    """
    def __callbacks(self):
        @self.__app.callback(
            Output("alert-shutdown", "is_open"),
            [Input('stop-server', 'n_clicks')],
            [State("alert-shutdown", "is_open")])
        def __button_cerrar_servidor(n_clicks, is_down):
            if(n_clicks):
                self.__logger.debug("Servidor dash cerrado desde botón web")
                self.__raise_exc()
                return not is_down
            return is_down
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
        self.__app.run_server(
            host=self.__host,
            port=self.__port,
            debug=self.__debug)

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

# NavBars
# --------------------
arq_navbar = dbc.Navbar(
    [
        dbc.Col(dbc.NavbarBrand("Dashboard", href="#"), sm=3, md=2),
        dbc.Col(dbc.Input(type="search", placeholder="Search here")),
        dbc.Col(dbc.Button("Parar servidor", id="stop-server", color="danger", className="mr-1"),
                ),
    ],
    color="dark",
    dark=True,
)

# Alerts
# --------------------
arq_alert_shutdown = dbc.Alert(
    "¡El servidor ha sido cerrado!",
    id="alert-shutdown",
    dismissable=False,
    fade=True,
    is_open=False,
    color="danger",
)

class DashTools(object):
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core):
        self.__init_services(core)
        # Local configuration
        self.__dash_conf_alias = self.__config.getProperty("groups", "dash.tools")
        self.__dash_conf = self.__config.getGroupOfProperties(
            self.__dash_conf_alias)
        self.__logger.info(
            "Servicios asociados a Herramientas Dash declarados correctamente")
    
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
    
    def alert(self,message:str,id:str,**kwargs):
        """https://dash-bootstrap-components.opensource.faculty.ai/docs/components/alert/"""
        self.__logger.debug("Argumentos para formar un objeto 'alert': %s",kwargs)
        if "id" not in kwargs:
            kwargs['id'] = id
        return dbc.Alert(message,**kwargs)
    
    """
    ----------
    Generador de componentes plantilla
    ----------
    """

    def dataframe_table(self, dataframe, max_rows=10):
        """Genera un componente tabla a partir de un dataframe"""
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

    def plotly_graph(self, plotly_figure,id_graph='plot'):
        """Genera una gráfica a partir de una figura propia de plotly"""
        return dcc.Graph(id=id_graph, figure=plotly_figure)