# filesystem
import logging
import time

# stadistic
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# Own
from arq_server.services.CoreService import Configuration
from arq_server.services.analytics.DashTools import DashServer
from arq_server.base.ArqErrors import ArqError
from arq_decorators.service_decorator import ServiceBase


class StatisticsTools(object):
    # Services TIPS
    __logger: logging.getLogger()
    __config: Configuration

    def __init__(self, core, factories):
        self.__init_services(core, factories)
        self.__logger.info("Servicios de estadística arrancados correctamente")

    def generate_figure(self, data=None, layout=None, frames=None, skip_invalid=False, **kwargs):
        """
        Genera una figura plotly bajo el layout de la arquitectura por defecto.
        """
        fig = {}
        try:
            fig = go.Figure(data=data, layout=layout, frames=frames,
                            skip_invalid=skip_invalid, **kwargs)

        except ValueError as val_e:
            self.__logger.error(
                "Error generando una figura plotly: %s", val_e, exc_info=True)
        finally:
            return fig

    def createDashServer(self, layout, treatment_callback, components=None, extra_callbacks=None, is_async=False):
        """
        Genera un panel Dash con los componentes propios de un servidor Dash
        """
        dash_thread: DashServer = self.__factories.dash_factory()
        dash_thread.start()
        # INI temp
        def prueba(df):
            trace = go.Scatter(
                x=df['Date'], y=df['AAPL.Open'],
                mode="lines",
                name="prueba"
            )
            return [trace]
        treatment_callback = prueba
        layout = None
        # FIN temp
        dash_thread.config_treatment_data(layout, treatment_callback)
        dash_thread.generateLayout(
            components=components, extra_callbacks=extra_callbacks)
        if not is_async:
            dash_thread.join()

    def __init_services(self, core, factories) -> None:
        # Servicio de logging
        self.__core = core
        self.__logger = core.logger_service().arqLogger()
        self.__config = core.config_service()
        self.__factories = factories

    class Normalizers(ServiceBase):
        def granularity(self, colValue: int, granularity=0.9):
            """
            Para un columna cuyo valor sea numérico, proporciona granularidad ( por defecto 1 )
            """
            if str(colValue) == "nan":
                return np.nan
            timeStamp = timeStamp // granularity
            timeStamp = timeStamp * granularity
            return timeStamp
