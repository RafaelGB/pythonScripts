# filesystem
import logging
import time

# stadistic
import pandas as pd
import plotly.graph_objs as go

# Own
from arq_server.services.CoreService import Configuration
from arq_server.services.analytics.DashTools import DashTools
from arq_server.base.ArqErrors import ArqError


class StatisticsTools(object):
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration
    __dash: DashTools

    def __init__(self, core, dash):
        self.__init_services(core, dash)
        self.__logger.info("Servicios de estadística arrancados correctamente")

    def pruebas(self):
        self.__dash.start()
        # Step 2. Import the dataset
        df = pd.read_csv(
            "C:/Users/sernn/OneDrive/Desktop/Proyectos/pythonScripts/Arquitectura/arq_server/services/analytics/finance-charts-apple.csv")

        # Step 3. Create a plotly figure
        trace_1 = go.Scatter(x=df.Date, y=df['AAPL.High'],
                             name='AAPL HIGH',
                             line=dict(width=2,
                                       color='rgb(229, 151, 50)'))

        layout = go.Layout(title='Time Series Plot',
                           hovermode='closest')

        fig = go.Figure(data=[trace_1], layout=layout)

        self.__dash.modifyLayout(fig)
        time.sleep(20)
        self.__dash.terminate()
        self.__dash.join()
        print(self.__dash.isAlive())

    def __init_services(self, core, dash) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__dash = dash
