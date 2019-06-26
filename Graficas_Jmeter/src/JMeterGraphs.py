import configparser
import sys

from functools import partial
from datetime import datetime
from graph_types.Basics import Template_graphs

file_extention_tuple = ('.csv','.CSV')
def read_conf(configFilename):
  """
  Dado un nombre de fichero (tipo incluido), carga la configuración y se devuelve mapeada
  """
  config = configparser.ConfigParser()
  config.read(configFilename)
  return config

def start():
  """
  Función de arranque
  """
  # Tratamiento de parámetros de entrada
  if len(sys.argv) != 3:
    print("Método de uso: JMeterGraphs.py tipoGrafica fichero.csv")
    return
  elif not sys.argv[2].endswith(file_extention_tuple):
    print("El programa solo soporta tipos de fichero CSV")
    return
  option = sys.argv[1]
  filename = sys.argv[2]
  # Inicializacion de configuracion
  configMap = read_conf("conf.cfg")
  # Seleccionamos la función a lanzar
  select_option(option,filename,configMap)

def select_option(option,filename,configMap,**kwargs):
  graphsClass = Template_graphs(filename,configMap)
  switcher = {
        "latencia": partial(graphsClass.latencyGraph,**kwargs),
        "boxplot_seaborn": partial(graphsClass.boxplot_seaborn,**kwargs),
        "boxplot_plotly": partial(graphsClass.boxplot_plotly,**kwargs)
  }
  func = switcher.get(option, lambda: "Función no definida")
  return func()

if __name__ == '__main__':
  start()