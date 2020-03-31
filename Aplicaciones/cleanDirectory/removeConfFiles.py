import os
import sys
from shutil import rmtree
#own
from arq_decorators import ArqToolsTemplate
###################################################
#               VARIABLES GLOBALES
###################################################
ignoreList = []
###################################################
#                 IMPLEMENTACIÓN
###################################################
class CleanDirectoryTools(ArqToolsTemplate):
    def __init__(self, *args, **kwargs):
        className = self.__class__.__name__
        super().__init__(className, *args, **kwargs)
    
    def read_file_by_line(self,filePath):
        content = []
        with open(filePath) as f:
            content = f.readlines()
            #-# Elimina los carácteres especiales como'\n' el final de cada línea
        content = [x.strip() for x in content]
        return content

    def removeFiles(self,mainPath):
        global ignoreList
        contDir = 0
        contFile = 0
        for root, dirs, files in os.walk(mainPath):
            for adir in filter(lambda x: (x+'/') in ignoreList, dirs):
                completeRoot = os.path.join(root, adir)
                try:
                    rmtree(completeRoot)
                    contDir = contDir+1
                    self.logger.info("%s || directorio borrado", completeRoot)
                except NameError as err:
                    self.logger.error("Fallo a la hora de resolver una función:\n%s",err)
                except:
                    raise

            for file in filter(lambda x: x in ignoreList, files):
                completeRoot = os.path.join(root, file)
                try:
                    os.remove(os.path.join(root, file))
                    contFile = contFile+1
                    self.logger.info("%s || fichero borrado", completeRoot)
                except NameError as err:
                    self.logger.error("Fallo a la hora de resolver una función:\n%s",err)
                except:
                    raise
        self.logger.info("***********************\nDirectorios borrados: %d \nFicheros borrados: %d",contDir,contFile)

    def main(self):
        #=# Check de uso correcto de argumentos
        if len(sys.argv) != 3:
            self.logger.info("Método de uso: removeConfFiles.py <nombreFichero>.ignore dir/")
            return

        if not sys.argv[1].endswith('.ignore'):
            self.logger.info("El nombre de fichero usado para el filtrado debe acabar en .ignore")
            return

        global ignoreList
        #=# Inicialización de lista a ignorar
        ignoreList = self.read_file_by_line(sys.argv[1])
        self.logger.info ("-----------------------\nEliminación de los siguientes ficheros:\n-----------------------")
        environment = sys.argv[1].replace(".ignore","").replace("environmnets/","")
        self.logger.info ("Bajo el entorno de "+environment+" se deben borrar los siguientes archivos:\n***********************")
        printList = ""
        for ignore in ignoreList:
            
            printList = printList+ ignore+"\n"
        printList = printList+"-----------------------"
        self.logger.info(printList)
        self.removeFiles(sys.argv[2])
# Dado una ruta de fichero, devuelve una lista con su contenido por líneas

    

    
if __name__ == '__main__':
    cleanDirectoryTools = CleanDirectoryTools()
    cleanDirectoryTools.main()