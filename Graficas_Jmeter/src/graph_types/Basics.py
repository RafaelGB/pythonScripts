import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import cufflinks as cf

from re import sub
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from itertools import tee
from functools import partial

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
    # Inicialización de variables globales
    self.filename = filename
    self.properties = configMap
    self.source_chunk = pd.DataFrame()  
    
  """
  *************
  PARTE PÚBLICA
  *************
  """
  def run_by_parts(self,func_to_exec,**kwargs):
    """
    Lectura y filtrado basico del fichero CSV
    """
    customChunkSize = int(self.properties["CSV_READER"]["chunk_size"])
    result = pd.DataFrame()
    # Se generan 2 iteradores , uno para la barra de carga y otro para elctura de datos
    df,chunck_count = tee(pd.read_csv(self.filename,error_bad_lines=False,
                                      warn_bad_lines=False, chunksize=customChunkSize,
                                      low_memory=False))
    count_of_chunks = self.__getNumberOfChunks(chunck_count)
    del chunck_count
    # Llamada inicial pintando 0% de progreso
    print("Se inicia la lectura del fichero\n******************")
    self.__printProgressBar(0,count_of_chunks)
    for index,chunk in enumerate(df):
        chunk = self.__parse_dataframe(chunk) # Parsea datos actuales
        chunk = self.__dataTreatment(chunk) # Añade informacion al datagrama
        #chunk.dropna(axis=0, inplace=True) # Borra las lineas con valores nulos
        self.source_chunk = chunk
        self.source_num_chunk = str(index)
        
        self.__run_selected_func(func_to_exec,**kwargs)
        result = result.append(chunk)
        # Actualiza la barra de carga
        self.__printProgressBar(index + 1,count_of_chunks)
    del df
  
  def obtainUniqueValuesFromColumn(self,**kwargs):
    """
    Dado el nombre d euna columna pasada por consola, obtiene todos 
    los valores únicos y el número de veces que aparecen
    """
    print("dentro")
    # Lectura y tratamiento del datagrama
    self.df = self.__custom_read_csv_file()
    # Inicio de la funcion
    column = str(kwargs["--column"].not_files[0])
    if column is None:
      print("Error: El valor de la columna no se ha introducido")
      print("Método de uso: JMeterGraphs.py tipoGrafica fichero.csv nombreColumna")
      return None

    if column not in self.df:
      print("Error: La columna no existe en el dataframe")
      return None

    filename = self.properties["FILENAMES"]["unique_value_counts"]+"_"+column+".txt"
    f= open(filename,"w+")
    table = self.df[column].value_counts()
    f.write(str(table))
    f.close()

  def latencyGraph(self,**kwargs):
      """
      Gráfica orientada a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """      
      traceLatency = self.__customTrace(self.source_chunk['date'],
                                        self.source_chunk['Latency'],
                                        mode = self.properties['GRAPHICS']['scatter_mode'],
                                        name=self.properties['FILENAMES']['trace_latency_name'],
                                        color=self.colors["red"])
      layout = go.Layout(
                      title='Gráfica',
                      plot_bgcolor='rgb(230, 230,230)', 
                      showlegend=True
                      )
      fig = go.Figure(data=[traceLatency], layout=layout)
      filename = self.__formatFilename("chunk"+self.source_num_chunk+"grafica_latencia_csv-",self.filename)
      plot(fig, filename=filename)

  def responseCodeGraph(self,**kwargs):
      """
      Gráfica orientada a exponer los tipos de respuesta devueltas
      por el servidor a lo largo del tiempo
      """
      traceLatency = self.__customTrace(self.source_chunk['date'],
                                        self.source_chunk['responseCode'],
                                        mode = self.properties['GRAPHICS']['scatter_mode'],
                                        name=self.properties['FILENAMES']['trace_server_response_name'],
                                        color=self.colors["red"])
      layout = go.Layout(
                      title='Gráfica',
                      plot_bgcolor='rgb(230, 230,230)', 
                      showlegend=True
                      )
      fig = go.Figure(data=[traceLatency], layout=layout)
      filename = self.__formatFilename("chunk"+self.source_num_chunk+"grafica_responseCode_csv-",self.filename)
      plot(fig, filename=filename)

  def boxplot_plotly(self,**kwargs):
      """
      Boxplot orientado a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """
      # Lectura y tratamiento del datagrama
      self.df = self.__custom_read_csv_file()
      # Inicio del boxplot 
      y = str(kwargs["--column"].not_files[0])
      if y is None:
        print("Error: El valor de la columna no se ha introducido")
        print("Método de uso: JMeterGraphs.py tipoGrafica fichero.csv nombreColumna")
        return None

      if y not in self.df:
        print("Error: La columna no existe en el dataframe")
        return None
      
      cf.set_config_file(offline=True, world_readable=True, theme='ggplot')
      # Inicio de la lógica de la función
      layout = go.Layout(title="Boxplot",font=dict(family='Courier New, monospace', size=18, color='rgb(0,0,0)'))
      # Define el boxplot
      latencia = self.__customBoxplot(self.df[y],self.df['Latency'],showlegend=True,name=self.properties['BOXPLOT_PLOTLY']['trace_latency_name'])
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
      # Lectura y tratamiento del datagrama
      self.df = self.__custom_read_csv_file()
      # Inicialización de variables a uso local
      myFig = plt.figure()
      bp = sns.boxplot(x='sentBytes', y='Latency', data=self.df)
      bp = sns.stripplot(x='sentBytes', y='Latency', data=self.df, color="orange", jitter=0.1, size=1.5)
      # Maquetado de la gráfica para interpretación legible de los resultados
      plt.title("Muestreo", loc="left")
      plt.xlabel("Bytes enviados")
      plt.ylabel("Latencia (milisegundos)")
      myFig.savefig(self.properties["BOXPLOT_SEABORN"]["image_name"]+"."+self.properties["BOXPLOT_SEABORN"]["image_format"],
                    format=self.properties["BOXPLOT_SEABORN"]["image_format"])
  """
  *************
  PARTE PRIVADA
  *************
  """  
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
    # Configuración según valores de entrada
    custom_boxmean = None
    if "boxmean" in kwargs:
      custom_boxmean = kwargs["boxmean"]
    custom_name = None
    if "name" in kwargs:
      custom_name = kwargs["name"]
    custom_showlegend = None
    if "showlegend" in kwargs:
      custom_showlegend = kwargs["showlegend"]
    # Creación del boxplot
    boxplot = go.Box(x=Xaxis,y=Yaxis,
                    showlegend=(True,custom_showlegend)["showlegend" in kwargs],
                    name=('Boxplot',custom_name)["name" in kwargs],
                    boxpoints=False,
                    jitter=0.3,
                    boxmean=(True,custom_boxmean)["boxmean" in kwargs]
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

  def __custom_read_csv_file(self):
    """
    Lectura y filtrado basico del fichero CSV
    """
    customChunkSize = int(self.properties["CSV_READER"]["chunk_size"])
    result = pd.DataFrame()
    # Se generan 2 iteradores , uno para la barra de carga y otro para elctura de datos
    df,chunck_count = tee(pd.read_csv(self.filename,error_bad_lines=False,
                                      warn_bad_lines=False, chunksize=customChunkSize,
                                      low_memory=False))
    count_of_chunks = self.__getNumberOfChunks(chunck_count)
    del chunck_count
    # Llamada inicial pintando 0% de progreso
    print("Se inicia la lectura del fichero\n******************")
    self.__printProgressBar(0,count_of_chunks)
    for index,chunk in enumerate(df):
        chunk = self.__parse_dataframe(chunk) # Parsea datos actuales
        chunk = self.__dataTreatment(chunk) # Añade informacion al datagrama
        #chunk.dropna(axis=0, inplace=True) # Borra las lineas con valores nulos
        result = result.append(chunk)
        # Actualiza la barra de carga
        self.__printProgressBar(index + 1,count_of_chunks)
    del df
    return result

  def __printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Se llama en un loop para crear una barra de progreso por terminal
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    format_iteration = 0 if (iteration == 0) else (iteration / total)
    percent = ("{0:." + str(decimals) + "f}").format(100 * format_iteration)
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
  
  def __dataTreatment(self,chunk):
    """
    Se añaden los datos de valor necesarios sobre el dataframe propio de la clase
    """
    chunk['date'] = pd.to_datetime(chunk['timeStamp'], unit='ms')
    chunk['date'] = pd.to_datetime(chunk['date'], format='%d/%b/%Y:%H:%M:%S', utc=True)
    return chunk
  
  def __parse_dataframe(self,chunk):
    """
    Una vez cargado el dataframe se realizan comprobaciones para su usabilidad
    """
    # Agrupa los diferentes errores ajenos a la peticion rest como error de conexion
    chunk['responseCode'] = chunk['responseCode'].map(lambda x: None if not str(x).isdigit() or x is None else int(x))
    chunk['responseCode'] = chunk['responseCode'].map(lambda x: None if x >600 or x < 100 else x)
    chunk = chunk.dropna(subset=['responseCode'])
    # Descarta timestamps que hayan podido ser recortados o carezcan de sentido
    chunk['timeStamp'] = chunk['timeStamp'].map(lambda x: None if len(str(x)) != 13 or not str(x).isdigit()  else x)
    chunk = chunk.dropna(subset=['timeStamp'])
    return chunk
  
  def __getNumberOfChunks(self,reader):
    """
    Dado un fileReader te devuelve el numero de apartados que tiene
    """
    number_of_chunks=0
    for chunk in reader:
      number_of_chunks=number_of_chunks+1
    return number_of_chunks
  
  def __run_selected_func(self,func,**kwargs):
    switcher = {
          "latencia": partial(self.latencyGraph,**kwargs),
          "response_code": partial(self.responseCodeGraph,**kwargs),
          "boxplot_seaborn": partial(self.boxplot_seaborn,**kwargs),
          "boxplot_plotly": partial(self.boxplot_plotly,**kwargs),
          "valores_unicos": partial(self.obtainUniqueValuesFromColumn,**kwargs),
    }
    func = switcher.get(func, lambda: "Función no definida")
    return func()