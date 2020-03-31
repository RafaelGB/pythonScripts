from flask import request, make_response, jsonify, current_app, session
from flask.views import MethodView
# Filesystem
from os import path, getenv
from pathlib import Path
import sys
import json

errors = {}
methods = {}

class ApplicationsApi(MethodView):
    """
    API RESTful interfaz para llamadas a las diferentes aplicaciones
    """

    global errors

    def __init__(self, view_name, *args, **kwargs):
        super(ApplicationsApi, self).__init__(*args, **kwargs)
        global methods
        self.logger = current_app.logger
        self.view_name = view_name
        self.apps = methods[self.view_name]["apps"]

    def get(self, app_name):
            """ app info """
            self.logger.info("View: '%s' - Peticion GET de la aplicación %s",self.view_name , app_name)
            if app_name in self.apps:
                return make_response(jsonify(self.apps[app_name]),200)
            else:
                return make_response(jsonify(errors['appNotFound']), 400)

    def post(self, app_name):
        """ run app """
        return make_response(jsonify(errors["methodNotSupported"]), 400)

    def put(self, app_name):
        """ substitute app info """
        return make_response(jsonify(errors["methodNotSupported"]), 400)

    def patch(self, app_name):
        """ substitute app info """
        return make_response(jsonify(errors["methodNotSupported"]), 400)

    def delete(self, app_name):
        """ delete app """
        return make_response(jsonify(errors["methodNotSupported"]), 400)


methodViewDict = {
    "applications_api": ApplicationsApi
}

"""
------------------
ISOLATED FUNCTIONS
------------------
"""
def init_update_methods_conf(file_path):
    global errors, methods
    if path.exists(file_path):
        with open(file_path, 'rt') as f:
            methodViews_dict = json.load(f)
            errors = methodViews_dict['errors']
            methods = methodViews_dict['methods']

def selectMethod(alias):
    if alias in methodViewDict:
        return methodViewDict[alias]
    else:
        return None
    