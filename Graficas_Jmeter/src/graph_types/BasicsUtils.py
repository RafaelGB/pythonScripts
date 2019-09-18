def obtainOptionalParameter(label,**kwargs):
    """
    En funcion de una etiqueta y el mapa de argumentos recibido en la entrada,
    devuelve el parámetro asociado a dicha columna si existe
    """
    return str(kwargs[label].not_files[0])

def getNumberOfChunks(reader):
    """
    Dado un fileReader te devuelve el numero de apartados que tiene
    """
    number_of_chunks=0
    for chunk in reader:
      number_of_chunks=number_of_chunks+1
    return number_of_chunks

def responseCodeNormalizer(responseCode):
    """
    Normaliza los datos de tiempo de respuesta
    para poder trabajar con ellos
    """
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

def timeStampNormalizer(timeStamp):
    """
    Normaliza los datos de timeStamp
    para poder trabajar con ellos
    """
    # Asegura que el tiempo esté en milisegundos y sea un número
    if len(str(timeStamp)) != 13 or not str(timeStamp).isdigit():
        return None
    else:
        return timeStamp

def allThreadsNormalizer(allThreads,str_interval):
    """
    Normaliza los datos de los hilso activos levantados
    para poder trabajar con ellos
    """
    # Descartar posibles valores no procesables
    if (not str(allThreads).isdigit()):
        return None
    # Para evitar ilegibilidad, agrupa los hilos en intervalos
    allThreads = int(allThreads)
    interval = int(str_interval)
    allThreads = allThreads//interval
    allThreads = allThreads*20
    return allThreads