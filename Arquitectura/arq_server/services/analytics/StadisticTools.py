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
        if layout == None:
            layout = default_layout
        fig = None
        try:
            fig = go.Figure(data=data, layout=layout, frames=frames,
                            skip_invalid=skip_invalid, **kwargs)

        except ValueError as val_e:
            self.__logger.error(
                "Error generando una figura plotly: %s", val_e, exc_info=True)
        finally:
            return fig

    def createDashLayout(self, figure=None, components=None, extra_callbacks=None, is_async=False):
        """
        Genera un panel Dash con los componentes propios de un servidor Dash
        """
        dash_thread: DashServer = self.__factories.dash_factory()
        dash_thread.start()
        dash_thread.generateLayout(figure=figure, components=components)
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


#
default_layout = go.Layout(
    title='Points Scored by the Top 9 Scoring NBA Players in 2012',
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=5,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
    showlegend=False
)
