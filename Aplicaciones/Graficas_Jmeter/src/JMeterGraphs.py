#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import traceback
import os

sys.path.insert(0, os.path.abspath('..'))

from clint.arguments import Args

import configparser

from functools import partial
from datetime import datetime
from graph_types.Basics import Template_graphs

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
  # Si se ha solicitado la opción de ayuda, muestra el panel
  if "-h" in groupedArgs or "--help" in groupedArgs:
    showHelp()
    # Tras mostrar la ayuda se sale del programa
    return
  # Inicialización en funcion de los parámetros de entrada obligatorios
  options = groupedArgs["-o"].all

  # Inicialización en funcion de los parámetros de entrada obligatorios
  path = groupedArgs["-f"].all[0]
  files = []
  if os.path.isdir(path): # En caso de ser un directorio la ruta de entrada 
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for aFile in f:
            if '.csv' in aFile or '.CSV' in aFile:
              files.append(os.path.join(r, aFile))
  elif os.path.isfile(path): # En caso de ser un fichero la ruta de entrada
     files.append(os.path.join('.', path))
  # Inicialización en funcion de los parámetros de entrada opcionales ( o por defecto )
  mode = optionalArgs["-m"]
  # Inicialización de configuracion
  configMap = read_conf("conf.cfg")
  print("Se pasan a procesar los siguientes ficheros:"+ str(files))
  singletonClass = None
  if '--compare-mode' in groupedArgs:
    singletonClass = Template_graphs(None,configMap)
  for index,filename in enumerate(files):
    if '--compare-mode' in groupedArgs:
      groupedArgs['generate-html'] = (index >= len(files) - 1)
      
    # Seleccionamos la función a lanzar
    for option in options:
      select_mode(option,mode,filename,configMap,groupedArgs,singletonClass)

def select_mode(option,mode,filename,configMap,groupedArgs,singletonClass):
  try:
    print("MODO "+mode)
    if singletonClass != None:
      singletonClass.setFilename(filename)
    else:
      singletonClass = Template_graphs(filename,configMap)
      
    switcher = {
          configMap["SWITCH_MODE"]["full"]: partial(singletonClass.run_full,option,groupedArgs),
          configMap["SWITCH_MODE"]["chunks"]: partial(singletonClass.run_by_parts,option,groupedArgs),
          configMap["SWITCH_MODE"]["grafana"]: partial(singletonClass.run_from_grafana,option,groupedArgs)          
    }
    func = switcher.get(mode, lambda: "Modo de ejecución no contemplada")
    return func()
  except Exception as error:
    print("[ERROR] => con Modo: {}, Opcion: {} ha saltado una excepción".format(option,mode))
    print(error)
    print("**************")
    print("[TRACEBACK] =>")
    traceback.print_exc(file=sys.stdout)
    
    return None
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
  elif not bool(groupedArgs['-f'].all) or len(groupedArgs['-f'].all) > 1:
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
  optionalArgs["-m"] = (groupedArgs["-m"].all[0],"full")['-m' not in groupedArgs]
  
  return optionalArgs

def showHelp():
  f = open('../readme.md', 'r')
  file_contents = f.read()
  print (file_contents)
  f.close()

if __name__ == '__main__':
  start()