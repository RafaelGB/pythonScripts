# communication
from flask import Flask, request
# Meta
from typing import Any
# Filesystem
from os import path
from pathlib import Path
import threading
from threading import Thread
import sys
import json
import logging
import signal
# Own
from arq_server.services.protocols.physical.Common import arqCache
from arq_server.services.CoreService import Configuration,ContextFilter
from arq_server.services.protocols.logical.NormalizeSelector import NormalizeSelector
from arq_server.services.protocols.physical.rest.MethodViews import ApplicationsApi , ArchitectureApi


class APIRestTools:
    server = Flask("arq_rest_server")
    __methodViewDict = {}

    # Services TIPS
    __logger: logging.Logger
    __config: Configuration
    __normalizer: NormalizeSelector

    def __init__(self, core, logical):
        self.__init_services(
            core.logger_service(),
            core.config_service(),
            logical
        )
        self.parent_path = Path(path.dirname(
            path.abspath(sys.modules['__main__'].__file__)))

        self.flask_conf_alias = self.__config.getProperty("groups", "flask")

        self.flask_conf = self.__config.getGroupOfProperties(
            self.flask_conf_alias,
            confKey=self.flask_conf_alias
        )

        self.__init_info_maps()
        self.__init_arq_url_rules()
        self.__logger.info("Herramientas de protocolo REST cargadas correctamente")
        # daemon=True,
        daemon = Thread(target=self.__start_server,kwargs={'loggerService':core.logger_service()})
        self.__logger.info("Protocolo REST lanzado en segundo plano")
        daemon.start()

    def stop_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def addUrlRule(self, URL: str, customMethodView=None, customFunc=lambda *args: None):
        """
        Añade un nuevo endpoint al servidor, el cual ejecutará la función que se determine.
        En caso de declarar un MethodView, se utilizará como salida del endpoint
        """
        self.__logger.debug("Añadiendo regla. URL:%s,  evento de llamada: %s",
                            URL, ("MethodView", "func")[customMethodView is None])
        if customMethodView is None:
            self.server.add_url_rule(URL,customFunc.__name__ ,customFunc)
        else:
            self.server.add_url_rule(
                URL,
                view_func=self.__selectMethod(customFunc).
                as_view(
                    customFunc,
                    customFunc
                )
            )

    """
    MÉTODOS PRIVADOS
    """
    def __start_server(self,*args,**kwargs):
        """
        Configuración y arranque del servidor Flask
        """
        self.server.normalizer=self.__normalizer
        self.server.logger=self.__logger
        self.server.config['JSON_AS_ASCII'] = False
        self.server.__dict__.update(kwargs)
        # Debug=True provoca error, ya que solo permite depurar bajo el hilo principal y no como daemon
        self.server.run(debug=False)

    def __selectMethod(self, alias):
        if alias in self.__methodViewDict:
            return self.__methodViewDict[alias]
        else:
            return None

    def __init_services(self, logger, config, logical):
        # Servicio de logging
        self.__logger = logger.arqLogger()
        self.__config = config
        self.__normalizer = logical.normalize_selector_service()
        serverLogger=logging.getLogger('werkzeug')
        serverLogger.addFilter(ContextFilter())
        arqCache.init_app(app=self.server, config={
                          "CACHE_TYPE": "filesystem", 'CACHE_DIR': Path('/tmp')})

    def __init_arq_url_rules(self):
        # Regla para filtrar según una condición la configuración de Flask
        def callback(elem): return elem.startswith("url.rule")
        # Recupera configuración utilizando el filtro
        url_rules_cfg_list = self.__config.getFilteredGroupOfProperties(
                                self.flask_conf_alias, 
                                callback,
                                confKey=self.flask_conf_alias
                            )
            
        for url_rule_cfg in url_rules_cfg_list:
            url_rule = self.flask_conf[url_rule_cfg]
            try:
                url_rule_info = url_rule.split(';')
                self.__logger.info(
                    "Regla URL: '%s' con alias '%s'", url_rule_info[0], url_rule_info[1])
                self.server.add_url_rule(
                    url_rule_info[0],
                    view_func=self.__selectMethod(url_rule_info[1]).
                    as_view(
                        url_rule_info[1],
                        url_rule_info[1]
                    )
                )
            except:
                self.__logger.error(
                    "Error añadiendo la regla de url '%s' al servidor", url_rule)

    def __init_info_maps(self):
        self.__methodViewDict['applications_api'] = ApplicationsApi
        self.__methodViewDict['architecture_api'] = ArchitectureApi
