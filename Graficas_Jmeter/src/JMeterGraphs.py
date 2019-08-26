#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import os

sys.path.insert(0, os.path.abspath('..'))

from clint.arguments import Args
from clint.textui import puts, colored, indent

import configparser

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
  args = Args()
  groupedArgs = dict(args.grouped)
  # Check de los parámetros de entrada
  if not (checkArgs(groupedArgs)):
    print("Error critico en los argumentos - fin del programa")
    return
  # Inicialización en funcion de los parámetros de entrada
  options = groupedArgs["-o"].all
  filename = groupedArgs["-f"].all[0]
  # Inicialización de configuracion
  configMap = read_conf("conf.cfg")
  # Seleccionamos la función a lanzar
  for option in options:
    select_option(option,filename,configMap,**dict(groupedArgs))

def select_option(option,filename,configMap,**kwargs):
  graphsClass = Template_graphs(filename,configMap)
  switcher = {
        "latencia": partial(graphsClass.latencyGraph,**kwargs),
        "boxplot_seaborn": partial(graphsClass.boxplot_seaborn,**kwargs),
        "boxplot_plotly": partial(graphsClass.boxplot_plotly,**kwargs),
        "valores_unicos": partial(graphsClass.obtainUniqueValuesFromColumn,**kwargs),
  }
  func = switcher.get(option, lambda: "Función no definida")
  return func()
"""
*************
SUBFUNCIONES
*************
"""
def checkArgs(groupedArgs):
  isCorrect = True
  # Comprueba argumentos sobre el fichero que contiene los datos
  if '-f' not in groupedArgs:
    print("Falta argumento -f necesario para indicar fichero")
    isCorrect = False
  elif not bool(groupedArgs['-f'].files) or len(groupedArgs['-f'].files) > 1:
    print("Debe indicarse una ruta a fichero CSV para el argumento -f")
    isCorrect = False

  # Comprueba la opción de grafica elegida
  if '-o' not in groupedArgs:
    print("Falta argumento -o necesario para indicar la/s opción/es de gráfica")
    isCorrect = False
  elif not bool(groupedArgs['-o'].not_files):
    print("No se ha elegido ninguna opcion de grafica para el argumento -o")
    isCorrect = False

  return isCorrect

if __name__ == '__main__':
  start()