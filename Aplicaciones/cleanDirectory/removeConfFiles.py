import os
import sys
from shutil import rmtree
###################################################
#               VARIABLES GLOBALES
###################################################
ignoreList = []
###################################################
#                 IMPLEMENTACIÓN
###################################################
# Dado una ruta de fichero, devuelve una lista con su contenido por líneas
def read_file_by_line(filePath):
    content = []
    with open(filePath) as f:
        content = f.readlines()
        #-# Elimina los carácteres especiales como'\n' el final de cada línea
    content = [x.strip() for x in content]
    return content

def removeFiles(mainPath):
    global ignoreList

    contDir = 0
    contFile = 0

    for root, dirs, files in os.walk(mainPath):
        for adir in filter(lambda x: (x+'/') in ignoreList, dirs):
            completeRoot = os.path.join(root, adir)
            try:
                rmtree(completeRoot)
                contDir = contDir+1
                print(completeRoot+" || directorio borrado")
            except NameError as err:
                print("Fallo a la hora de resolver una función:\n",err)
            except:
                raise

        for file in filter(lambda x: x in ignoreList, files):
            completeRoot = os.path.join(root, file)
            try:
                os.remove(os.path.join(root, file))
                contFile = contFile+1
                print(completeRoot+" || fichero borrado")
            except NameError as err:
                print("Fallo a la hora de resolver una función:\n",err)
            except:
                raise
    print("***********************\nDirectorios borrados:"+str(contDir)+"\nFicheros borrados:"+str(contFile))

def main():
    #=# Check de uso correcto de argumentos
    if len(sys.argv) != 3:
        print("Método de uso: removeConfFiles.py <nombreFichero>.ignore dir/")
        return

    if not sys.argv[1].endswith('.ignore'):
        print("El nombre de fichero usado para el filtrado debe acabar en .ignore")
        return

    global ignoreList
    #=# Inicialización de lista a ignorar
    ignoreList = read_file_by_line(sys.argv[1])
    print ("-----------------------\nEliminación de los siguientes ficheros:\n-----------------------")
    environment = sys.argv[1].replace(".ignore","").replace("environmnets/","")
    print ("Bajo el entorno de "+environment+" se deben borrar los siguientes archivos:\n***********************")
    for ignore in ignoreList:
        print (ignore,)
    print ("-----------------------")

    removeFiles(sys.argv[2])
    

    
if __name__ == '__main__':
    main()