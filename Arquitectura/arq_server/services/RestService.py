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
class FlaskFunctions:
    """TODO"""
    server = Flask(__name__)
    
    def __init__(self,core):
        self.parent_path = Path(path.dirname(path.abspath(sys.modules['__main__'].__file__)))
        self.__init_services(
            core.logger_service_provider(),
            core.config_service_provider()
            )
        
        self.local_conf_alias = self.config.getProperty("groups","flask")
        self.local_conf=self.config.getGroupOfProperties(self.local_conf_alias)
    def prueba(self):
        return "hola"
    def start_server(self):
        self.server.run(debug=True)

    def stop_server(self):
        func = request.environ.get(self.local_conf["shutdown"])
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        
    class InventoryItemApi(MethodView):
        """ /api/inventory/<item_name> """
        inventory = {
            "apple": {
                "description": "Crunchy and delicious",
                "qty": 30
            },
            "cherry": {
                "description": "Red and juicy",
                "qty": 500
            },
            "mango": {
                "description": "Red and juicy",
                "qty": 500
            }
        }

        error = {
            "itemNotFound": {
                "errorCode": "itemNotFound",
                "errorMessage": "Item not found"
            },
            "itemAlreadyExists": {
                "errorCode": "itemAlreadyExists",
                "errorMessage": "Could not create item. Item already exists"
            }
        }

        def get(self, item_name):
            """ Get an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            return make_response(jsonify(self.inventory[item_name]), 200)

        def post(self, item_name):
            """ Create an item """
            if self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemAlreadyExists"]), 400)
            body = request.get_json()
            self.inventory[item_name] = {"description": body.get("description", None), "qty": body.get("qty", None)}
            return make_response(jsonify(self.inventory[item_name]))

        def put(self, item_name):
            """ Update/replace an item """
            body = request.get_json()
            self.inventory[item_name] = {"description": body.get("description", None), "qty": body.get("qty", None)}
            return make_response(jsonify(self.inventory[item_name]))

        def patch(self, item_name):
            """ Update/modify an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            body = request.get_json()
            self.inventory[item_name].update({"description": body.get("description", None), "qty": body.get("qty", None)})
            return make_response(jsonify(self.inventory[item_name]))

        def delete(self, item_name):
            """ Delete an item """
            if not self.inventory.get(item_name, None):
                return make_response(jsonify(self.error["itemNotFound"]), 400)
            del self.inventory[item_name]
            return make_response(jsonify({}), 200)
    
    def __init_services(self, logger, config):
        # Servicio de logging
        self.logger = logger.arqLogger()
        self.config = config
    
    def __init_url_rules(self):
        url_rules_list = self.config.getGroupOfProperties(self.local_conf_alias,lambda elem :  elem.startswith("url.rule"))
        for url_rule in url_rules_list:
            try:
                url_rule_info = url_rule.split(';')
                self.server.add_url_rule(url_rule_info[0], view_func=self.InventoryItemApi.as_view(url_rule_info[1]))
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


    
