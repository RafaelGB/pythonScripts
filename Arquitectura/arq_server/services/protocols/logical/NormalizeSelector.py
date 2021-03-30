# Services
import logging
from typing import List
# Own
from arq_server.base.ArqErrors import ArqError
from arq_server.services.CoreService import Configuration

class NormalizeSelector:
    # Services TIPS
    __logger: logging.Logger
    __config: Configuration

    def __init__(self, core,cross):
        self.__init_services(
            core.logger_service(),
            core.config_service()
        )
        self.__logger.info("NormalizeSelector - Servicios core inicializados correctamente")
        self.__avaliableServicesWithIntut={
            'configuration': core.config_service(),
            'security': cross.security_tools()
        }

        self.__logger.info("NormalizeSelector - lista de servicios que admiten instrucciones:"+str(self.__avaliableServicesWithIntut))
    
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
            input = self.__validateInput(input)
            context = input.pop('context')
            metadata = input.pop('metadata')
            if context == 'arq':
                output['response']=self.__arq_instructions(input.pop('service'),input)
            else:
                raise ArqError("contexto no válido", 101)
            
            output['metadata']=metadata

        except ArqError as arqErr:
            output['error']=arqErr.normalize_exception()
        return output
    
    def __arq_instructions(self,service, input_instructions:dict):
        if service not in self.__avaliableServicesWithIntut:
            raise ArqError("Servicio de arquitectura no existe o no admite instrucciones",102)
        return self.__avaliableServicesWithIntut[service].read_input_instruccions(input_instructions)
    
    def __validateInput(self,raw_input:dict)->dict:
        """
        Comprueba que el input fuente contiene las claves configuradas. Descarta excesos
        """
        avaliableKeys= self.__config.getProperty('logical','avaliableKeys').split(',')
        try:
            filtered_input =  { av_key: raw_input[av_key] for av_key in avaliableKeys }
            if (not isinstance(filtered_input['args'],List)) or (not isinstance(filtered_input['args'],List)):
                raise ArqError("Los argumentos no traen el formato correcto",101)
            return filtered_input
        except ArqError as arqe:
            raise arqe
        except Exception as e:
            raise ArqError("La entrada no cumple los requisitos, revisar", 101)



    def __init_services(self, logger, config):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__config = config
        


