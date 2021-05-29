# Librerias nativas
import types

# filesystem
from functools import wraps
import logging

# own
from arq_server.base.ArqErrors import ArqError, ArqErrorMock

deco_logger = logging.getLogger()
def method_wrapper(function):
    code_error = 101
    error_type = ArqErrorMock

    @wraps(function)
    def wrapper(*args, **kwargs):
        error_type=None
        if 'error_type' in kwargs:
            error_type = kwargs['error_type']
        try:
            result = function(*args, **kwargs)
        except error_type as own_e:
            raise ArqError(own_e)
        except Exception as e:
            raise e
        return result
    return wrapper

class ServiceBase(object):
    def __getattribute__(self, attr):
        try:
            attr_val = super().__getattribute__(attr)
            if type(attr_val) == types.MethodType:
                w_attr = method_wrapper(attr_val)
                return w_attr
            else:
                return attr_val
        except:
            raise AttributeError(attr)

def enableFunction(isEnabled:bool=True,className="not defined"):
    '''
    Decorator to active/deactivate functions
    '''
    global deco_logger
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        return wrapper
    # Empty function
    def empty_func(function,*args,**kargs):
        deco_logger.warn("Clase:'%s' - Funcion '%s' deshabilitada",className,function.__name__)
        # En caso de usarse la función como runnable, se invoca una lambda vacía
        return lambda *_, **__: None
    # If is enabled, returns complete func, otherwise an empty one
    if isEnabled:
        return inner_function
    else:
        return empty_func