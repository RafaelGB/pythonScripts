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
  # En caso de no tener parámetros opcionales cargar los de por defecto
  optionalArgs = defaultOptionalArgs(groupedArgs)
  # Inicialización en funcion de los parámetros de entrada obligatorios
  options = groupedArgs["-o"].all
  filename = groupedArgs["-f"].all[0]
  # Inicialización en funcion de los parámetros de entrada opcionales ( o por defecto )
  mode = optionalArgs["-m"]
  # Inicialización de configuracion
  configMap = read_conf("conf.cfg")
  # Seleccionamos la función a lanzar
  print(options)
  for option in options:
    select_option(option,mode,filename,configMap,groupedArgs)

def select_option(option,mode,filename,configMap,groupedArgs):
  print("MODO "+mode)
  graphsClass = Template_graphs(filename,configMap)
  switcher = {
        "full": partial(graphsClass.run_full,option,groupedArgs),
        "chunks": partial(graphsClass.run_by_parts,option,groupedArgs)
        
  }
  func = switcher.get(mode, lambda: "Modo de ejecución no contemplada")
  return func()
"""
*************
 UTILIDADES
*************
"""
def checkArgs(groupedArgs):
  """
  Comprobación de los parámetros de entrada obligatorios
  """
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
    print("No se ha elegido ninguna opcion para el argumento -o")
    isCorrect = False
  return isCorrect

def defaultOptionalArgs(groupedArgs):
  """
  Comprobación de los parámetros de entrada opcionales e inicialización
  a valores por defecto si aplica
  """
  optionalArgs = {}
  optionalArgs["-m"] = "full" if '-m' not in groupedArgs else groupedArgs["-m"].all[0]
  
  return optionalArgs


if __name__ == '__main__':
  start()