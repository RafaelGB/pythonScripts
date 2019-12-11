import re

import numpy as np
import pandas as pd

#VARIABLES GLOBALES
ENTER_KEY = '\n'

class section(dict):
    def __init__(self):
        self = dict()
        
    def addTitle(self, title):
        self['title'] = title
    
    def addContent(self, content):
        self['content'] = content

class ReportUtils():
  """
  PREPROCESOS DE CLASE
  """
  def __init__(self, configMap):
    # Inicialización de variables globales de clase
    self.properties = configMap
    self.sections = []

  """
  FUNCIONES PUBLICAS
  """
  def obtain_unique_results_from_optional_param(self,**kwargs):
    """
    Seccion que añade sobre la columna elegida los valores únicos y un contador
    """
    num_records_section = section()
    # coge el valor asignado por parámetro de entrada
    choosenHeader = self.__obtainCustomParameter(self.properties["INFORME"]["unique_value_param"],**kwargs)
    title = self.properties["INFORME"]["unique_value_title"] + " para la columna " + choosenHeader
    num_records_section.addTitle(title)
    if choosenHeader not in self.df:
      print("Error: La columna no existe en el dataframe")
      raise Exception('Error: La columna {} no existe en el dataframe'.format(choosenHeader))

    valueCounts = self.df[choosenHeader].value_counts()
    content = ''
    for i, v in valueCounts.iteritems():
        content = content + 'Parámetro único "{}" con {} repeticiones'.format(i,v) + ENTER_KEY
    
    num_records_section.addContent(str(content))
    self.__addNewSection(num_records_section)

  def obtain_num_records_per_time_unit(self,**kwargs):
    """
    Seccion para mostrar por rangos de tiempo el número de muestras registradas
    """
    unique_values_section = section()
    unique_values_section.addTitle(self.properties["INFORME"]["num_records_title"])
    # coge el valor asignado por parámetro de entrada
    timeUnit = self.__obtainCustomParameter(self.properties["INFORME"]["num_records_param"],**kwargs)
    
    groupCount = self.df.groupby([self.properties["CSV_HEADERS"]["count"]]).size()
    content = ''
    lastInitRangeRef = 0
    adjustment = int(self.properties["NORMALIZER"]["adjust_miliseconds"]) / 60000
    stopAdjustment = int(self.properties["NORMALIZER"]["adjust_stops"]) / 60000

    # Agregaciones para incluir medias según sectores
    RealLatencyAggMean = self.df.groupby(self.properties["CSV_HEADERS"]["count"]).agg({self.properties["CSV_HEADERS"]["RealLatency"]:'mean'})
    allThreadsAggMean = self.df.groupby(self.properties["CSV_HEADERS"]["count"]).agg({self.properties["CSV_HEADERS"]["allThreads"]:'mean'})
    
    for index , (i, v) in enumerate(groupCount.iteritems(),0):
        i = int(i)*adjustment + ( stopAdjustment * index )

        latencyMean = RealLatencyAggMean.iloc[index].item()
        allThreadsMean = allThreadsAggMean.iloc[index].item()
        content = content + 'Del minuto {} al {} se han ejecutado {} transacciones con una media de respuesta de {} milisegundos y {} hilos concurrentes'.format(lastInitRangeRef,i,v,latencyMean,allThreadsMean) + ENTER_KEY
        lastInitRangeRef = i + ( int(self.properties["NORMALIZER"]["adjust_stops"]) / 60000 )
    unique_values_section.addContent(str(content))
    self.__addNewSection(unique_values_section)

  def hitRate(self, **kwargs):
    """
    Seccion que añade sobre la columna elegida los valores únicos y un contador
    """
    hit_rate_section = section()
    hit_rate_section.addTitle(self.properties["INFORME"]["hit_rate_title"])
    # coge directamente de configuración la cabecera del código de respuesta
    responseCodeLabel = self.properties["CSV_HEADERS"]["responseCode"]

    if responseCodeLabel not in self.df:
      print("Error: La columna no existe en el dataframe")
      raise Exception('Error: La columna {} no existe en el dataframe'.format(responseCodeLabel))

    valueCounts = self.df[responseCodeLabel].value_counts()
    contentOK = ''
    contentKO = ''
    totalHits = self.df.shape[0]

    for i, v in valueCounts.iteritems():
      if i == self.properties["RESPONSE_CODE_VALUES"]["200"]:
        OkRate = (int(v)*100) / totalHits
        contentOK = contentOK + 'Tasa de aciertos para "{}" con un porcentaje del {} %'.format(i,str(OkRate)) + ENTER_KEY
      else:
        KORate = (int(v)*100) / totalHits
        contentKO = contentKO + 'Tasa de fallos para "{}" con un porcentaje del {} %'.format(i,str(KORate)) + ENTER_KEY
    
    hit_rate_section.addContent(str(contentOK)+str(contentKO))
    self.__addNewSection(hit_rate_section)

  def generateReport(self,filename,**kwargs):
    try:
        file = open(filename,"w+")
        file.write(self.__generateTextFromSections())
    except IOError as IO:
        raise Exception("Error de entrada salida:\n{}".format(IO))
    finally:
        file.close()
        self.sections = []
  

  """
  SETTERS
  """
  def setDataframe(self, dataframe):
      self.df = dataframe

  """
  FUNCIONES PRIVADAS
  """
  def __obtainCustomParameter(self, label, **kwargs):
    """
    En funcion de una etiqueta y el mapa de argumentos recibido en la entrada,
    devuelve el parámetro asociado a dicha columna si existe
    """
    param = kwargs[label].not_files[0]
    if param is None:
      raise Exception('Falta el argumento {} columnName'.format(label))

    return str(kwargs[label].not_files[0])

  def __addNewSection(self, section):
    """
    Añade a la lista de secciones ya guardadas una nueva, usando el parámetro de text
    como contenido
    """
    self.sections.append(section)

  def __generateTextFromSections(self):
    """
    Añade a la lista de secciones ya guardadas una nueva, usando el parámetro de text
    como contenido
    """
    final_text = ''
    for section in self.sections:
        final_text = final_text + ('*' * len(section['title'])) + ENTER_KEY
        final_text = final_text + section['title'] + ENTER_KEY
        final_text = final_text + ('*' * len(section['title'])) + ENTER_KEY
        final_text = final_text + section['content'] + ENTER_KEY
    return final_text

