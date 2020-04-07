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

    def __init__(self, core, factories):
        self.__init_services(core, factories)
        self.__logger.info("Servicios de estadística arrancados correctamente")

    def pruebas(self):
        dash_thread: DashTools = self.__factories.dash_factory()
        dash_thread.start()
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
        components = []

        components.append(dash_thread.generate_table(df,max_rows=50))
        dash_thread.generateLayout(figure=fig,components=components)
        dash_thread.join()

    def __init_services(self, core, factories) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__factories = factories
