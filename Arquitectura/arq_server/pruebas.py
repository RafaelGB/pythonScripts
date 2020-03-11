import sys
sys.path.append('../')
import dependency_injector.containers as containers
import dependency_injector.providers as providers

class Engine:
    """Example engine base class.

    Engine is a heart of every car. Engine is a very common term and could be
    implemented in very different ways.
    """


class GasolineEngine(Engine):
    """Gasoline engine."""


class DieselEngine(Engine):
    """Diesel engine."""


class ElectricEngine(Engine):
    """Electric engine."""


class Car:
    """Example car."""

    def __init__(self, engine):
        """Initialize instance."""
        self._engine = engine  # Engine is injected

class Engines(containers.DeclarativeContainer):
    """IoC container of engine providers."""

    gasoline = providers.Factory(GasolineEngine)

    diesel = providers.Factory(DieselEngine)

    electric = providers.Factory(ElectricEngine)


class Cars(containers.DeclarativeContainer):
    """IoC container of car providers."""

    gasoline = providers.Factory(Car,
                                 engine=Engines.gasoline)

    diesel = providers.Factory(Car,
                               engine=Engines.diesel)

    electric = providers.Factory(Car,
                                 engine=Engines.electric)


if __name__ == '__main__':
    gasoline_car = Cars.gasoline()
    diesel_car = Cars.diesel()
    electric_car = Cars.electric()