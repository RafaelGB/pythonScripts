import configparser

def read_conf(configFilename):
    """
    Dado un nombre de fichero (tipo incluido), carga la configuración y se devuelve mapeada
    """
    config = configparser.ConfigParser()
    config.read(configFilename)
    return config