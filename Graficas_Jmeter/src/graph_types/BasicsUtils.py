import re

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
      granularity = int(self.properties["NORMALIZER"]["granularity"])
      timeStamp = timeStamp // granularity
      timeStamp = timeStamp * granularity
      return timeStamp

  def responseCodeNormalizer(self, responseCode):
    """
    Normaliza los datos de tiempo de respuesta
    para poder trabajar con ellos
    """
    # Rellena valores nulos
    if str(responseCode) == "nan":
        return "Sin respuesta"
    # Filtra primero valores residuales no esperados
    if not str(responseCode).isdigit():
        return None
    # Asigna a cada valor entero una condición
    code = int(responseCode)
    if code == 200:
        return "200: OK"
    if code == 401:
        return "401 No autorizado"
    if code == 404:
        return "404 Servicio no encontrado"
    if code == 500:
        return "500: Error interno del servidor"
    if code == 503:
        return "503: Servicio no disponible"
    if code == 504:
        return "504: Gateway timeout"
    # En caso de que la opcion no esté contemplada se descarta
    return None

  def timeStampNormalizer(self, timeStamp):
    """
    Normaliza los datos de timeStamp
    para poder trabajar con ellos
    """
    # Asegura que el tiempo esté en milisegundos y sea un número
    if len(str(timeStamp)) != 13 or not str(timeStamp).isdigit():
        return None
    else:
        return timeStamp

  def allThreadsNormalizer(self, allThreads):
    """
    Normaliza los datos de los hilos activos levantados
    para poder trabajar con ellos
    """
    str_interval = self.properties["NORMALIZER"]["allThreadsInterval"]
    # Descartar posibles valores no procesables
    if (not str(allThreads).isdigit()):
        return None
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
        return None
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
            return None
        # Ajustar a MB
        global MB_SCALE
        grafanaMemoryMetric = int(grafanaMemoryMetric.replace(".","")) // MB_SCALE
        return grafanaMemoryMetric