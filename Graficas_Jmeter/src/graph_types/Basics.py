import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import cufflinks as cf

from re import sub
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

class Template_graphs():
   # Variables propias de la clase
  colors = {
    "red":'r'
  }
  file_extention_tuple = ('.csv','.CSV')
  """
  FUNCIONES PROPIAS DE CLASE
  """
  def __init__(self,filename,configMap, *args, **kwargs):
    self.filename = filename
    self.df = pd.read_csv(filename)
    self.__dataTreatment()
    self.properties = configMap
    
  """
  *************
  PARTE PÚBLICA
  *************
  """
  def latencyGraph(self,**kwargs):
      """
      Gráfica orientada a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """
      traceLatency = self.__customTrace(self.df['date'],
                                        self.df['Latency'],
                                        mode = 'lines',
                                        name=self.properties['FILENAMES']['trace_latency_name'],
                                        color=self.colors["red"])
      layout = go.Layout(
                      title='Gráfica',
                      plot_bgcolor='rgb(230, 230,230)', 
                      showlegend=True
                      )
      fig = go.Figure(data=[traceLatency], layout=layout)
      filename = self.__formatFilename("grafica_latencia_csv-",self.filename)
      plot(fig, filename=filename)

  def boxplot_plotly(self,**kwargs):
      """
      Boxplot orientado a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """
      cf.set_config_file(offline=True, world_readable=True, theme='ggplot')
      # Inicio de la lógica de la función
      layout = go.Layout(title="Boxplot",font=dict(family='Courier New, monospace', size=18, color='rgb(0,0,0)'))
      # Define el boxplot
      latencia = self.__customBoxplot(self.df['sentBytes'],self.df['Latency'],showlegend=True,name='Latencia de respuesta')
      # Define el nombre del fichero
      filename = self.__formatFilename("boxplot_latencia_csv-",self.filename)
      plot({
            "data": [latencia], 
            "layout": layout
            },
            filename=filename
          )

  def boxplot_seaborn(self,**kwargs):
      """
      Dibujo con la información de agregación relevante de la gráfica
      Devuelve una imagen en el formato configurado
      """
      # Inicialización de variables a uso local
      myFig = plt.figure()
      bp = sns.boxplot(x='sentBytes', y='Latency', data=self.df)
      bp = sns.stripplot(x='sentBytes', y='Latency', data=self.df, color="orange", jitter=0.1, size=1.5)
      # Maquetado de la gráfica para interpretación legible de los resultados
      plt.title("Muestreo", loc="left")
      plt.xlabel("Bytes enviados")
      plt.ylabel("Latencia (milisegundos)")
      myFig.savefig(self.properties["FILENAMES"]["boxplot_image_name"]+"."+self.properties["FILE_FORMATS"]["boxplot_format"],
                    format=self.properties["FILE_FORMATS"]["boxplot_seaborn_format"])
  """
  *************
  PARTE PRIVADA
  *************
  """
  def __dataTreatment(self):
    """
    Se añaden los datos de valor necesarios sobre el dataframe propio de la clase
    """
    self.df['date'] = pd.to_datetime(self.df['timeStamp'], unit='ms')
    self.df['date'] = pd.to_datetime(self.df['date'], format='%d/%b/%Y:%H:%M:%S', utc=True)
  
  def __formatFilename(self,label,filename):
    """
    Dada una etiqueta y un nombre de fichero, se forma el nombre final del html
    """
    for endRegex in self.file_extention_tuple:
          filename = sub(endRegex+'$', '.html', filename)
    return label+filename

  def __customBoxplot(self,Xaxis,Yaxis,**kwargs):
    """
    Calculo del boxplot con la información más relevante en funcion de los siguientes 
    parametros de entrada
    Xaxis : eje de la x
    Yaxis : eje de la y
    """
    boxplot = go.Box(x=Xaxis,y=Yaxis,
                    showlegend=(True,kwargs["showlegend"])["showlegend" in kwargs],
                    name=('Boxplot',kwargs["name"])["name" in kwargs],
                    boxpoints='all',
                    jitter=0.3
                    )
    return boxplot

  def __customTrace(self,Xaxis,Yaxis,**kwargs):
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

  def __constructAggregations(self):
    """
    Genera el menú con las posibles agregaciones sobre la gráfica
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