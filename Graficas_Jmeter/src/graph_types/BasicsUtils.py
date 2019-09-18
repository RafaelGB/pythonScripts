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
    # Filtra primero valores residuales no esperados
    if not str(responseCode).isdigit():
        return None
    # Asigna a cada valor entero una condición
    code = int(responseCode)
    if code == 200:
        return "200: OK"
    elif code == 503:
        return "503: Problema servidor"
    elif code == 504:
        return "504: Timeout"
    else:
        return None