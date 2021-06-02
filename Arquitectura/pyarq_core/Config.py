# Basic
import configparser
import logging
from cachetools import cached, TTLCache
from typing import Any, Dict

# Filesystem
import json
#own
from .Base import Base, request
from .ArqErrors import ArqError
from .Constants import Const

class Configuration(Base):
    """
    CONFIGURACION
    -------------
    Servicio para ofrecer configuración centralizada al resto de servicios y aplicaciones
    """
    __const:Const
    __logger:logging.Logger
    __allModulesConfDict : Dict
    def __init__(self,logger,const,configuration_config):
        self.__init_services(logger,const)
        self.__logger.info("INI - servicio de Configuración")
        try:
            self.__init_conf(configuration_config['github'])
        except Exception as ex:
            raise ArqError("Error: no se han definido las credenciales para recuperar la configuración")
        self.__logger.info("FIN - servicio de Configuración")
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getProperty(self, group, key, parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave ( usando cache )
        """
        if group in self.__allModulesConfDict[confKey]:
            if key in self.__allModulesConfDict[confKey][group]:
                try:
                    return parseType(self.__allModulesConfDict[confKey][group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warning("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warning("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyVerbose(self, group, key, parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave ( sin usar cache )
        """
        if group in self.__allModulesConfDict[confKey]:
            if key in self.__allModulesConfDict[confKey][group]:
                try:
                    return parseType(self.__allModulesConfDict[confKey][group][key])
                except:
                    self.__logger.error("La propiedad '%s' en el grupo '%s' no acepta el tipo impuesto '%s'. Devuelve 'None'",key, group, parseType)
                    return None
            else:
                self.__logger.warn("La propiedad '%s' no está definida en el grupo '%s' en configuración",key, group)
                return None
        else:
            self.__logger.warn("El grupo '%s' no está definido en configuración", group)
            return None

    def getPropertyDefault(self, group, key, defaultValue:Any,parseType=str,confKey="arq", **kwargs) -> Any:
        """
        Obtener propiedad en función del grupo y la clave.
        En caso de no existir, define un valor por defecto
        """
        propertyValue = self.getProperty(group,key,parseType=parseType,confKey=confKey)
        return (propertyValue, defaultValue)[propertyValue == None]
    
    def getGroupOfProperties(self,group_name,confKey="arq", **kwargs):
        """
        Devuelve un grupo de propiedades.
        En caso de no existir devuelve 'None'
        """
        if group_name in self.__allModulesConfDict[confKey]:
            return self.__allModulesConfDict[confKey][group_name]
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def getFilteredGroupOfProperties(self, group_name, callback,confKey="arq", **kwargs):
        """
        Devuelve un grupo de propiedades filtradas en función de la condición impuesta por parámetro
        """
        if group_name in self.__allModulesConfDict[confKey]:
            return self.__filterTheDict(self.__allModulesConfDict[confKey][group_name], callback)
        else:
            self.__logger.error("El grupo '%s' no está definido en configuración", group_name)
            return None

    def __init_services(self,logger,const):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__const = const
    
    def __init_conf(self,credentialsPath):
        """
        Dado un fichero de credenciales, recupera configuración de un repositorio git
        """
        self.__allModulesConfDict = self.__getConfFromGit(credentialsPath)

    def __getConfFromGit(self,credentials) -> dict:
        """
        Recupera configuración de un repositorio git
        """ 
        self.__logger.info("Obteniendo configuracion con perfil %s en git",credentials['profile'])
        confDict={}
        content= credentials['content_url']+credentials['profile']
        filelist=request(content,headers={'Authorization':'Token '+credentials['config_token']})
        for hit in json.loads(filelist.text):
            self.__logger.info("Fichero '%s' obtenido",hit["name"])
            funcConf=configparser.ConfigParser()
            urlFile=self.__generate_git_file_url(
                credentials['user'],
                credentials['repo'],
                credentials['branch'],
                hit['path'])
            response=request(urlFile,headers={'Authorization':'Token '+credentials['config_token']})
            funcConf.read_string(response.text)
            confDict[hit["name"][:hit["name"].index(".")]]=funcConf
        return confDict
    
    def __generate_git_file_url(self,user,repo,branch,path):
        separator='/'
        url="https://raw.githubusercontent.com"
        url = url+separator+user
        url = url+separator+repo
        url = url+separator+branch
        url = url+separator+path
        return url
        
    def __filterTheDict(self, dictObj, callback):
        newDict = dict()
        # Itera sobnrte todos los elementos del diccionario
        for (key, value) in dictObj.items():
            # Comprueba si satisface la condición del parámetro para añadir al diccionario
            if callback(key):
                newDict[key] = value
        return newDict