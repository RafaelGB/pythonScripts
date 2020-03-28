import json
from pathlib import Path

# define Python user-defined exceptions
class ArqError(Exception):
   """Base class for other exceptions"""
   def __init__(self,message, code):
        super().__init__(message)
        self.code = code

   def code_message(self) -> str:
      if self.code in ArqErrorInfo:
         return ArqErrorInfo[self.code]
      return "##ERROR## Código de error no válido"


ArqErrorInfo = {
   101:{
      "message","Error de prueba: ¡algo malo ocurrió!"
   }
}