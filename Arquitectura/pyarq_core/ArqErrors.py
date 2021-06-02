import traceback

class ArqErrorMock(Exception):
   pass
# define Python user-defined exceptions
class ArqError(Exception):
   """Base class for other exceptions"""
   def __init__(self,message,traceback=None):
        super().__init__(message)
        self.__customTraceback=traceback

   def normalize_exception(self)->dict:
      verboseException = {}
      verboseException['message']= self.message()
      if self.__customTraceback is None:
         verboseException['traceback']= ''.join(
            traceback.format_exception(
               etype=type(self), 
               value=self, 
               tb=self.__traceback__
               )
            )
      else:
         verboseException['traceback']=self.__customTraceback

      return verboseException

   def message(self) -> str:
      return str(self)


