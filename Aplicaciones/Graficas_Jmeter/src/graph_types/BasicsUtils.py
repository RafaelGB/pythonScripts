import re

import numpy as np
import pandas as pd

#VARIABLES GLOBALES
MB_SCALE = (1024*1024)

class BasicUtils():
  """
  PREPROCESOS DE CLASE
  """
  def __init__(self, configMap):
    # Inicialización de variables globales de clase
    self.properties = configMap
    self.performanceDict = {}
    for key in self.properties["PERFORM_COLLECTOR"]:
        self.performanceDict[self.adjustStringToLabel(self.properties["PERFORM_COLLECTOR"][key])] = 0
  """
  FUNCIONES PUBLICAS
  """
  def str_to_boolean(self,string):
      if string == 'True':
          return True
      elif string == 'False':
          return False
      raise Exception('Error: La transformacion de {} a booleano no está soportada'.format(string))

  def obtainOptionalParameter(self, label,**kwargs):
    """
    En funcion de una etiqueta y el mapa de argumentos recibido en la entrada,
    devuelve el parámetro asociado a dicha columna si existe
    """
    return str(kwargs[label].not_files[0])

  def getNumberOfChunks(self, reader):
    """
    Dado un fileReader te devuelve el numero de apartados que tiene
    """
    number_of_chunks=0
    for chunk in reader:
        number_of_chunks=number_of_chunks+1
    return number_of_chunks

  def adjustStringToLabel(self, mainString):
    # Caracteres a remplazar
    toBeReplaces = [" ","/"]
    newString = "_"
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in str(mainString):
            # Reemplaza el elemento por el marcaje apropiado
            mainString = mainString.replace(elem, newString)
    return  mainString

  # Funciones para normalizar los datos de JMETER
  # ---------------------------------------------
  def granularityNormalizer(self, timeStamp):
      """
      Modifica la base de tiempos timeStamp para forzar una granularidad de muestreo
      """
      granularity = int(self.properties["NORMALIZER"]["granularity"])
      timeStamp = timeStamp // granularity
      timeStamp = timeStamp * granularity
      return timeStamp
    
  def realLatencyNormalizer(self, latency, connect):
      """
      Resta a la latencia total el tiempo de conexión para obtener el resultado
      real de procesado por el servicio Rest
      """
      try:
        realLatency = int(latency) - int(connect)
        if realLatency < 0:
            raise Exception("Valor de latencia incongruente")
        return realLatency
      except:
        return np.nan

  def responseCodeNormalizer(self, responseCode):
    """
    Normaliza los datos de tiempo de respuesta
    para poder trabajar con ellos
    """
    # Rellena valores nulos
    if str(responseCode) == "nan":
        return np.nan
    # Filtra primero valores residuales no esperados
    if not str(responseCode).isdigit():
        try:
            responseCode = int(responseCode)
        except:
            return np.nan
    # Asigna a cada valor entero una condición
    code = str(responseCode)
    if code in self.properties["RESPONSE_CODE_VALUES"]:
        return self.properties["RESPONSE_CODE_VALUES"][code]
    else:
        # En caso de que la opcion no esté contemplada se descarta
        return np.nan

  def timeStampNormalizer(self, timeStamp):
    """
    Normaliza los datos de timeStamp
    para poder trabajar con ellos
    """
    # Asegura que el tiempo esté en milisegundos y sea un número
    if len(str(timeStamp)) != 13 or not str(timeStamp).isdigit():
        return np.nan
    else:
        return int(timeStamp)

  def allThreadsNormalizer(self, allThreads):
    """
    Normaliza los datos de los hilos activos levantados
    para poder trabajar con ellos
    """
    str_interval = self.properties["NORMALIZER"]["allThreadsInterval"]
    # Descartar posibles valores no procesables
    if (not str(allThreads).isdigit()):
        try:
            allThreads = int(allThreads)
        except:
             return np.nan
    # Para evitar ilegibilidad, agrupa los hilos en intervalos
    allThreads = int(allThreads)
    interval = int(str_interval)
    allThreads = allThreads//interval
    allThreads = allThreads*interval
    return allThreads

  def performanceLabelMetricNormalizer(self, performanceMetric):
    """
    Normaliza la columna label interpretada con las etiquetas de rendimiento
    del sistema, obtenidas con el agente 'PerfMon Metrics Collector'
    """
    # Descartar posibles valores que no sean enteramente string
    if (any(char.isdigit() for char in performanceMetric)):
        return np.nan
    # Para evitar ilegibilidad, agrupa los hilos en intervalos
    return performanceMetric

  def performanceElapsedMetricNormalizer(self, label, elapsed, srcMetric):
    """
    Normaliza la columna elapsed interpretada con los parámetros de rendimiento
    del sistema, obtenidas con el agente 'PerfMon Metrics Collector'
    """
    performCollectorMetrics = self.properties["PERFORM_COLLECTOR"]
    # Indica el uso de una variable global de función
    key = self.adjustStringToLabel(srcMetric)
    if label == srcMetric:
        # Si coincide la metrica a tratar con la etiqueta normalizamos el dato
        if performCollectorMetrics["CPU"] == label:
            # CPU pasa a ser de 0% a 100%
            elapsed = elapsed // 1000
        elif performCollectorMetrics["Memory"] == label:
            # Memoria escalada 1:1000
            elapsed = elapsed // 1000
        # registra el nuevo valor
        self.performanceDict[key] = elapsed
    else:
        # Utiliza el valor almacenado si no coincide en el tiempo
        elapsed = self.performanceDict[key]
    return elapsed

  # Funciones para normalizar los datos de GRAFANA
  # ----------------------------------------------
  def grafanaMemoryMetricNormalizer(self, grafanaMemoryMetric):
    """
    Normaliza la columna label interpretada con las etiquetas de rendimiento
    del sistema, obtenidas con el agente 'PerfMon Metrics Collector'
    """
    # Descartar posibles valores que no sean dígitos
    if not re.match("^[0-9]{3}\.[0-9]{3}\.[0-9]{3}$",grafanaMemoryMetric):
        return np.nan
    # Ajustar a MB
    global MB_SCALE
    grafanaMemoryMetric = int(grafanaMemoryMetric.replace(".","")) // MB_SCALE
    return grafanaMemoryMetric

  # Funciones para aplicar un offset sobre tiempos
  # ----------------------------------------------
  def offsetTimestampNormalizer(self, timeStamp,offset):
    """
    Aplica una reducción común a la línea temporal para superponer gráficas
    """
    return timeStamp - offset

  # Funciones para añadir información a un dataframe
  # ------------------------------------------------
  def obtainDateWithEpochMillis(self,timestamp):
    """
    Genera una fecha a partir de milisegundos en formato epoch millis
    """
    try:  
        result = pd.to_datetime(timestamp, unit='ms')
        return result
    except:
        return np.nan

  def adjustMilisecondsToAnotherUnit(self, timeStamp):
    """
    Aplica un ajuste de los milisegundos a otra unidad de tiempo mayor
    en función de la configuración asignada
    """
    try:
        adjustment = int(self.properties["NORMALIZER"]["adjust_miliseconds"])
        stop = int(self.properties["NORMALIZER"]["adjust_stops"])

        if stop >= adjustment:
            raise Exception("El tiempo de parada no puede ser mayor al de bloque")

        adjustment  = adjustment + stop
        if (timeStamp > adjustment) and (timeStamp % adjustment < stop):
            return np.nan
        else:
            return timeStamp // adjustment

    except:
        return np.nan

  # Funciones para "humanizar" la información recibida
  # --------------------------------------------------
  def humanizeDateWithFormat(self,date):
    """
    Genera una fecha a partir de milisegundos en formato epoch millis
    """
    try:  
        result = pd.to_datetime(date, format='%d/%b/%Y:%H:%M:%S', utc=True)
        return result
    except:
        return np.nan