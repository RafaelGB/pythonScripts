import json
from pathlib import Path

class ArqErrorMock(Exception):
   pass
# define Python user-defined exceptions
class ArqError(Exception):
   """Base class for other exceptions"""
   def __init__(self,message, code):
        super().__init__(message)
        self.code:int = code

   def code_message(self) -> str:
      if self.code in ArqErrorInfo:
         return str(ArqErrorInfo[self.code])
      return "##ERROR## Código de error no válido"


ArqErrorInfo = {
   101:{
      "esp","Error no controlado: ¡algo malo ocurrió!"
   },
   # Errores relacionados con ficheros
   201:{
      "esp","Credenciales no encontradas"
   }
}