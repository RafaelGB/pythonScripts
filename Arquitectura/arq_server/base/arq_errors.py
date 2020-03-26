# define Python user-defined exceptions
class ArqError(Exception):
   """Base class for other exceptions"""
   def __init__(self, code):
        self.code = code

class ValueTooSmallError(ArqError):
   """Raised when the input value is too small"""
   pass

class ValueTooLargeError(ArqError):
   """Raised when the input value is too large"""
   pass