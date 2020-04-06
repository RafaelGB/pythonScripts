import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output

import multiprocessing
import time

app = dash.Dash(__name__)

app.layout = html.Div([

    dcc.Interval(
        id='interval-component',
        interval=1*10000,  # in milliseconds
        n_intervals=0
    ),

    html.Div([
        daq.Gauge(
            id='gauge-chart',
            value=2,
            max=100,
            min=0,
            units="MPH",
        )
    ])
])


@app.callback(
    Output('gauge-chart', 'value'),
    [Input('interval-component', 'n_intervals')]
)
def update_gauge(n_intervals):
    value = 50
    return value


def startServer(self, dash):
    def run():
        dash.scripts.config.serve_locally = True
        dash.run_server(
            port=8050,
            debug=False,
            processes=4,
            threaded=False
        )

    # Run on a separate process so that it doesn't block
    self.server_process = multiprocessing.Process(target=run)
    self.server_process.start()
    time.sleep(0.5)

    # Visit the dash page
    self.driver.get('http://localhost:8050')
    time.sleep(0.5)


startServer(app)