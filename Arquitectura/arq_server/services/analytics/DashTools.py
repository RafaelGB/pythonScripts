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
import base64
import io

# dataframe
import pandas as pd

# Own
from arq_server.services.CoreService import Configuration
from arq_server.base.ArqErrors import ArqError

#Temp
import plotly.graph_objs as go

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

    """
    ----------
    Generador de componentes bootstrap
    ----------
    """
    def alert(self,message:str,id:str,**kwargs):
        """
        Genera un objeto de tipo alerta propio de bootstrap. Mensaje e id son campos obligatorios.

        https://dash-bootstrap-components.opensource.faculty.ai/docs/components/alert/
        """
        self.__logger.debug("Argumentos para formar un objeto 'alert': %s",kwargs)
        if "id" not in kwargs:
            kwargs['id'] = id
        return dbc.Alert(message,**kwargs)
    
    """
    ----------
    Generador de componentes html
    ----------
    """
    def upload_file_component(self,id='upload-data',multiple=True):
        return dcc.Upload(
                id=id,
                children=html.Div([
                    'Arrastrar aquí o ',
                    html.A('selecciona un fichero')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Permite subir múltiples ficheros
                multiple=multiple
            )

    def dataframe_table_component(self, dataframe, max_rows=10):
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

    def graph_component(self, figure,id_graph='main-graph'):
        """Genera una gráfica a partir de una figura propia de plotly"""
        return dcc.Graph(id=id_graph, figure=figure)


class DashServer(Thread):
    # Default server conf
    __app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    __host = 'localhost'
    __port = 8050
    __debug = False
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration
    __tools: DashTools
    # figure elements
    __main_figure = dcc.Graph(id='main-graph')

    def __init__(self, core, tools, *args, **kwargs):
        super(DashServer, self).__init__(*args, **kwargs)
        self.__init_services(core,tools)
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
        figure=None, 
        components: list = None, 
        extra_callbacks = None):
        if figure == None:
            figure = dcc.Graph(id='main-graph')
        # Componentes insertados por la arquitectura
        layoutComponents = [
            arq_navbar,
            self.__tools.alert(
                "¡El servidor ha sido cerrado!",
                "alert-shutdown",
                dismissable=False,
                fade=True,
                is_open=False,
                color="danger"
                ),
            self.__tools.upload_file_component(),
            figure
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
        
        @self.__app.callback(Output('main-graph', 'figure'),
            [
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ])
        def __update_graph(contents, filename):

            if contents:
                contents = contents[0]
                filename = filename[0]
                df = self.__parse_data(contents, filename)
                #df = df.set_index(df.columns[0])
                trace = go.Scatter(
                    x = df['Date'], y = df['AAPL.Open'],
                    mode = "lines",
                    name = "prueba"
                    )
                self.__main_figure = go.Figure(data=[trace])
            return self.__main_figure
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

    def __init_services(self, core,tools) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__tools = tools

    class ThreadStopped(Exception):
        pass

    def __raise_exc(self):
        thread_id = self.ident
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(self.ThreadStopped))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
    
    def __parse_data(self,contents, filename):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV or TXT file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
            elif 'txt' or 'tsv' in filename:
                # Assume that the user upl, delimiter = r'\s+'oaded an excel file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')), delimiter = r'\s+')
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return df
# NavBars
# --------------------
arq_navbar = dbc.Navbar(
    [
        dbc.Col(dbc.NavbarBrand("Dashboard", href="#"), sm=3, md=2),
        dbc.Col(dbc.Input(type="search", placeholder="Search here")),
        dbc.Col(dbc.Button("Parar servidor", id="stop-server", color="danger", className="mr-1"))
    ],
    color="dark",
    dark=True
)