# Dependency
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration as di_Configuration
# System
import sys
import os
# own
from arq_decorators.arq_decorator import ArqToolsTemplate, Base

class TestingArq(ArqToolsTemplate,Base):
    # declaro servicios propios del decorador para evitar que el lint indique error
    def __init__(self, *args, **kwargs):
        super().__init__(self.__class__.__name__, *args, **kwargs)
        self.expose_app(self)

if __name__ == "__main__":
    arq = TestingArq()
    arq.logger.info("hola")
