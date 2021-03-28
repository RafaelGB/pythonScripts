# Services
import logging
# Own
from arq_server.base.ArqErrors import ArqError
from arq_server.services.CoreService import Configuration

class NormalizeSelector:
    # Services TIPS
    __logger: logging.Logger
    __config: Configuration

    def __init__(self, core):
        self.__init_services(
            core.logger_service(),
            core.config_service()
        )
        self.__logger.info("NormalizeSelector - Servicios core inicializados correctamente")
        self.__avaliableServicesWithIntut={
            'configuration': self.__config
        }

        self.__logger.info("NormalizeSelector - lista de servicios que admiten instrucciones:"+str(self.__avaliableServicesWithIntut))
    
    def processInput(self,input:dict)->dict:
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
            context = input.pop('context')
            metadata = input.pop('metadata')
            if context == 'arq':
                output['response']=self.__arq_instructions(input.pop('service'),input)

        except ArqError as arqErr:
            self.__logger.exception("Error controlado: ",arqErr)
            output['error']=arqErr.code_message
            output['metadata']=metadata
        return output
    
    def __arq_instructions(self,service, input_instructions:dict):
        if service not in self.__avaliableServicesWithIntut:
            raise ArqError("Servicio de arquitectura no existe o no admite instrucciones",102)
        return self.__avaliableServicesWithIntut[service].read_input_instruccions(input_instructions)
    
    def __init_services(self, logger, config):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__config = config
        


