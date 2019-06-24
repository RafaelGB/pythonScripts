import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from re import sub
colors = {
  "red":'r'
}

file_extention_tuple = ('.csv','.CSV')

"""
*************
PARTE PÚBLICA
*************
"""
def latencyGraph(**kwargs):
    """
    Gráfica orientada a tiempos de respuesta
    devuelve un fichero html para una consulta interactiva de la información
    """
    # Inicialización de variables a uso local
    global colors
    global file_extention_tuple
    df = kwargs["df"]
    confMap = kwargs["configMap"]
    filename = kwargs["filename"]
    # Inicio de la lógica de la función
    df['date'] = pd.to_datetime(df['timeStamp'], unit='ms')
    df['date'] = pd.to_datetime(df['date'], format='%d/%b/%Y:%H:%M:%S', utc=True)

    traceLatency = customTrace(df['date'],df['Latency'],mode = 'lines',name=confMap['FILENAMES']['trace_latency_name'],color=colors["red"])
    layout = go.Layout(
                    title='Gráfica',
                    plot_bgcolor='rgb(230, 230,230)', 
                    showlegend=True
                    )
    fig = go.Figure(data=[traceLatency], layout=layout)
    for endRegex in file_extention_tuple:
        filename = sub(endRegex+'$', '.html', filename)
    py.plot(fig, filename=filename)

def box_plotGraph(**kwargs):
    """
    Dibujo con la información de agregación relevante de la gráfica
    Devuelve una imagen en el formato configurado
    """
    # Inicialización de variables a uso local
    df = kwargs["df"]
    confMap = kwargs["configMap"]
    myFig = plt.figure()
    bp = sns.boxplot(x='sentBytes', y='Latency', data=df)
    bp = sns.stripplot(x='sentBytes', y='Latency', data=df, color="orange", jitter=0.1, size=1.5)
    # Maquetado de la gráfica para interpretación legible de los resultados
    plt.title("Muestreo", loc="left")
    plt.xlabel("Bytes enviados")
    plt.ylabel("Latencia (milisegundos)")
    myFig.savefig(confMap["FILENAMES"]["boxplot_image_name"]+"."+confMap["FILE_FORMATS"]["boxplot_format"],
                  format=confMap["FILE_FORMATS"]["boxplot_format"])
"""
*************
PARTE PRIVADA
*************
"""
def customTrace(Xaxis,Yaxis,**kwargs):
  """
  Calculo de traza en el esquema estadistico en funcion de los siguientes parametros de entrada
  Xaxis : eje de la x
  Yaxis : eje de la y
  """
  trace = go.Scatter(
          x = Xaxis, y = Yaxis,
          mode = ("lines",kwargs["mode"])["mode" in kwargs],
          name = ("no name",kwargs["name"])["name" in kwargs]
          )
  return trace

def constructAggregations():
  """
  Genera el menú con las posibles agregaciones sobre la gráfca
  """
  aggs = ["count","sum","avg","median","mode","rms","stddev","min","max","first","last"]
  agg = []
  agg_func = []
  for i in range(0, len(aggs)):
    agg = dict(
        args=['transforms[0].aggregations[0].func', aggs[i]],
        label=aggs[i],
        method='restyle'
    )
    agg_func.append(agg)
  return agg_func