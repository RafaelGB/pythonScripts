# communication
from flask import Flask
from flask import jsonify
from flask import request, make_response
from flask.views import MethodView
# Filesystem
from os import path, getenv
from pathlib import Path
import sys
import json
# IoC
from dependency_injector import containers, providers
# own
from arq_server.services.CoreService import CoreService
from arq_server.services.protocols.MethodViews import selectMethod
class FlaskFunctions:
    """TODO"""
    server = Flask("mi_aplicacion")
    
    def __init__(self,core):
        self.__init_services(
            core.logger_service(),
            core.config_service()
            )
        self.logger.info("INI - arranque funcionalidades de Flask")
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        self.local_conf_alias = self.config.getProperty("groups","flask")
        self.local_conf=self.config.getGroupOfProperties(self.local_conf_alias)
        self.__init_url_rules()
        self.logger.info("FIN - arranque funcionalidades de Flask")
        
    def start_server(self):
        self.server.run(debug=False)

    def stop_server(self):
        func = request.environ.get(self.local_conf["shutdown"])
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    
    def __init_services(self, logger, config):
        # Servicio de logging
        self.logger = logger.arqLogger()
        self.config = config
    
    def __init_url_rules(self):
        callback = lambda elem :  elem.startswith("url.rule")
        url_rules_cfg_list = self.config.getFilteredGroupOfProperties(self.local_conf_alias, callback)
        for url_rule_cfg in url_rules_cfg_list:
            url_rule = self.local_conf[url_rule_cfg]
            try:
                url_rule_info = url_rule.split(';')
                self.logger.info("Regla URL: '%s' con alias '%s'",url_rule_info[0],url_rule_info[1])
                self.server.add_url_rule(url_rule_info[0], view_func=selectMethod(url_rule_info[1]).as_view(url_rule_info[1]))
            except:
                self.logger.error("Error añadiendo la regla de url '%s' al servidor",url_rule)
    
    def __init_info_maps(self):
        app_info_path = path.join(
            self.parent_path,
            self.config.getProperty("base","path.resources"),
            self.config.getProperty("applications","path.app.repository"),
            self.config.getProperty("applications","filename.app.info")
            )
        if path.exists(app_info_path):
            with open(app_info_path, 'rt') as f:
                self.app_info = json.load(f)


    
