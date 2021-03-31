# Services
import logging
from typing import List
# Own
from arq_server.base.ArqErrors import ArqError
from arq_server.services.CoreService import Configuration
from arq_server.services.support.SecurityTools import Security
class NormalizeSelector:
    # Services TIPS
    __logger: logging.Logger
    __config: Configuration
    __security: Security

    def __init__(self, core, cross):
        self.__init_services(
            core.logger_service(),
            core.config_service(),
            cross.security_tools()
        )
        self.__logger.info("NormalizeSelector - Servicios core inicializados correctamente")
        self.__avaliableServicesWithInput={
            'configuration': core.config_service(),
            'security': cross.security_tools()
        }

        self.__logger.info("NormalizeSelector - lista de servicios que admiten instrucciones:\n"+str(self.__avaliableServicesWithInput.keys()))
    
    def addAvaliableService(self,singletonService):
        # TODO
        pass

    def processInput(self,input:dict, headers:dict)->dict:
        """
        metadata:
        {
            'protocol' : '',
            'timeInit' : '',
            'user' : ''
        }
        """
        output = {}
        try:
            input = self.__validateInput(input) # Si la entrada no es correcta, salta excepción
            # Parametros de entrada
            context = input.pop('context')
            service = input.pop('service')
            metadata = input.pop('metadata')
            if service not in ['security']:
                filtered_headers=self.__validateheaders(headers) # Si faltan cabeceras, salta excepción
                self.__security.validate_token(filtered_headers['token']) # Valida token para los servicios protegidos
            self.__logger.info("Contexto: %s",context)
            if context == 'arq':
                output['response']=self.__arq_instructions(service,input)
            else:
                raise ArqError("contexto no válido", 101)
            
            output['metadata']=metadata
        except ArqError as arqErr:
            output['error']=arqErr.normalize_exception()
        return output
    
    def __arq_instructions(self,service, input_instructions:dict):
        if service not in self.__avaliableServicesWithInput:
            raise ArqError("Servicio de arquitectura no existe o no admite instrucciones",101)
        return self.__avaliableServicesWithInput[service].read_input_instruccions(input_instructions)
    
    def __validateInput(self,raw_input:dict)->dict:
        """
        Comprueba que el input fuente contiene las claves configuradas. Descarta excesos
        ---
        Devuelve el diccionario de entrada filtrado
        """
        avaliableKeys= self.__config.getProperty('logical','avaliableInputKeys').split(',')
        try:
            filtered_input =  { av_key: raw_input[av_key] for av_key in avaliableKeys }
            if (not isinstance(filtered_input['args'],List)) or (not isinstance(filtered_input['kwargs'],List)):
                raise ArqError("Los argumentos no traen el formato correcto",101)
            self.__logger.info("La entrada es válida")
            return filtered_input
        except ArqError as arqe:
            raise arqe
        except Exception as e:
            raise ArqError("La entrada no cumple los requisitos, revisar:"+str(e), 101)
    
    def __validateheaders(self,raw_headers):
        """
        Comprueba que las cabeceras contiene las claves configuradas. Descarta excesos
        ---
        Devuelve el diccionario de cabeceras filtrado
        """
        avaliableHeaders = self.__config.getProperty('logical','avaliableHeaders').split(',')
        try:
            filtered_headers =  { av_key: raw_headers[av_key] for av_key in avaliableHeaders }
            return filtered_headers
        except ArqError as arqe:
            raise arqe
        except Exception as e:
            raise ArqError("Faltan cabeceras, revisar:"+str(e), 101)
        
    def __init_services(self, logger, config, security):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__config = config
        self.__security = security
        


