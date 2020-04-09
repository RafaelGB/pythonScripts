import os
import copy

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

from graph_types.DataframeHelper import format_timestamp, equilibrateListsWithNulls
from graph_types.BasicsUtils import BasicUtils
from graph_types.ReportUtils import ReportUtils
class Template_graphs():
   # Variables propias de la clase
  colors = {
    'red' : 'r',
    'blue' : 'b'
  }
  file_extention_tuple = ('.csv','.CSV')
  """
  PREPROCESOS DE CLASE
  """
  def __init__(self,filename,configMap, *args, **kwargs):
    # Inicialización de variables globales
    self.filename = filename
    self.properties = configMap
    self.bu = BasicUtils(self.properties)
    self.ru = ReportUtils(self.properties)
    
    # Inicialización de cabeceras
    self.timeStamp_label = self.properties["CSV_HEADERS"]["timeStamp"]
    self.elapsed_label = self.properties["CSV_HEADERS"]["elapsed"]
    self.label_label = self.properties["CSV_HEADERS"]["label"] 
    self.responseCode_label = self.properties["CSV_HEADERS"]["responseCode"]
    self.responseMessage_label = self.properties["CSV_HEADERS"]["responseMessage"]
    self.threadName_label = self.properties["CSV_HEADERS"]["threadName"]
    self.dataType_label = self.properties["CSV_HEADERS"]["dataType"]
    self.success_label = self.properties["CSV_HEADERS"]["success"]
    self.bytes_label = self.properties["CSV_HEADERS"]["bytes"]
    self.sentBytes_label = self.properties["CSV_HEADERS"]["sentBytes"]
    self.grpThreads_label = self.properties["CSV_HEADERS"]["grpThreads"]
    self.allThreads_label = self.properties["CSV_HEADERS"]["allThreads"]
    self.URL_label = self.properties["CSV_HEADERS"]["URL"]
    self.Latency_label = self.properties["CSV_HEADERS"]["Latency"]
    self.IdleTime_label = self.properties["CSV_HEADERS"]["IdleTime"]
    self.Connect_label = self.properties["CSV_HEADERS"]["Connect"]
    # Inicialización de cabeceras añadidas 
    self.date_label = self.properties["CSV_HEADERS"]["date"]
    self.count_label = self.properties["CSV_HEADERS"]["count"]
    self.RealLatency_label = self.properties["CSV_HEADERS"]["RealLatency"]
    
    # Objetos necesarios para el modo de comparativa
    self.compareDFList = []
    self.filenameList = []
  """
  *************
  PARTE PÚBLICA
  *************
  """
  def run_from_grafana(self,option,groupedArgs):
    """
    Lectura y ejecución de una gráfica proveniente de grafana del fichero CSV y el proceso seleccionado
    TODO o no exporta bien grafana la info o la grafica no es muy fina... datos inconclusos
    """
    print("ANALÍTICAS DE GRAFANA - "+option)
    self.source_num_chunk = None
    # Se genera el datagrama con el fichero y se elimina contenido nulo
    self.df = pd.read_csv(self.filename, error_bad_lines=False,
                                      warn_bad_lines=False, low_memory=False,sep=';')
    self.df = self.df.dropna()
    if option == self.properties["GRAFANA_COLLECTOR"]["memory"]:
      self.df[option] = self.df[self.properties["GRAFANA_COLLECTOR"]["value"]].map(lambda x: self.bu.grafanaMemoryMetricNormalizer(x))
    else:
      raise Exception('Error: La opcion {} no está contemplada para Grafana'.format(option))
    self.df = self.df.dropna(subset=[option])
    # Para el modo de grafana, la opcion es igual al parámetro opcional de la gráfica
    groupedArgs[self.properties["GRAPHIC_PLOTLY"]["optional_parameter"]] = groupedArgs["-o"]
    self.__run_selected_func(self.properties["SWITCH_OPTION"]["plotlyGraph"],**dict(groupedArgs))
    
  def run_full(self,func_to_exec,groupedArgs):
    """
    Lectura y ejecución COMPLETA del fichero CSV y el proceso seleccionado
    """
    print("EJECUCIÓN COMPLETA - "+func_to_exec)
    self.source_num_chunk = None
    # Se genera el datagrama con el fichero
    df = pd.read_csv(self.filename, error_bad_lines=False,
                                      warn_bad_lines=False, low_memory=False)
    df = self.__parse_dataframe(df) # Parsea datos actuales
    if '--offset' in groupedArgs:
      df = self.__applyOffsets(df) # Aplica offset en caso de indicarse sobre el timestamp
    self.df = self.__dataTreatment(df) # Añade informacion al datagrama
    if self.df.shape[0] > 1:
      self.__run_selected_func(func_to_exec,**dict(groupedArgs))
    else:
      print("El dataframe no contiene ningún valor tras aplicar la normalización - se descarta la ejecución")

  def run_by_parts(self,func_to_exec,groupedArgs):
    """
    Lectura y ejecución POR PARTES del fichero CSV y el proceso seleccionado
    """
    print("EJECUCIÓN POR PARTES - "+func_to_exec)
    customChunkSize = int(self.properties["CSV_READER"]["chunk_size"])
    result = pd.DataFrame()
    # Se generan 2 iteradores , uno para la barra de carga y otro para elctura de datos
    df,chunck_count = tee(pd.read_csv(self.filename,error_bad_lines=False,
                                      warn_bad_lines=False, chunksize=customChunkSize,
                                      low_memory=False))
                                      
    count_of_chunks = self.bu.getNumberOfChunks(chunck_count)
    del chunck_count
    # Llamada inicial pintando 0% de progreso
    print("******************\nSe inicia la lectura del fichero\n******************")
    self.__printProgressBar(0,count_of_chunks)
    for index,chunk in enumerate(df):
        chunk = self.__parse_dataframe(chunk) # Parsea datos actuales
        chunk = self.__dataTreatment(chunk) # Añade informacion al datagrama
        self.df = chunk
        self.source_num_chunk = str(index)
        
        self.__run_selected_func(func_to_exec,**dict(groupedArgs))
        result = result.append(chunk)
        # Actualiza la barra de carga
        self.__printProgressBar(index + 1,count_of_chunks)
    del df
  """
  *************
  Setters
  *************
  """
  def setFilename(self,filename):
    self.filename = filename
  """
  *********************
  FUNCIONES PRINCIPALES
  *********************
  """  
  def __generateReport(self,**kwargs):
    """
    Dado el nombre de una columna pasada por consola, obtiene todos 
    los valores únicos y el número de veces que aparecen
    """
    self.df[self.count_label] = self.df[self.timeStamp_label].map(lambda x: self.bu.adjustMilisecondsToAnotherUnit(x))
    self.df = self.df.dropna(subset=[self.count_label])
    print("numero de filas tras aplicar el ajuste de milisegundos de "+
          self.properties["NORMALIZER"]["adjust_miliseconds"]+
          ": "+str(self.df.shape[0]))
    # Inicio de la funcion
    label = self.properties["INFORME"]["filename"]
    filename = self.__formatFilename(label,self.filename,'.txt')
    self.ru.setDataframe(self.df)

    self.ru.hitRate(**kwargs)
    self.ru.obtain_unique_results_from_optional_param(**kwargs)
    self.ru.obtain_num_records_per_time_unit(**kwargs)

    self.ru.generateReport(filename)

  def __plotlyGraph(self,**kwargs):
      """
      Gráfica orientada a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """
      # Inicialización de parámetros
      choosenHeader = self.bu.obtainOptionalParameter(self.properties["GRAPHIC_PLOTLY"]["optional_parameter"],**kwargs)
      traceName = self.filename
      mode = self.properties['GRAPHIC_PLOTLY']['scatter_mode']
      mainTrace = self.__customTrace(self.df[self.date_label],
                                        self.df[choosenHeader],
                                        mode = mode,
                                        name=traceName,
                                        color=self.colors["red"])
                                
      self.compareDFList.append(mainTrace)

      if "generate-html" not in kwargs or ("generate-html" in kwargs and bool(kwargs['generate-html'])):
        layout = self.__customLayout(self.date_label,choosenHeader,self.properties['LAYOUT_GRAPHIC_PLOTLY']['title'])
        fig = go.Figure(data=self.compareDFList, layout=layout)
        filename = self.__formatFilename(self.properties['FILENAMES'][choosenHeader],self.filename)
        plot(fig, filename=filename)
        self.compareDFList = []

  def __boxplot_plotly(self,**kwargs):
      """
      Boxplot orientado a tiempos de respuesta
      devuelve un fichero html para una consulta interactiva de la información
      """
      choosenHeader_x = self.bu.obtainOptionalParameter(self.properties["BOXPLOT_PLOTLY"]["optional_parameter_x"],**kwargs)
      choosenHeader_y = self.bu.obtainOptionalParameter(self.properties["BOXPLOT_PLOTLY"]["optional_parameter_y"],**kwargs)
      if choosenHeader_x is None:
        raise Exception('Falta el argumento {} columnName'.format(self.properties["BOXPLOT_PLOTLY"]["optional_parameter_x"]))

      if choosenHeader_x not in self.df:
        raise Exception('Error: La columna {} no existe en el dataframe'.format(choosenHeader_x))

      if choosenHeader_y is None:
        raise Exception('Falta el argumento {} columnName'.format(self.properties["BOXPLOT_PLOTLY"]["optional_parameter_y"]))

      if choosenHeader_y not in self.df:
        raise Exception('Error: La columna {} no existe en el dataframe'.format(choosenHeader_y))
      
      cf.set_config_file(offline=True, world_readable=True, theme='ggplot')
      # Inicio de la lógica de la función
      #go.Layout(title="Boxplot",font=dict(family='Courier New, monospace', size=22, color='rgb(0,0,0)'))
      layout = self.__customLayout(choosenHeader_x,choosenHeader_y,self.properties['LAYOUT_BOXPLOT_PLOTLY']['title'])
      # Define el boxplot
      custom_boxpoints = (self.properties["BOXPLOT_PLOTLY"]["boxpoints"],False)[self.properties["BOXPLOT_PLOTLY"]["boxpoints"] == "False"]
      latencia = self.__customBoxplot(self.df[choosenHeader_x],self.df[choosenHeader_y],boxpoints=custom_boxpoints,showlegend=True,name=self.filename)
      # Define el nombre del fichero
      filename = self.__formatFilename(self.properties["BOXPLOT_PLOTLY"]["filename"]+"_"+choosenHeader_x+"_"+choosenHeader_y,self.filename)
      plot({
            "data": [latencia], 
            "layout": layout
            },
            filename=filename
          )

  def __boxplot_seaborn(self,**kwargs):
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
      myFig.savefig(self.properties["BOXPLOT_SEABORN"]["image_name"]+"."+self.properties["BOXPLOT_SEABORN"]["image_format"],
                    format=self.properties["BOXPLOT_SEABORN"]["image_format"])
  
  def __performanceSystemMetrics(self,**kwargs):
    """
    Con las métricas obtenidas del sistema al que ataca JMeter (usando un agente), devuelve una gráfica con
    cada medida parametrizada (CPU, Memoria, NetworkIO,...)
    """
    uniquePerfLabels = self.df.label.unique()
    self.__normalize_performance_metrics(uniquePerfLabels)
    # Create traces
    data = []
    for key in uniquePerfLabels:
      key = self.bu.adjustStringToLabel(key)
      data.append(go.Scatter(x=self.df[self.date_label], y=self.df[key],
                            mode='lines',
                            name=key))
      layout = go.Layout(
                        title=self.properties['LAYOUT_GRAPHIC_PLOTLY']['title'],
                        plot_bgcolor=self.properties['LAYOUT_GRAPHIC_PLOTLY']['plot_bgcolor'], 
                        showlegend=True
                        )
    # Define el nombre del fichero
    filename = self.__formatFilename(self.properties["PERFORM_COLLECTOR"]["filename"],self.filename)
    fig = go.Figure(data=data)
    plot(fig,
            filename=filename
          )
    
  def __numberHitsPerNMiliseconds(self,**kwargs):
    """
    Gráfica orientada a tiempos de respuesta
    devuelve un fichero html para una consulta interactiva de la información
    """
    # Inicialización de parámetros
    self.df[self.count_label] = self.df[self.timeStamp_label].map(lambda x: self.bu.adjustMilisecondsToAnotherUnit(x))
    self.df = self.df.dropna(subset=[self.count_label])
    print("numero de filas tras aplicar el ajuste de milisegundos de "+
          self.properties["NORMALIZER"]["adjust_miliseconds"]+
          ": "+str(self.df.shape[0]))
    print("Se guarda el dataframe tratado para el fichero "+ self.filename)
    self.compareDFList.append(self.df)
    self.filenameList.append(self.filename)
    if "generate-html" not in kwargs or ("generate-html" in kwargs and bool(kwargs['generate-html'])):
      fig = self.__generateCountPlotFromMultipleDF(self.timeStamp_label,
                                                  self.count_label,
                                                  self.properties['LAYOUT_COUNT_PLOTLY']['title'],
                                                   **kwargs) 
      filename = self.__formatFilename(self.properties['COUNT_PLOTLY']['filename'],self.filename)
      plot(fig, filename=filename)
      self.compareDFList = []
      self.filenameList = []

  """
  ******************
  FUNCIONES DE APOYO
  ******************
  """
  def __formatFilename(self,label,filename,suffix='.html'):
    """
    Dada una etiqueta, el timelapse de la muestra y a opcion se monta el
    nombre del fichero a generar
    """
    firstDate = ""
    lastDate = ""

    if(self.timeStamp_label in self.df):
      firstDate = format_timestamp(self.df[self.timeStamp_label].iloc[0])
      lastDate = format_timestamp(self.df[self.timeStamp_label].iloc[-1])
    prefix = label+"___"+firstDate+"___"+lastDate+"___"
    filename = os.path.splitext(filename)[0]
    return filename+prefix+suffix

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
    if "boxpoints" in kwargs:
      custom_boxpoints = kwargs["boxpoints"]
    # Creación del boxplot
    boxplot = go.Box(x=Xaxis,y=Yaxis,
                    showlegend=(True,custom_showlegend)["showlegend" in kwargs],
                    name=('Boxplot',custom_name)["name" in kwargs],
                    boxpoints=(False,custom_boxpoints)["boxpoints" in kwargs],
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

  def __customLayout(self, xaxis_label, yaxis_label, ctm_title, **kwargs):
    """
    Calculo de traza en el esquema estadistico en funcion de los siguientes parametros de entrada
    Xaxis : label para el eje x
    Yaxis : label para el eje y
    """
    ctm_margin={'l': 0, 'r': 0, 't': 100, 'b': 0}
    ctm_xaxis={'automargin': True, 'title': self.properties['AXIS_LABELS'][xaxis_label]}
    ctm_yaxis={'automargin': True, 'title': self.properties['AXIS_LABELS'][yaxis_label]}
    layout = go.Layout(
            plot_bgcolor=self.properties['LAYOUT_GRAPHIC_PLOTLY']['plot_bgcolor'], 
            showlegend=True,
            font=dict(family='Courier New, monospace', size=20, color='rgb(0,0,0)'),
            margin=ctm_margin,
            xaxis=ctm_xaxis,
            yaxis=ctm_yaxis,
            title = ctm_title
            )
    return layout

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
    chunk[self.date_label] = chunk[self.timeStamp_label].map(lambda x: self.bu.obtainDateWithEpochMillis(x))
    chunk = chunk.dropna(subset=[self.date_label])
    print("numero de filas tras generar la columna de fecha a partir de timestamp: "+str(chunk.shape[0]))
    chunk[self.date_label] = chunk[self.date_label].map(lambda x:self.bu.humanizeDateWithFormat(x))
    chunk = chunk.dropna(subset=[self.date_label])
    print("numero de filas tras aplicar formato a la fecha: " + str(chunk.shape[0]))
    chunk[self.RealLatency_label] = chunk.apply(lambda x: self.bu.realLatencyNormalizer(x.Latency, x.Connect), axis=1)
    chunk = chunk.dropna(subset=[self.RealLatency_label])
    print("numero de filas tras insertar una columna de latencia real: "+str(chunk.shape[0]))
    return chunk
      
  def __parse_dataframe(self,chunk):
    """
    Una vez cargado el dataframe se realizan comprobaciones para su usabilidad
    """
    print("numero de filas iniciales: "+str(chunk.shape[0]))
    # Aplica granularidad al dataframe si está activado
    if (self.bu.str_to_boolean(self.properties["NORMALIZER"]["granularity_active"])):
      print("¡Granularidad activada!")
      chunk[self.timeStamp_label] = chunk[self.timeStamp_label].map(lambda x: self.bu.granularityNormalizer(x))
      subsetLabels =[self.timeStamp_label]
      # En caso de conener la etiqueta label, es necesario filtrar con ella para no perder informacion
      if self.label_label in chunk:
        subsetLabels.append(self.label_label)
      chunk = chunk.drop_duplicates(subset=subsetLabels, keep=self.properties["NORMALIZER"]["granularity_keep"])
      print("numero de filas tras aplicar la granularidad: "+str(chunk.shape[0]))
    # Agrupa los diferentes errores ajenos a la peticion rest como error de conexion
    chunk[self.responseCode_label] = chunk[self.responseCode_label].map(lambda x: self.bu.responseCodeNormalizer(x))
    chunk = chunk.dropna(subset=[self.responseCode_label])
    print("numero de filas tras aplicar normalización en código de respuesta: "+str(chunk.shape[0]))
    # Descarta timestamps que hayan podido ser recortados o carezcan de sentido

    chunk[self.timeStamp_label] = chunk[self.timeStamp_label].map(lambda x: self.bu.timeStampNormalizer(x))
    chunk = chunk.dropna(subset=[self.timeStamp_label])
    print("numero de filas tras aplicar normalización en timestamp: "+str(chunk.shape[0]))
    # Agrupa los hilos levantados en función de un intervalo definido por configuración
    chunk[self.allThreads_label] = chunk[self.allThreads_label].map(lambda x: self.bu.allThreadsNormalizer(x))
    chunk = chunk.dropna(subset=[self.allThreads_label])
    print("numero de filas tras aplicar normalización en hilos ejecutados: "+str(chunk.shape[0]))
    return chunk
  
  def __applyOffsets(self,chunk):
    # En función del timeStamp más reducido, aplicar un offset para abstraer el valor
    minFromTimestamp = chunk[self.timeStamp_label].min()
    # Para evitar perder información, se resta del mínimo el ajuste de unidades
    minFromTimestamp = minFromTimestamp - int(self.properties["NORMALIZER"]["adjust_miliseconds"]) -  int(self.properties["NORMALIZER"]["adjust_stops"])
    print("Valor del offset referencia con el ajuste aplicado: "+str(minFromTimestamp))
    chunk[self.timeStamp_label] = chunk[self.timeStamp_label].map(lambda x: self.bu.offsetTimestampNormalizer(x,minFromTimestamp))
    chunk = chunk.dropna(subset=[self.timeStamp_label])
    print("numero de filas tras aplicar el offset al timestamp: "+str(chunk.shape[0]))
    return chunk

  def __generateCountPlotFromMultipleDF(self, ctm_xaxis, ctm_yaxis, ctm_title, **kwargs):
    # Inicialización de parámetros
    mode = self.properties['GRAPHIC_PLOTLY']['scatter_mode']  
    traceList = []
    labelsList = []
    valuesList = []
    for srcDf in self.compareDFList:
      print("Obteniendo info del dataframe con '"+str(len(srcDf))+"' registros")
      labels = srcDf["count"].unique()
      values = srcDf["count"].value_counts().values
      print("Size de labels: "+str(len(labels)))
      print("Size de values: "+str(len(values)))
      labelsList.append(labels)
      valuesList.append(values)
      print("Información obtenida")
    
    
    labelsList, valuesList = equilibrateListsWithNulls(labelsList,valuesList)

    for srcFilename, srcLabel, srcValues in zip(self.filenameList, labelsList, valuesList):
      print("Generando traza de gráfica con '"+str(len(srcValues))+"' valores")
      traceName = srcFilename
      trace = self.__customTrace(srcLabel,
                                srcValues,
                                mode=mode,
                                name=traceName,
                                color=self.colors["red"])
      traceList.append(trace)
      print("Traza generada")
                       
    layout = self.__customLayout(ctm_xaxis, ctm_yaxis, ctm_title)

    print("Construyendo Figura con todas las trazas( puede tardar con registros voluminosos)")   
    fig = go.Figure(data=traceList, layout=layout)
    print("figura contruida")
    return fig

  def __normalize_performance_metrics(self,uniqueValues):
    """
    Para la opcion 'system_metrics' se normaliza la información pertinente para poder ser tratada
    """
    # Descarta etiquetas que contengan numeros
    self.df[self.label_label] = self.df[self.label_label].map(lambda x: self.bu.performanceLabelMetricNormalizer(x))
    self.df = self.df.dropna(subset=[self.label_label])
    # Añade nuevas métricas al dataframe
    for performMetric in uniqueValues:
      adjust_label = self.bu.adjustStringToLabel(performMetric)
      self.df[adjust_label] = self.df.apply(lambda x: self.bu.performanceElapsedMetricNormalizer(x.label, x.elapsed, performMetric), axis=1)


  def __run_selected_func(self,func,**kwargs):
    print("seleccionando funcion: "+func)
    switcher = {
          self.properties["SWITCH_OPTION"]["plotlyGraph"]: partial(self.__plotlyGraph,**kwargs),
          self.properties["SWITCH_OPTION"]["boxplot_seaborn"]: partial(self.__boxplot_seaborn,**kwargs),
          self.properties["SWITCH_OPTION"]["boxplot_plotly"]: partial(self.__boxplot_plotly,**kwargs),
          self.properties["SWITCH_OPTION"]["generateReport"]: partial(self.__generateReport,**kwargs),
          self.properties["SWITCH_OPTION"]["performanceSystemMetrics"]: partial(self.__performanceSystemMetrics,**kwargs),
          self.properties["SWITCH_OPTION"]["numberHitsPerNMiliseconds"]: partial(self.__numberHitsPerNMiliseconds,**kwargs)
    }
    function = switcher.get(func, lambda: print("La opción '"+func+"' no está contemplada"))
    return function()

    

    