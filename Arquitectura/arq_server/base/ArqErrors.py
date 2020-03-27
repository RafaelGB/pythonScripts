import json
from pathlib import Path

# define Python user-defined exceptions
class ArqError(Exception):
   """Base class for other exceptions"""
   def __init__(self, code):
        self.code = code

   def message(self) -> str:
      if self.code in ArqErrorInfo:
         return ArqErrorInfo[self.code]
      return "##ERROR## Código de error de válido"

class ValueTooSmallError(ArqError):
   """Raised when the input value is too small"""
   pass

class ValueTooLargeError(ArqError):
   """Raised when the input value is too large"""
   pass

ArqErrorInfo = {
   222:{
      "message","¡algo malo ocurrió!"
      }
}