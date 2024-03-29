from copy import deepcopy

class baseConst(object):
    # config keys
    ARQ_CONF_KEY = "arq"
    DOCKER_CONF_KEY = "docker"
    # resources
    RESOURCE_CREDENTIALS = "credentials"
    
    # Inmutable Logic
    def __setattr__(self, name, value):
        """Solo permite instanciar una vez"""
        if name in self.__dict__:
            return deepcopy(self.__dict__[name])
        self.__dict__[name] = value

    def __getattr__(self, name, value):
        if name in self.__dict__:
            return deepcopy(self.__dict__[name])

    def __delattr__(self, item):
        """No permite borrar atributos"""
        if item in self.__dict__:
            pass

class Const(baseConst):
    def __setattr__(self, name, value):
        """No permite instanciar nada nuevo"""
        if name in self.__dict__:
            pass
