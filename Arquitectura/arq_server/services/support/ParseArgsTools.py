# system
import argparse
import logging
# IoC
from arq_server.services.CoreService import Configuration

class ParseArgsTools(object):
    logger: logging.getLogger()
    config: Configuration
    
    parser = argparse.ArgumentParser()

    def __init__(self, core, *args, **kwargs):
        self.__init_services(core)
        self.logger.info("Herramientas para tratar argumentos de entrada tratados correctamente")
    
    def add_argument(self):
        self.parser.add_argument('--foo', help='foo of the %(prog)s program')
    
    def show_help(self):
        self.parser.print_help()
        
    def __init_services(self, core) -> None:
        # Servicio de logging
        self.logger = core.logger_service().arqLogger()
        self.config = core.config_service()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', help='foo help')
    args = parser.parse_args()
    print(args)