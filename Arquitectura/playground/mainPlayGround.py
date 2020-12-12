from functools import wraps

def enableFunction(isEnabled:bool=True):
    # Complete function
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            function(*args, **kwargs)
        return wrapper
    # Empty function
    def empty_func(*args,**kargs):
        print("Funcion '{0}' desactivada. Active en configuración el módulo utilizado".format(func.__name__))
    # If is enabled, returns complete func, otherwise an empty one
    if isEnabled:
        return inner_function
    else:
        return empty_func


@enableFunction(False)
def main():
    print("hello world")

if __name__ == "__main__":
    main()