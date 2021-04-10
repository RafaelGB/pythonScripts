from arq_decorators import ArqToolsTemplate

class LogReader(ArqToolsTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)

if __name__ == '__main__':
    logReader = LogReader()
    logReader.logger.info("prueba")